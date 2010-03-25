# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

import pygame
import numpy as np
import scipy.spatial.distance
from numpy.random import random,randint
import time

screen_size = (1920,1080)

pygame.init()
screen = pygame.display.set_mode(screen_size)

screen.fill((0,0,0))

grid = np.zeros(screen_size)

# generate some random hotspots
n = 10
hotspots = [np.random.random(2) * screen_size for i in range(n)]
hotspot_intensities = [1 for i in range(n)]
#hotspots = ((0,0),)
#hotspot_intensities = (1,)

print 'hotspots are',zip(hotspots,hotspot_intensities)

positions = []
for x in range(screen_size[0]):
    for y in range(screen_size[1]):
        positions.append((x,y))
positions = np.array(positions) 
grid = scipy.spatial.distance.cdist(hotspots,positions,'euclidean')

for i,v in enumerate(hotspot_intensities):
    grid[i] *= v

grid /= np.max(grid)
grid = 1 - grid

# change into exponential
grid **= 10

grid = np.sum(grid,axis=0)
grid /= np.max(grid)

# convert back to 2d dimensions
grid = np.reshape(grid,screen_size)


if False:
    # convert to pixels, grayscale
    pixels = np.tile(grid.transpose(),(3,1,1)).transpose()
    pygame.surfarray.use_arraytype('numpy')
    pygame.surfarray.blit_array(screen,pixels * 255)


#            pygame.draw.aaline(self.screen,(30,30,40),ip(track.a.pos),ip(track.b.pos))

nodes = []
while len(nodes) < 2500:
    p = np.random.random(2) * screen_size
    p = p.astype(int)
    if grid[p[0],p[1]] ** 3 > random():
        nodes.append(p)
        screen.set_at(p,(255,0,0))

dists = scipy.spatial.distance.pdist(nodes,'euclidean')
dists = scipy.spatial.distance.squareform(dists)

edges = {}

pygame.display.flip()
pos = 0 
dest = 1 
while True:
    # Generate roads by taking random trips
    if pos == dest:
        dest += 1
        if dest >= len(nodes):
            print 'done'
            while True:
                pygame.display.flip()

    oldpos = pos

    # Find the closest node, that gets us closer to our destination.
    dist_to_goal = dists[pos,dest]

    closest_to_us = np.argsort(dists[pos])
    for i in closest_to_us:
        print pos,dest,i,dists[pos,i],dist_to_goal
        if dists[i,dest] < dist_to_goal:
            pos = i
            break

    if pos == oldpos:
        # shouldn't happen
        while True:
            pass

    if not (oldpos,pos) in edges and not (pos,oldpos) in edges:
        edges[(oldpos,pos)] = True
        pygame.draw.aaline(screen,(60,60,80),nodes[oldpos],nodes[pos])

    pygame.display.flip()
