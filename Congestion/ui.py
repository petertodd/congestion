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
    world = False

    def __init__(self,world,screen_size):
        self.world = world

        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)

    def do(self,dt):
        self.screen.fill((0,0,0))

        # Display the world

        if False:
            for n in self.world.nodes: 
                x,y = n.pos
                c = (100,100,100)
                size = 2
                if n.occupying is not None:
                    c = (255,0,0)
                pygame.draw.circle(self.screen,c,ip((x + 1,y + 1)),size)

        all_rails = []
        for track in self.world.tracks:
            pygame.draw.aaline(self.screen,(30,30,40),ip(track.a.pos),ip(track.b.pos))
            all_rails.extend(track.left_rails)
            all_rails.extend(track.right_rails)

        for intersection in self.world.intersections:
            all_rails.extend(intersection.rails)

        for rail in all_rails:
            pygame.draw.aaline(self.screen,(50,50,60),ip(rail.a.pos),ip(rail.b.pos))

        # draw the trains on the track
        for rail in all_rails: 
            # determine slope for later
            a = rail.a.pos
            b = rail.b.pos
            dx = b[0] - a[0]
            dy = b[1] - a[1]
            for p,t in rail.trains:
                def pos_to_v(pos):
                    f = pos / rail.length
                    return (rail.a.pos[0] + (dx * f),rail.a.pos[1] + (dy * f))

                train_start = pos_to_v(max(0,p))
                train_end = pos_to_v(min(rail.length,max(0,p + t.l)))
                buffer_end = pos_to_v(min(rail.length,max(0,p + t.l + t.b)))

                print train_start,train_end
                if train_start != train_end:
                    print 'drawing train',train_start,train_end
                    pygame.draw.aaline(self.screen,(255,0,0),ip(train_start),ip(train_end))

        # where the mouse is, equivilent to node id
        pos = pygame.mouse.get_pos()
        pygame.event.clear()

        font = pygame.font.Font(None, 12)
        text = font.render(str(pos), 1, (10, 10, 10))
        self.screen.blit(text,(1,1,0,0))
        
        pygame.display.flip()