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

class Train:
    speed = False
    length = False

    # What sections of track we are currently occupying
    occupying = False 

    # How far along we are on that track
    travelled = 0

    def __init__(self,location,speed=15.0,length=10):
        self.speed = speed
        self.length = length

        self.occupying = [location]
        location.present.append(self)

    def do(self,delta_t):
        # Move us along
        self.travelled += delta_t * self.speed

        # Have we reached the end of the current track segment?
        if (self.travelled > self.occupying[0].length):
            # Where else can we go?
            next_tracks = self.occupying[0].b.exits
            if len(next_tracks):
                next = next_tracks[randrange(0,len(next_tracks))]
            else:
                 # uh-oh, no exit, magically go to the start of this track
                 next = self.occupying[0]
            
            # take us off the track we just left
            exited_track = self.occupying.pop()
            exited_track.present.remove(self)

            # put us onto the next track
            self.occupying.insert(0,next)
            next.present.append(self)

            # reset the distance travelled
            self.travelled = 0
