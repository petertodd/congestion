# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Trains - train network thingy
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

"""Train class and related logic."""

import Trains.Simulator.network

from collections import deque
import random

class Train:
    v = 0.0 # current velocity, m/s
    b = 0.0 # current buffer distance, m
    
    # Current applied force, either braking or acelleration, newtons. Does not
    # include air resistance.
    f = 0.0 

    # intrinsic characteristics
    l = 40.0 # length, m
    m = 100.0 # mass, kg
    max_driving_force = 500.0 # max driving force, newtons
    max_braking_force = -1000.0 # max braking force, newtons
    cd = -0.1 # drag coefficient, unitless, Fd = v^2 * cd

    # Safety margin for the buffer, multiplier
    buffer_safety_margin = 1.1

    def __init__(self,net,location,**kwargs):
        self.net = net

        # add ourselves to the beginning of the track
        self.occupying = deque((location,))
        location.add_train(self,0)

        self.max_driving_force *= random.random() + 0.5
        self.max_braking_force = self.max_driving_force * -3

    def do_extend_buffers(self,dt):
        # The buffer zone is to provide sufficient space to stop the train via
        # the action of the brakes, at maximum force, at the current velocity.
        # Since dt has elapsed, first calculate the total force on the train,
        # the sum of acelleration/braking and drag force, and find the current
        # velocity.
        tf = (self.v*self.v * self.cd) # drag 
        tf += self.f # current applied force due to accelleration/braking
        self.v += (tf / self.m) * dt
        self.v = max(0,self.v) # velocity must always be positive

        # Calculate the stopping distance at our current velocity
        stopping_distance = (self.v*self.v*self.m) / -self.max_braking_force
        stopping_distance *= self.buffer_safety_margin
        stopping_distance = max(0,stopping_distance)

        print 'tf',tf,'f',self.f,'v',self.v,'m',self.m,'b',self.b,'stopping_distance',stopping_distance

        if self.b > stopping_distance:
            # reducing the stopping distance is too complex, as we would then
            # have to potentially deoccupy tracks, so just don't do it
            pass
        else:
            # Attempt to reserve the extra buffer needed
            head_track = self.occupying[-1]
            end_pos = head_track.find_train(self) + self.l
            if end_pos + stopping_distance >= head_track.length():
                # We've reached the end of the track, find where to go next
                if head_track.b.occupying is None:
                    # Pick a random exit that is empty
                    exits = list(head_track.b.exits)
                    random.shuffle(exits)
                    print self,'exits',exits
                    for next_track in exits:
                        if next_track.add_train(self,(end_pos + stopping_distance) - head_track.length()):
                            # Found an empty exit track
                            head_track.b.occupying = self
                            self.occupying.append(head_track.b)
                            self.occupying.append(next_track)
                            self.b = stopping_distance
                            print 'found empty track',head_track.b,next_track
                            break
                        else:
                            print self,'blocked at',next_track
            else:
                # If the track is not occupied at the new stopping distance
                # endpoint, we can set the buffer space to the new stopping
                # distance. Otherwise the buffer stays the same.
                occupied_by = head_track.occupied(end_pos + stopping_distance)
                if occupied_by is None or occupied_by is self:
                    self.b = stopping_distance
                else:
                    print 'head track for train',self,'occupied by',head_track.occupied(end_pos + stopping_distance),'at',end_pos,stopping_distance,'self.pos',head_track.find_train(self),'head_track',head_track
                    print head_track.trains

        if self.b < stopping_distance:
            # Note how if there was no safety margin we wouldn't actually stop in time 
            self.f = self.max_braking_force
        else:
            # FIXME: add in jerk, shouldn't apply accelleration suddenly
            self.f = self.max_driving_force

    def do_move(self,dt):
        dp = self.v * dt

        # Since we have moved forward, our buffer has to be decreased by the same amount.
        self.b -= dp

        # Update positions
        left_track = False
        for track in self.occupying:
            if isinstance(track,Trains.Simulator.network.Track):
                if track.move_train(self,dp):
                    assert not left_track
                    left_track = True
        if left_track:
            print self.occupying
            assert isinstance(self.occupying[1],Trains.Simulator.network.Node)
            assert self.occupying[1].occupying is self
            self.occupying[1].occupying = None
            self.occupying.popleft()
            self.occupying.popleft()
            print self.occupying
