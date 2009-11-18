#!/usr/bin/python
# (c) 2009 Peter Todd
import pygame
import numpy
import sys
import random
import time
from collections import deque
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

goal_types = (0,1)

goal_network_colors = {(255,0,0):0,
                       (0,0,255):1}

MAX_NODE_NEIGHBORS = 8
MAX_GOAL_DIST = 2**16-1
INVALID_NODE_IDX = 2**16-1

goal_network_colors_r = {}
for key,val in goal_network_colors.iteritems():
    goal_network_colors_r[val] = key
print >>sys.stderr,goal_network_colors,goal_network_colors_r

nodes = []
nodes_by_xy = {}

class Node:
    """An ant is always on a node"""
    def __init__(self,x,y,goal = None):
        global max_node_idx
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
            for dx,dy in ((0,-1),(1,0),(0,1),(-1,0)):
                j = nodes_by_xy.get((self.x - dx,self.y - dy))
                if j is not None:
                    self.neighbors.add(j)
        return self.neighbors 

    def __repr__(self):
        return 'Node(x=%(x)d,y=%(y)d)' % self.__dict__

screen.fill((0,0,0))
show_progresses = 0
def show_progress(node,color,dt=0,update_interval=100):
    if dt != 0:
        update_interval = 1

    pygame.draw.circle(screen,color,(node.x * led_width,node.y * led_width),led_width / 2)
    global show_progresses
    show_progresses += 1
    if show_progresses > update_interval:
        show_progresses = 0
        pygame.display.flip()
    if dt: time.sleep(dt)


# generate the map
pixels = pygame.surfarray.pixels3d(netimg)
for x in range(1,xsize - 1):
    for y in range(1,ysize - 1):
        pixel = pixels[x][y]
        if pixel:
            goal = None
            if pixel[0] == 255:
                goal = 0
            elif pixel[2] == 255:
                goal = 1
            nodes_by_xy[(x,y)] = Node(x,y,goal)
            show_progress(nodes_by_xy[(x,y)],(20,20,20),dt=0)
            # pixel = tuple(pixel)
            # The above doesn't work, as the individual elements of the array,
            # are arrays as well it seems.
            #pixel = (int(pixel[0]),int(pixel[1]),int(pixel[2]))
            #if goal_network_colors.get(pixel) is not None:
            #    nodes_by_xy[(x,y)].goal = goal_network_colors[pixel]

for n in nodes:
    n.find_neighbors()

# compute goal distances with Dijkstra's algorithm
max_goal_dist_in_network = {0:0,1:0}
def pathfind(node,goal,best):
    stack = deque(((node,0),))

    while len(stack):
        (node,best) = stack.popleft()

        # lights = min(255,node.goal_dists.get(0,best + 1 if goal == 0 else 0) / 5)
        # darks = min(255,node.goal_dists.get(1,best + 1 if goal == 1 else 0) / 5)
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


# Nodes and node distances are done. Now we need to extract vertexes and edges
# from that map.
class Edge:
    pass
vertex_idx = 0
class Vertex:
    def __init__(self,node):
        self.node = node
        node.owner = self

        global vertex_idx
        self.idx = vertex_idx
        vertex_idx += 1

vertex_nodes = []
remaining_edge_nodes = set()

# Separate the nodes into vertex and edge nodes.
for n in nodes:
    if len(n.neighbors) > 2:
        vertex_nodes.append(n)
    else:
        remaining_edge_nodes.add(n)

# Generate edges.
edges = []
while remaining_edge_nodes:
    edge = Edge()
    edges.append(edge)
    center = remaining_edge_nodes.pop()
    center.owner = edge
    enodes = set((center,))
    nodes_list = deque((center,))
    assert len(center.neighbors) == 2
    right,left = center.neighbors

    while right is not None or left is not None:
        def evaluate(n,f):
            if n is not None and len(n.neighbors) == 2:
                remaining_edge_nodes.remove(n)
                enodes.add(n)
                f(n)
                n.owner = edge
                return n.neighbors.difference(enodes).pop()
            else:
                return None
        right = evaluate(right,lambda n: nodes_list.appendleft(n))
        left = evaluate(left,lambda n: nodes_list.append(n))
    edge.nodes = nodes_list

# Generate vertexes
vertexes = []
for n in vertex_nodes:
    vertexes.append(Vertex(n))

# Assign node idxs to all the nodes, making sure edges are contiguous.
i = 0
for e in edges:
    for n in e.nodes:
        n.idx = i
        i += 1
for v in vertexes:
    v.node.idx = i
    i += 1



# Done generating the world. Now we need to output the data to C. There are two
# files involved, a C header with all the definitions, such as the NUM_*
# #defines, and a C source that staticly initializes the contents of the
# involved arrays.

