#!/usr/bin/python
# (c) 2009 Peter Todd
import pygame
import numpy
import sys
import random
import time
sys.setrecursionlimit(10000)

pygame.init()

netimg = pygame.image.load(sys.argv[1])

led_width = 6
led_color_on = (200,0,0)
led_color_off = (30,30,30)
xsize,ysize = netimg.get_size()

xsize,ysize = netimg.get_size()

print >>sys.stderr,xsize,ysize
screen = pygame.display.set_mode((xsize * led_width,ysize * led_width))

goal_types = ('Light','Dark')

goal_network_colors = {(255,0,0):'Light',
                       (0,0,255):'Dark'}

MAX_NODE_NEIGHBORS = 8
MAX_GOAL_DIST = 2**16-1
INVALID_NODE_IDX = 2**16-1

goal_network_colors_r = {}
for key,val in goal_network_colors.iteritems():
    goal_network_colors_r[val] = key
print >>sys.stderr,goal_network_colors,goal_network_colors_r

nodes = []
nodes_by_xy = {}

max_node_idx = -1
class Node:
    """An ant is always on a node"""
    def __init__(self,x,y,goal = None):
        global max_node_idx
        max_node_idx += 1
        self.idx = max_node_idx

        self.x = x
        self.y = y

        self.owner = None

        self.goal_dists = {}
        self.goal = goal

        self.neighbors = None

        nodes.append(self)
        nodes_by_xy[(self.x,self.y)] = self

    def find_neighbors(self):
        if self.neighbors is None:
            self.neighbors = set()
            for dx,dy in ((0,-1),(1,0),(0,1),(-1,0),(-1,-1),(1,-1),(1,1),(-1,1)):
                j = nodes_by_xy.get((self.x - dx,self.y - dy))
                if j is not None:
                    self.neighbors.add(j)
        return self.neighbors 

    def __repr__(self):
        return 'Node(x=%(x)d,y=%(y)d)' % self.__dict__

screen.fill((0,0,0))
show_progresses = 0
def show_progress(node,color,dt=0):
    pygame.draw.circle(screen,color,(node.x * led_width,node.y * led_width),led_width / 2)
    global show_progresses
    show_progresses += 1
    if show_progresses > 100:
        show_progresses = 0
        pygame.display.flip()
    #time.sleep(dt)


# generate the map
pixels = pygame.surfarray.pixels3d(netimg)
for x in range(1,xsize - 1):
    for y in range(1,ysize - 1):
        pixel = pixels[x][y]
        if pixel:
            goal = None
            if pixel[0] == 255:
                goal = 'Light'
            elif pixel[2] == 255:
                goal = 'Dark'
            nodes_by_xy[(x,y)] = Node(x,y,goal)
            show_progress(nodes_by_xy[(x,y)],(20,20,20),0)
            # pixel = tuple(pixel)
            # The above doesn't work, as the individual elements of the array,
            # are arrays as well it seems.
            #pixel = (int(pixel[0]),int(pixel[1]),int(pixel[2]))
            #if goal_network_colors.get(pixel) is not None:
            #    nodes_by_xy[(x,y)].goal = goal_network_colors[pixel]

for n in nodes:
    n.find_neighbors()

# compute goal distances with Dijkstra's algorithm
max_goal_dist_in_network = {'Light':0,'Dark':0}
def pathfind(node,goal,best):
    from collections import deque
    stack = deque(((node,0),))

    while len(stack):
        (node,best) = stack.popleft()

        # lights = min(255,node.goal_dists.get('Light',best + 1 if goal == 'Light' else 0) / 5)
        # darks = min(255,node.goal_dists.get('Dark',best + 1 if goal == 'Dark' else 0) / 5)
        # show_progress(node,(lights,0,darks))

        if node.goal_dists.get(goal,best + 1) > best:
            node.goal_dists[goal] = best
            global max_goal_dist_in_network
            max_goal_dist_in_network[goal] = max(max_goal_dist_in_network[goal],best)

            for n in node.neighbors:
                # show_progress(n,(0,100,0))
                stack.append((n,best + 1))

for n in nodes:
    if n.goal is not None:
        print 'pathfinding, starting at',n,'for',n.goal
        pathfind(n,n.goal,0)

screen.fill((0,0,0))
for n in nodes:
    color = led_color_off
    pygame.draw.circle(screen,led_color_off,(n.x * led_width,n.y * led_width),led_width / 2)



# Done generating the world. Now we need to output the data to C. There are two
# files involved, a C header with all the definitions, such as the NUM_*
# #defines, and a C source that staticly initializes the contents of the
# involved arrays.

node_lines = []
for n in nodes:
    print n
    neighbor_idxs = [adj.idx for adj in n.neighbors] + ([INVALID_NODE_IDX,] * (MAX_NODE_NEIGHBORS - len(n.neighbors)))

    node_lines.append('{%d,%d,{%s},{%d,%d}}, // #%d' % \
            (n.x,n.y,
             ','.join(['%d' % i for i in neighbor_idxs]),
             n.goal_dists['Light'],n.goal_dists['Dark'],
             n.idx))

# Save the final structures to the output files.
fd_defs = open(sys.argv[2],'w')
fd_data = open(sys.argv[3],'w')

print >>fd_defs,\
"""// AUTOGENERATED
// Network defs

#define WORLD_WIDTH (%(world_width)d)
#define WORLD_HEIGHT (%(world_height)d)

#define NUM_NODES (%(num_nodes)d)

extern goal_dist_t max_goal_dist_in_network[NUM_GOALS];

#define MAX_NODE_NEIGHBORS (%(max_node_neighbors)d)
#define INVALID_NODE_IDX (%(invalid_node_idx)d)
""" % {'world_width':xsize,
       'world_height':ysize,
       'num_nodes':len(nodes),
       'max_goal_dist_in_network':max_goal_dist_in_network,
       'max_node_neighbors':MAX_NODE_NEIGHBORS,
       'invalid_node_idx':INVALID_NODE_IDX,
      }

print >>fd_data,\
"""// AUTOGENERATED
// Network data

struct node nodes[] = {
%(node_lines)s
};

goal_dist_t max_goal_dist_in_network[] = {%(max_light)d,%(max_dark)d};
""" % {'node_lines':'\n'.join(node_lines), \
        'max_light':max_goal_dist_in_network['Light'],
        'max_dark':max_goal_dist_in_network['Dark']}

while len(sys.argv) < 5:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

#        time.sleep(0.1 / len(ants))
