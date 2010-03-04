# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Trains - train network thingy
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

"""Train class and related logic."""

import sys

from Congestion.world import world,Node,Rail

from collections import deque
import random

cdef class Train:
    cdef public float v # current velocity, m/s
    
    # Current accelleration, m/s^2 
    cdef public float a

    # Current buffer zone, m
    cdef public float b

    # intrinsic characteristics
    cdef public float l # length, m

    # Limits on acelleration and braking
    cdef public float max_driving_accelleration # m/s^2
    cdef public float max_driving_jerk # m/s^3
    cdef public float max_braking_accelleration # m/s^2
    cdef public float max_braking_jerk # m/s^3

    # Minimum distance from next train
    cdef public float buffer_min_distance

    # What Nodes or Tracks we are occupying
    cdef public occupying

    def __init__(self,location,**kwargs):
        defaults = {'v':0.0,
                    'a':0.0,
                    'l':5.0,
                    'max_driving_accelleration':1.0,
                    'max_driving_jerk':10.0,
                    'max_braking_accelleration':-5.0,
                    'max_braking_jerk':-5.0,
                    'buffer_min_distance':5}
        defaults.update(kwargs) 
        for k,v in defaults.iteritems():
            setattr(self,k,v)

        self.b = self.buffer_min_distance

        # add ourselves to the beginning of the rail
        self.occupying = deque((location,))
        location.add_train(self,0)

    cdef braking_distance(self,v0):
        """Calculate braking distance for a given starting velocity"""
        r = (v0*v0)/(-self.max_braking_accelleration)

        # add extra distance to account for the braking jerk 
        # FIXME

        # add minimum distance from next train
        r += self.buffer_min_distance
        return r

    cpdef do_plan(self,float dt):
        # The buffer zone is to provide sufficient space to stop the train via
        # the action of the brakes, at maximum force, before velocity limiting
        # obstacles ahead, taking into account the current velocity,
        # acelleration, and limits on jerk.

        # Find the minimum speed limit
        speed_limit = 1000000.0
        for r,n,rn in zip(self.occupying,list(self.occupying)[1:] + [None],list(self.occupying)[2:] + [None,None]):
            if isinstance(r,Rail):
                speed_limit = min(r.speed_limit,speed_limit) 
                if n is not None:
                    pass

        # Determine the upper limit on how much additional buffer zone we would
        # like to have.
        #
        # This is done by finding new velocity we would have, if we applied maximum accelleration available
        new_v = min(speed_limit,(self.v + (dt * (self.a + (dt * self.max_driving_jerk)))))
        new_bd = self.braking_distance(new_v) + new_v*dt
        db = new_bd - self.b
        # 
        db = max(0,db)

        # Is there an obstacle in our path, were the buffer zone to be extended by db?
        #
        # Essentially, while there is still db to use up, attempt to allocate
        # additional buffer. This has to be done iteratively, as we may have a
        # velocity high enough that we clear whole rail segments in one dt.
        while db > 0.01: 
            head_rail = self.occupying[-1]
            head_pos = head_rail.find_train(self)
            cur_end_pos = head_pos + self.l + self.b
            find_next_rail = False
            trial_end_pos = None
            if head_rail.length > cur_end_pos + db:
                trial_end_pos = cur_end_pos + db
            else:
                find_next_rail = True
                trial_end_pos = head_rail.length + 0.00001

            # Allocate the part of db that extends up-to and including the end
            # of the head rail.
            r = head_rail.occupying(cur_end_pos,trial_end_pos,self)
            if r is not None:
                p,t = r
                # We can extend the buffer up to where the obstructing train starts.
                assert p + 1 > cur_end_pos
                self.b += p - cur_end_pos
                assert self.b > 0
                db -= p - cur_end_pos
                break
            else:
                # Success!
                self.b += trial_end_pos - cur_end_pos
                assert self.b > 0
                db -= trial_end_pos - cur_end_pos
               
                # Have we reached the end of the rail?
                if not find_next_rail: 
                    break
                else:
                    # Find where to go next
                    if head_rail.b.occupying is not None:
                        break
                    else:
                        # Pick a random exit that is empty
                        exits = list(head_rail.b.exits)
                        random.shuffle(exits)
                        blocked = True
                        for next_rail in exits:
                            if next_rail.find_train(self) is None and \
                               next_rail.ok_to_enter() and \
                               next_rail.add_train(self,0):

                                # Found an empty exit rail
                                head_rail.b.occupying = self
                                self.occupying.append(head_rail.b)
                                self.occupying.append(next_rail)
                                blocked = False
                                break
                            else:
                                pass
                        if blocked:
                            break

        if db > 0.01:
            # If there is any db left, we ran into an obstacle, so start applying the brakes
            #self.a += self.max_braking_jerk * dt
            #self.a = max(self.max_braking_accelleration,self.a)
            self.a = self.max_braking_accelleration
        else:
            # Otherwise keep accellerating, up to the speed limit
            self.a += self.max_driving_jerk * dt
            self.a = min(self.max_driving_accelleration,self.a)
            self.a = min((speed_limit - self.v) * dt,self.a)

    cpdef do_move(self,float dt):
        dp = self.v * dt
        dp = min(dp,self.b)
        self.b -= dp
        assert self.b + 1 > self.buffer_min_distance
        self.b = max(self.b,self.buffer_min_distance)

        # Update positions
        rails_left = 0
        for rail in self.occupying:
            if isinstance(rail,Rail):
                if rail.move_train(self,dp):
                    rails_left += 1 
        for i in range(rails_left):
            assert isinstance(self.occupying[1],Node)
            assert self.occupying[1].occupying is self
            self.occupying[1].occupying = None
            self.occupying.popleft()
            self.occupying.popleft()

        self.v += self.a * dt
        self.v = max(0,self.v)
