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

"""User interface."""

import pygame

class UserInterface:
    """The user interface."""

    screen = False
    network = False

    def __init__(self,network):
        self.network = network

        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))

    def do(self):
        self.screen.fill((255,255,255))

        # Display the network
        for track in self.network.tracks:
            for x,y in (track.a.pos,track.b.pos):
                pygame.draw.circle(self.screen,(0,0,0),(x + 1,y + 1),2)
            pygame.draw.line(self.screen,(0,0,0),track.a.pos,track.b.pos)

        pygame.display.flip()
