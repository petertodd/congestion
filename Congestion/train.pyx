# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Trains - train network thingy
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

"""Train class and related logic."""

from Congestion.world import world,Node,Rail

from collections import deque
import random

cdef class Train:
    cdef public float v # current velocity, m/s
    cdef public float b # current buffer distance, m
    
    # Current applied force, either braking or acelleration, newtons. Does not
    # include air resistance.
    cdef public float f

    # intrinsic characteristics
    cdef public float l # length, m
    cdef public float m # mass, kg
    cdef public float max_driving_force # max driving force, newtons
    cdef public float max_braking_force # max braking force, newtons
    cdef public float cd # drag coefficient, unitless, Fd = v^2 * cd

    # Safety margin for the buffer, multiplier
    cdef public float buffer_safety_margin

    # Minimum distance from next train
    cdef public float buffer_min_distance

    cdef public occupying

    def __init__(self,location,**kwargs):
        defaults = {'v':0.0,
                    'b':0.0,
                    'f':0.0,
                    'l':15.0,
                    'm':100.0,
                    'max_driving_force':10000.0,
                    'max_braking_force':-50000.0,
                    'cd':-0.1,
                    'buffer_safety_margin':1.1,
                    'buffer_min_distance':5}
        defaults.update(kwargs) 
        for k,v in defaults.iteritems():
            setattr(self,k,v)

        # add ourselves to the beginning of the rail
        self.occupying = deque((location,))
        location.add_train(self,0)

        self.m = self.m * (random.random() + 0.5)
        self.l = self.l * (random.random() + 0.5)
        self.cd = self.cd * (random.random() + 0.5)
        self.max_driving_force = self.max_driving_force * (random.random() + 0.5)
        self.max_braking_force = self.max_driving_force * -5

    cpdef do_extend_buffers(self,float dt):
        # The buffer zone is to provide sufficient space to stop the train via
        # the action of the brakes, at maximum force, at the current velocity.
        # Since dt has elapsed, first calculate the total force on the train,
        # the sum of acelleration/braking and drag force, and find the current
        # velocity.
        tf = (self.v*self.v * self.cd) # drag 
        tf += self.f # current applied force due to accelleration/braking
        self.v += (tf / self.m) * dt
        self.v = max(0,self.v) # velocity must always be positive

        # keep velocity low enough to avoid doing weird stuff
        self.v = min(2.5/dt,self.v)

        # Calculate the stopping distance at our current velocity
        stopping_distance = (self.v*self.v*self.m) / -self.max_braking_force
        stopping_distance *= self.buffer_safety_margin
        stopping_distance = max(self.buffer_min_distance,stopping_distance)

        #print 'tf',tf,'f',self.f,'v',self.v,'m',self.m,'b',self.b,'stopping_distance',stopping_distance

        if self.b > stopping_distance:
            # reducing the stopping distance is too complex, as we would then
            # have to potentially deoccupy rails, so just don't do it
            pass
        else:
            # Attempt to reserve the extra buffer needed
            head_rail = self.occupying[-1]
            end_pos = head_rail.find_train(self) + self.l
            if end_pos + stopping_distance >= head_rail.length:
                # We've reached the end of the rail, find where to go next
                if head_rail.b.occupying is None:
                    # Pick a random exit that is empty
                    exits = list(head_rail.b.exits)
                    random.shuffle(exits)
                    for next_rail in exits:
                        if next_rail.find_train(self) is None and \
                           next_rail.ok_to_enter() and \
                           next_rail.add_train(self,(end_pos + stopping_distance) - head_rail.length):
                            # Found an empty exit rail
                            head_rail.b.occupying = self
                            self.occupying.append(head_rail.b)
                            self.occupying.append(next_rail)
                            self.b = stopping_distance
                            break
                        else:
                            #print self,'blocked at',next_rail
                            pass
            else:
                # If the rail is not occupied at the new stopping distance
                # endpoint, we can set the buffer space to the new stopping
                # distance. Otherwise the buffer stays the same.
                occupied_by = head_rail.occupied(end_pos + stopping_distance)
                if occupied_by is None or occupied_by is self:
                    self.b = stopping_distance
                else:
                    #print 'head rail for train',self,'occupied by',head_rail.occupied(end_pos + stopping_distance),'at',end_pos,stopping_distance,'self.pos',head_rail.find_train(self),'head_rail',head_rail
                    #print head_rail.trains
                    pass

        if self.b < stopping_distance:
            # Note how if there was no safety margin we wouldn't actually stop in time 
            self.f = self.max_braking_force
        else:
            # FIXME: add in jerk, shouldn't apply accelleration suddenly
            self.f = self.max_driving_force

    cpdef do_move(self,float dt):
        dp = self.v * dt

        # Since we have moved forward, our buffer has to be decreased by the same amount.
        self.b -= dp

        # Update positions
        left_rail = False 
        print self.occupying
        for rail in self.occupying:
            if isinstance(rail,Rail):
                if rail.move_train(self,dp):
                    assert left_rail is False
                    left_rail = True
        if left_rail:
            print self.occupying
            assert isinstance(self.occupying[1],Node)
            assert self.occupying[1].occupying is self
            self.occupying[1].occupying = None
            self.occupying.popleft()
            self.occupying.popleft()
            print self.occupying
            left_rail -= 1
