import pygame
import sys
import random
import time

pygame.init()

netimg = pygame.image.load(sys.argv[1])

led_width = 4
led_color_on = (255,0,0)
led_color_off = (50,0,0)
xsize,ysize = netimg.get_size()

print xsize,ysize
screen = pygame.display.set_mode((xsize * led_width,ysize * led_width))

class Node:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.neighbors = set()
        self.ant = set()
nodes = {}

class Ant:
    def __init__(self,node):
        self.cur_node = node
        self.last_node = node
        self.cur_node.ant.add(self)

    def do(self):
        new_node = random.sample(self.cur_node.neighbors.difference(set((self.last_node,))),1)[0]
        self.last_node = self.cur_node
        self.cur_node = new_node
        self.last_node.ant.remove(self) 
        self.cur_node.ant.add(self)


pixels = pygame.surfarray.pixels3d(netimg)
for x in range(1,xsize - 1):
    for y in range(1,ysize - 1):
        if pixels[x][y][0] > 0:
            nodes[(x,y)] = Node(x,y)

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
            color = led_color_on
        pygame.draw.circle(screen,color,(n.x * led_width,n.y * led_width),led_width / 2)
    pygame.display.flip()

    time.sleep(0.1)
