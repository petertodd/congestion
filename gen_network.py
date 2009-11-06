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

goal_network_colors_r = {}
for key,val in goal_network_colors.iteritems():
    goal_network_colors_r[val] = key
print >>sys.stderr,goal_network_colors,goal_network_colors_r

class Node:
    """An ant is always on a node"""
    def __init__(self,x,y):
        self.x = x
        self.y = y

        self.owner = None

    def __repr__(self):
        return 'Node(x=%(x)d,y=%(y)d)' % self.__dict__

vertexes = []
class Vertex:
    """A node with choices of edges to go to"""
    def __init__(self,node,edges):
        self.node = node

        # direction,edge
        self.edges = edges

        vertexes.append(self)

edges = []
class Edge:
    """A series of Nodes, connected to vertexes at either end"""
    def __init__(self,start,nodes,end):
        self.nodes = nodes
        # note, start and end refer to the nodes themselves, their owner gets you the vertexes
        self.start = start
        self.end = end

        # Direction of travel
        self.direction = 1

        edges.append(self)

nodes = {}

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
            nodes[(x,y)] = Node(x,y)
            show_progress(nodes[(x,y)],(20,20,20),0)
            # pixel = tuple(pixel)
            # The above doesn't work, as the individual elements of the array,
            # are arrays as well it seems.
            #pixel = (int(pixel[0]),int(pixel[1]),int(pixel[2]))
            #if goal_network_colors.get(pixel) is not None:
            #    nodes[(x,y)].goal = goal_network_colors[pixel]



def find_node_neighbors(node):
    r = set()
    # prefer horizontal and vertical neighbors
    for dx,dy in ((0,-1),(1,0),(0,1),(-1,0)):
        j = nodes.get((node.x - dx,node.y - dy))
        if j is not None:
            r.add(j)
    return r


def generate_edge(start,next):
    # start is the vertex that is generating us, next is the next node in the
    # trail.
    assert isinstance(start,Vertex)
    assert next.owner is None

    # Edges should have at least one node in them, directly connecting a vertex
    # to a vertex is not allowed. Therefor next should have exactly two neighbors.
    assert len(find_node_neighbors(next)) == 2

    # The start vertex is known, create the edge and assign it to the start
    # vertexes edge list.
    edge = Edge(start,[],None)
    start.edges.append((edge,0))

    prev = start.node
    while True:
        neighbors = find_node_neighbors(next)
        if len(neighbors) != 2:
            break

        show_progress(next,(75, 0, 0))

        next.owner = edge
        edge.nodes.append(next)

        # Next edge is the neighbor that was not the previous edge
        cur = next
        next = find_node_neighbors(cur).difference(set((prev,))).pop()
        prev = cur

    # Detect dead ends
    assert len(neighbors) > 2

    assert len(edge.nodes) > 0

    # Should be impossible to have a node with more than 2 neighbors be owned
    # by an edge.
    assert not isinstance(next.owner,Edge)

    # Must be at a node that could be a vertex.
    #
    # Is the edge unowned?
    if next.owner is None:
        # Continue the generation process, creating a new vertex.
        generate_vertex(next)
    else:
        # The search must have looped back upon itself; do nothing, the
        # generate_vertex() code will add that vertex to as our end when it
        # checks node next as a potential neighbor.
        pass

def generate_vertex(node):
    assert node.owner is None

    show_progress(node,(95, 0, 0))

    # Create a Vertex owning the starting node immediately. If the search loops
    # around to this node, it needs to have an owner so the search will
    # terminate.
    edges = []
    node.owner = Vertex(node,edges)

    # Now for each neighboring node, generate the attached edge.
    neighbors = find_node_neighbors(node)
    assert len(neighbors) > 2
    for n in neighbors:
        # If the owner is not none, either we found the edge from the
        # generate_edge() that called us, or the search looped back upon
        # itself. In either case we are that edges end.
        if n.owner is not None:
            assert isinstance(n.owner,Edge)

            # Set that edges end to be ourselves
            n.owner.end = node.owner

            # And add that edge to our edges list; note that we're guaranteed
            # to be that edges end. Potentially, we're also that eges beginning.
            node.owner.edges.append((n.owner,len(n.owner.nodes) - 1))
        else:
            # A virgin edge, generate.
            generate_edge(node.owner,n)

for n in nodes.itervalues():
    if len(find_node_neighbors(n)) > 2:
        generate_vertex(n)
        break

screen.fill((0,0,0))
for n in nodes.itervalues():
    color = led_color_off
    pygame.draw.circle(screen,led_color_off,(n.x * led_width,n.y * led_width),led_width / 2)