# Interestingly, there is actually only one array involved, the vertexes fixed
# data. Edges and nodes are implied by the index numbers, and there is no fixed
# data associated with them.
vertex_lines = []
for v in vertexes:
    # HACK! Keep the ordering consistant
    v.node.neighbors = list(v.node.neighbors)

    # Find the end vertexes for the adjacent edges
    neighbors = []
    for n in v.node.neighbors:
        # The edge nodes list has two end points. One of those end points will
        # have our node as a neighbor, the other will not. This gives us the
        # start and end nodes of the edge.
        start_node = None
        end_node = None
        if v.node in n.owner.nodes[0].neighbors:
            start_node = n.owner.nodes[0]
            end_node = n.owner.nodes[-1]
        else:
            start_node = n.owner.nodes[-1]
            end_node = n.owner.nodes[0]

        # The end vertex, can be found by finding the neighbor of the end node
        # that is not a member of the edge's nodes.
        end_vertex = end_node.neighbors.difference(set(n.owner.nodes)).pop().owner

        neighbors.append((start_node,end_node,end_vertex))

    # Calculate the relative goal distances
    goal_dists = [(min(g[0],255),min(g[1],255)) for g in [end_vertex.node.goal_dists for (start,end,end_vertex) in neighbors]]
    min0 = 100000
    min1 = 100000
    print goal_dists
    for d0,d1 in goal_dists:
        min0 = min(min0,d0)
        min1 = min(min1,d1)
    goal_dists = [((d0 - min0),(d1 - min1)) for d0,d1 in goal_dists]

    neighbor_lines = []
    for (start_node,end_node,end_vertex),(gd0,gd1) in zip(neighbors,goal_dists):
        neighbor_lines.append(\
            "{%(valid)d,%(start_idx)d,%(end_idx)d,%(vertex_idx)d,{%(goal_dist_0)d,%(goal_dist_1)d}}" % \
                    {'valid':1,
                     'start_idx':start_node.idx,
                     'end_idx':end_node.idx,
                     'vertex_idx':end_vertex.idx,
                     'goal_dist_0':gd0,
                     'goal_dist_1':gd1})
    neighbor_lines.extend(['{0,0,0,0,{0,0}}'] * (4 - len(v.node.neighbors)))
    neighbor_lines = ','.join(neighbor_lines)

    vertex_lines.append('{%d,{%s}}' % (v.node.idx,neighbor_lines))

# For the sake of debugging, produce a list of nodes and who their owners are
#
# This is also a good time to produce the node_idx->(x,y) table that's needed
# for the xwindows target.
nodes_lines = ['// Nodes list']
xy_lines = []
def add_xy_line(n):
    xy_lines.append('{%d,%d}, // %d' % (n.x,n.y,n.idx))
for e,eidx in zip(edges,range(0,len(edges))):
    for n in e.nodes:
        nodes_lines.append('// %d%s' % \
                (n.idx,
                 ' - Edge %d' % eidx if n is e.nodes[0] else ''))
        add_xy_line(n)
for v in vertexes:
    nodes_lines.append('// %d - Vertex %d' % (v.node.idx,v.idx))
    add_xy_line(v.node)

# Save the final structures to the output files.
fd_defs = open(sys.argv[2],'w')
fd_data = open(sys.argv[3],'w')

print >>fd_defs,\
"""// AUTOGENERATED
// Network defs

#define WORLD_WIDTH (%(world_width)d)
#define WORLD_HEIGHT (%(world_height)d)

#define NUM_NODES (%(num_nodes)d)
#define NUM_VERTEXES (%(num_vertexes)d)

struct node_idx_to_xy {
    uint16_t x,y;
};

extern const struct node_idx_to_xy node_idx_to_xy[%(num_nodes)d];

extern const uint16_t max_goal_dist_in_network[2];

""" % {'world_width':xsize,
       'world_height':ysize,
       'num_nodes':len(nodes),
       'num_vertexes':len(vertexes),
      }

print >>fd_data,\
"""// AUTOGENERATED
// Network data

%(nodes_lines)s

const struct vertex_rom vertexes_rom[] = {
%(vertex_lines)s
};

const uint16_t max_goal_dist_in_network[] = {%(max_light)d,%(max_dark)d};

const struct node_idx_to_xy node_idx_to_xy[] = {
%(xy_lines)s
};

""" % {'nodes_lines':'\n'.join(nodes_lines),
       'vertex_lines':',\n'.join(vertex_lines),
       'xy_lines':'\n'.join(xy_lines),
       'max_light':max_goal_dist_in_network[0],
       'max_dark':max_goal_dist_in_network[1]}

while len(sys.argv) < 5:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

#        time.sleep(0.1 / len(ants))
