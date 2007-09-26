# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# ### BOILERPLATE ###
# Trains - train network thingy
# Copyright (C) 2007 Peter Todd <pete@petertodd.org>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ### BOILERPLATE ###

"""Train class and related logic."""

from random import randrange

from pathfinding import pathfind

class Train:
    speed = False
    length = False

    # What sections of track we are currently occupying
    occupying = False 

    # How far along we are on that track
    travelled = None 

    waiting_for = None
    waiting_for_delta_t = None

    def __init__(self,net,location,speed=15.0,length=10):
        self.speed = speed
        self.length = length
        self.net = net

        self.occupying = [location]
        location.present.append(self)

        # Randomize starting position on the track
        self.travelled = randrange(0,location.length)

        self.target = self.net.nodes[0]

    def do(self,delta_t):
        # Have we reached the end of the current track segment?
        if (self.travelled <= self.occupying[0].length):
            # Nope, keep moving.
            self.travelled += delta_t * self.speed
        else:
            if self.waiting_for:
                # Waiting for track ahead to clear.
                if not len(self.waiting_for.present) or \
                    ((self.waiting_for.present[0].travelled > self.waiting_for.present[0].length + self.length) \
                     and (self.waiting_for.waiting_to_enter[0] == self)):

                    # aren't waiting anymore
                    self.waiting_for.waiting_to_enter.remove(self)

                    # take us off the track we just left
                    exited_track = self.occupying.pop()
                    exited_track.present.pop()

                    # put us onto the next track
                    self.occupying.insert(0,self.waiting_for)
                    self.waiting_for.present.insert(0,self)

                    # Waiting_for_time is the total time we've been waiting. The 
                    # pathfinder code operates on distances. So logically, how far 
                    # could we have gone in that time? While we're at it, do a 
                    # quick, crude average as well.
                    self.waiting_for.traffic = (self.waiting_for.traffic + self.waiting_for_time * self.speed) / 2

                    self.travelled = 0
                    self.waiting_for = None
                else:
                    # Still waiting, make note of the congestion for the pathfinder.
                    self.waiting_for_time += delta_t 
            else:
                # Where should we go next? 
              
                # Reached our target?
                if self.occupying[0].b == self.target:
                    if self.target == self.net.nodes[0]:
                        self.target = self.net.nodes[1]
                    else:
                        self.target = self.net.nodes[0]

                # Pathfind to target.
                self.waiting_for = pathfind(self.net,self.occupying[0].b,self.target)
                self.waiting_for.waiting_to_enter.append(self)
                self.waiting_for_time = 0