# Done generating the world. Now we need to output the data to C. There are two
# files involved, a C header with all the definitions, such as the NUM_*
# #defines, and a C source that staticly initializes the contents of the
# involved arrays.
#
# Generation proceeds in two stages, first initialization lines for the nodes,
# edges, and vertexes are collected. Then the strings are .join'ed up and
# written to the output files.
#
# Node data generation is fairly simple, as the involved data structure simply
# consists of x and y co-ordinates, and a pointer to any ant on the node, which
# is of course set to NULL.
#
# However, the edge structure has a pointer to the array of nodes comprising
# each edge. Since each node can only belong to one edge (or one vertex) we can
# be clever here, and avoid an additional layer of indirection. The actual
# nodes list is generated while edges are generated, and each set of nodes
# belonging to a single edge is put contiguously in memory. Given a set of
# edges a,b,c,d the ownership of the resulting nodes list would be as follows:
#
# AAAAABBBBCCCDD
#
# Where edge A has five nodes in it, B four nodes etc.
#
#
#


node_lines = []
def add_node_to_node_lines(n,comment = ''):
    node_lines.append('{%d,%d,0}, // #%d %s' % (n.x,n.y,len(node_lines),comment))

# The vertex generation code refers to the edges table later on, so keep a map
# of edge indexes by edge so it can generate the required pointers.
edge_idxs_by_edge = {}
edge_lines = []
for e in edges:
    # Save the index to the beginning of this edges nodes in the final nodes list.
    beginning_of_this_edges_nodes = len(node_lines)

    for n in e.nodes:
        add_node_to_node_lines(n,'Edge %d' % len(edge_lines) if e.nodes[0] is n else '')

    edge_idxs_by_edge[e] = len(edge_lines)

    # Since the vertex_lines haven't been generated yet, insert references to
    # the start and end vertexes as part of a tuple along with the bits of the
    # known string comprising the edge line. Later, after the vertex_lines
    # generation, we'll resolve those.
    edge_lines.append(\
            ('{0,0,(struct vertex *)',e.start,',(struct vertex *)',e.end,',{{65535,65535},{65535,65535}},%d,(struct node *)%d}, // #%d' \
                % (len(e.nodes),beginning_of_this_edges_nodes,len(edge_lines))))

vertex_lines = []
vertex_idxs_by_vertex = {}
for v in vertexes:
    # offset by 1 so we can represent NULL's with 0's
    v_edges_idx_list = [(edge_idxs_by_edge[e] + 1,i) for e,i in v.edges]
    # pad with null's
    v_edges_idx_list.extend([(0,2**8-1) for i in range(0,4 - len(v_edges_idx_list))])

    vertex_idxs_by_vertex[v] = len(vertex_lines)
    vertex_lines.append(\
            '{(struct node *)%d,{%s}}, // #%d' \
            % (len(node_lines),\
               ','.join(['{(struct edge *)%d,%d}' % (e,i) for e,i in v_edges_idx_list]),
               len(vertex_lines)))
    add_node_to_node_lines(v.node,'Vertex %d' % (len(vertex_lines) - 1))

# Resolve vertex references in edge_lines
edge_lines = [''.join([str(vertex_idxs_by_vertex[part]) if isinstance(part,Vertex) else part for part in line]) \
                for line in edge_lines]

# Save the final structures to the output files.
fd_defs = open(sys.argv[2],'w')
fd_data = open(sys.argv[3],'w')

print >>fd_defs,\
"""// AUTOGENERATED
// Network defs

#define WORLD_WIDTH (%(world_width)d)
#define WORLD_HEIGHT (%(world_height)d)

#define NUM_NODES (%(num_nodes)d)
#define NUM_EDGES (%(num_edges)d)
#define NUM_VERTEXES (%(num_vertexes)d)

extern struct node nodes[];
extern struct edge edges[];
extern struct vertex vertexes[];
""" % {'world_width':xsize,
       'world_height':ysize,
       'num_nodes':len(nodes),
       'num_edges':len(edges),
       'num_vertexes':len(vertexes)
      }

print >>fd_data,\
"""// AUTOGENERATED
// Network data

struct node nodes[] = {
%(node_lines)s
};

struct edge edges[] = {
%(edge_lines)s
};

struct vertex vertexes[] = {
%(vertex_lines)s
};
""" % {'node_lines':'\n'.join(node_lines),
       'edge_lines':'\n'.join(edge_lines),
       'vertex_lines':'\n'.join(vertex_lines)}

while len(sys.argv) < 5:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

#        time.sleep(0.1 / len(ants))
