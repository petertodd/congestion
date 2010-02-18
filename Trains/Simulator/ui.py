# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

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
        self.screen.fill((0,0,0))

        # Display the network

        # Draw the tracks and nodes
        for track in self.network.tracks:
#            for n in (track.a,track.b):
#                x,y = n.pos
#                c = (0,0,0)
#                size = 2
#                if n.occupying is not None:
#                    c = (255,0,0)
#                pygame.draw.circle(self.screen,c,ip((x + 1,y + 1)),size)
            pygame.draw.aaline(self.screen,(100,100,100),ip(track.a.pos),ip(track.b.pos))

        # draw the trains on the track
        for track in self.network.tracks:
            # determine slope for later
            a = track.a.pos
            b = track.b.pos
            dx = b[0] - a[0]
            dy = b[1] - a[1]
            for p,t in track.trains:
                def pos_to_v(pos):
                    f = pos / track.length()
                    return (track.a.pos[0] + (dx * f),track.a.pos[1] + (dy * f))

                train_start = pos_to_v(max(0,p))
                train_end = pos_to_v(min(track.length(),max(0,p + t.l)))
                buffer_end = pos_to_v(min(track.length(),max(0,p + t.l + t.b)))

                pygame.draw.aaline(self.screen,(255,0,0),ip(train_start),ip(train_end))
                pygame.draw.aaline(self.screen,(75,0,0),ip(train_end),ip(buffer_end))

        # where the mouse is, equivilent to node id
        pos = pygame.mouse.get_pos()
        pygame.event.clear()

        font = pygame.font.Font(None, 12)
        text = font.render(str(pos), 1, (10, 10, 10))
        self.screen.blit(text,(1,1,0,0))
        
        pygame.display.flip()
