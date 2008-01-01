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

def ip(pos):
    x,y = pos
    return (int(x),int(y))

class UserInterface:
    """The user interface."""

    screen = False
    network = False

    def __init__(self,network,screen_size):
        self.network = network

        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)

    def do(self):
        self.screen.fill((255,255,255))

        # Display the network
        for track in self.network.tracks:
            for n in (track.a,track.b):
                x,y = n.pos
                c = (0,0,0)
                size = 2
                if n == self.network.nodes[0]:
                    c = (255,255,0)
                    size = 4
                if n == self.network.nodes[1]:
                    c = (0,255,0)
                    size = 4
                if n == self.network.nodes[2]:
                    c = (0,255,255)
                    size = 4
                pygame.draw.circle(self.screen,c,ip((x + 1,y + 1)),size)
            pygame.draw.aaline(self.screen,(0,0,min(track.traffic,255)),ip(track.a.pos),ip(track.b.pos))

        # Draw the trains
        for t in self.network.trains:
            # Calculate what fraction of the total length the train has travelled.
            f = t.travelled / t.occupying[0].length()

            # Determine where on the line segment to draw the dot.
            a = t.occupying[0].a.pos
            b = t.occupying[0].b.pos
            dx = b[0] - a[0]
            dy = b[1] - a[1]

            x = int(a[0] + (dx * f))
            y = int(a[1] + (dy * f))

            pygame.draw.circle(self.screen,(255,0,0),(x + 1,y + 1),2)

        # where the mouse is, equivilent to node id
        pos = pygame.mouse.get_pos()
        pygame.event.clear()

        font = pygame.font.Font(None, 12)
        text = font.render(str(pos), 1, (10, 10, 10))
        self.screen.blit(text,(1,1,0,0))
        
        pygame.display.flip()
