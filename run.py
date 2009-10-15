import pygame
import numpy
import sys
import random
import time

pygame.init()

netimg = pygame.image.load(sys.argv[1])

led_width = 4
led_color_on = (200,0,0)
led_color_off = (30,30,30)
xsize,ysize = netimg.get_size()

print xsize,ysize
screen = pygame.display.set_mode((xsize * led_width,ysize * led_width))

goal_types = ('Temp','Sound','Home')

goal_network_colors = {(255,0,0):'Temp',
                       (0,0,255):'Sound',
                       (0,255,0):'Home'}

goal_network_colors_r = {}
for key,val in goal_network_colors.iteritems():
    goal_network_colors_r[val] = key
print goal_network_colors,goal_network_colors_r

class Node:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.neighbors = set()
        self.ant = set()
        self.goal = None
        self.goal_scents = {}
    def __repr__(self):
        return 'Node(x=%(x)d,y=%(y)d)' % self.__dict__
nodes = {}

class Ant:
    def __init__(self,node):
        self.cur_node = node
        self.last_node = node
        self.cur_node.ant.add(self)

        self.goal = 'Home'
        self.trailing = None

    def do(self):
        choices = tuple(self.cur_node.neighbors.difference(set((self.last_node,))))
        cum_choices = []
        cum = 0
        new_node = None
        for i in choices:
            cum += i.goal_scents.get(self.goal,0) ** 2
            cum_choices.append(cum)
        #print choices,cum_choices
        if cum_choices[-1] == 0:
            new_node = random.choice(choices)
        else:
            p = random.random() * cum_choices[-1]
            for new_node,cum in zip(choices,cum_choices):
                if cum > p:
                    break

        if self.trailing is not None:
            self.cur_node.goal_scents[self.trailing] = min(255,self.cur_node.goal_scents.get(self.trailing,0) + 20)


        self.last_node = self.cur_node
        self.cur_node = new_node
        self.last_node.ant.remove(self) 
        self.cur_node.ant.add(self)

        if self.cur_node.goal == self.goal:
            self.last_node = self.cur_node # important! we're going back the way we came
            if self.goal in ('Temp','Sound'):
                self.trailing = self.goal
                self.goal = 'Home'
            else:
                self.trailing = 'Home'
                if random.random() > 0.5:
                    self.goal = 'Temp'
                else:
                    self.goal = 'Sound'

pixels = pygame.surfarray.pixels3d(netimg)
for x in range(1,xsize - 1):
    for y in range(1,ysize - 1):
        pixel = pixels[x][y]
        if pixel:
            nodes[(x,y)] = Node(x,y)
            # pixel = tuple(pixel)
            # The above doesn't work, as the individual elements of the array,
            # are arrays as well it seems.
            pixel = (int(pixel[0]),int(pixel[1]),int(pixel[2]))
            if goal_network_colors.get(pixel) is not None:
                nodes[(x,y)].goal = goal_network_colors[pixel]

for i in nodes.itervalues():
    for dx,dy in ((0,-1),(1,0),(0,1),(-1,0)):
        j = nodes.get((i.x - dx,i.y - dy))
        if j:
            i.neighbors.add(j)
    if len(i.neighbors) < 2: 
        for dx,dy in ((-1,-1),(1,-1),(1,1),(-1,1)):
            j = nodes.get((i.x - dx,i.y - dy))
            if j:
                i.neighbors.add(j)

for i in nodes.itervalues():
    if len(i.neighbors) < 1:
        print 'Bad # of neighbors at ',i.x,i.y,i.neighbors
        sys.exit(1)

ants = [Ant(n) for n in random.sample(set(nodes.itervalues()),10)]
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    for a in ants:
        a.do()

    screen.fill((0,0,0))
    for n in nodes.itervalues():
        # draw connecting lines to neighbors
        for i in n.neighbors:
            pygame.draw.line(screen,(50,50,0),(n.x * led_width,n.y * led_width),(i.x * led_width,i.y * led_width))
    for n in nodes.itervalues():
        color = led_color_off
        if n.ant:
            color = goal_network_colors_r[tuple(n.ant)[0].goal]
        elif n.goal:
            color = goal_network_colors_r[n.goal]
        else:
            color = numpy.array(color)
            for g in goal_types:
                if n.goal_scents.get(g) is not None and n.goal_scents[g] > 0:
                    color += (n.goal_scents[g] / 256.0) * numpy.array(goal_network_colors_r[g]) / 2
                    n.goal_scents[g] -= 0.1
        color = (min(255,color[0]),min(255,color[1]),min(255,color[2]))
        pygame.draw.circle(screen,color,(n.x * led_width,n.y * led_width),led_width / 2)
    pygame.display.flip()

    time.sleep(0.1)
