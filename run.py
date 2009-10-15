import pygame
import numpy
import sys
import random
import time

pygame.init()

netimg = pygame.image.load(sys.argv[1])

led_width = 6
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
    """An ant is always on a node"""
    def __init__(self,x,y):
        self.x = x
        self.y = y

        self.ant = None
        self.owner = None

    def __repr__(self):
        return 'Node(x=%(x)d,y=%(y)d)' % self.__dict__

class Vertex:
    """A node with choices of edges to go to"""
    def __init__(self,node,edges):
        self.node = node

        # direction,edge
        self.edges = edges

class Edge:
    """A series of Nodes, connected to vertexes at either end"""
    def __init__(self,start,nodes,end):
        self.nodes = nodes
        # note, start and end refer to the nodes themselves, their owner gets you the vertexes
        self.start = start
        self.end = end

        # Direction of travel
        self.direction = 1

nodes = {}

TRAILING_MAX=256
class Ant:
    def __init__(self,vertex):
        self.vertex = vertex
        assert self.vertex.node.ant is None
        self.vertex.node.ant = self
        self.edge = None
        self.edge_i = None

    def do(self):
        if random.random() < 0.05:
            # do nothing
            return

        assert (self.vertex is None and self.edge is not None) or (self.vertex is not None and self.edge is None)
        if self.vertex is not None:
            #print 'on a vertex'
            neighboring_edges = []
            for e in self.vertex.edges:
                #print 'evaluating',e
                if e.start is self.vertex.node and e.direction == 1 and e.nodes[0].ant == None:
                    neighboring_edges.append((e,0))
                elif e.end is self.vertex.node and e.direction == -1 and e.nodes[-1].ant == None:
                    neighboring_edges.append((e,len(e.nodes) - 1))
            if len(neighboring_edges) == 0:
                #print 'no neighbors'
                if random.random() < 0.5:
                    edge_to_switch = random.choice(self.vertex.edges)
                    if edge_to_switch.direction == 1:
                        edge_to_switch.direction = -1
                    else:
                        edge_to_switch.direction = 1
                else:
                    return

            else:
                self.vertex.node.ant = None
                self.vertex = None

                e,i = random.choice(neighboring_edges)
                self.edge = e
                self.edge_i = i
                self.edge.nodes[self.edge_i].ant = self
        else:
            new_i = self.edge_i + self.edge.direction
            if 0 <= new_i < len(self.edge.nodes):
                #print self.edge.nodes,new_i
                if self.edge.nodes[new_i].ant is None:
                    self.edge.nodes[self.edge_i].ant = None
                    self.edge_i = new_i
                    self.edge.nodes[self.edge_i].ant = self
                else:
                    # sit and wait
                    return
                
            else:
                if new_i < 0 and self.edge.start.ant is None:
                    # at the start vertex
                    self.edge.nodes[self.edge_i].ant = None
                    self.edge.start.ant = self
                    self.vertex = self.edge.start.owner
                    self.edge = None
                elif new_i >= len(self.edge.nodes) and self.edge.end.ant is None:
                    # at the end vertex
                    self.edge.nodes[self.edge_i].ant = None
                    self.edge.end.ant = self
                    self.vertex = self.edge.end.owner
                    self.edge = None
                else:
                    pass
                    #print 'stuck',new_i,self.edge.start.ant,self.edge.end.ant,self


screen.fill((0,0,0))
def show_progress(node,color,dt=0):
    pygame.draw.circle(screen,color,(node.x * led_width,node.y * led_width),led_width / 2)
    pygame.display.flip()
    time.sleep(dt)

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
    assert isinstance(start.owner,Vertex)
    if next.owner is not None:
        return next.owner

    prev = start
    nodes = []
    r = Edge(None,None,None)
    while True: 
        n = find_node_neighbors(next)
        assert len(n) > 1
        if len(n) == 2:
            show_progress(next,(55,55,55))
            nodes.append(next)
            next.owner = r
            new_next = set(n).difference(set((prev,))).pop()
            prev = next
            next = new_next
        else:
            end = next
            break

    r.start = start
    assert len(nodes) > 0
    r.nodes = nodes
    r.end = end
    if r.end.owner is not None:
        r.end.owner.edges.append(r)
    return r

ants = []
def generate_vertex(node):
    assert not isinstance(node.owner,Edge)
    if isinstance(node.owner,Vertex):
        return node.owner

    show_progress(node,(55, 0, 0))
    
    neighbors = find_node_neighbors(node)
    assert len(neighbors) > 2

    node.owner = Vertex(node,None)
    
    ant = Ant(node.owner)
    ants.append(ant)

    edges = []
    for n in neighbors:
        edges.append(generate_edge(node,n))
    node.owner.edges = edges

    #print edges
    for e in edges:
        e.end.owner = generate_vertex(e.end)

    return node.owner

for n in nodes.itervalues():
    if len(find_node_neighbors(n)) > 2:
        generate_vertex(n)
        break

screen.fill((0,0,0))
for n in nodes.itervalues():
    color = led_color_off
    pygame.draw.circle(screen,led_color_off,(n.x * led_width,n.y * led_width),led_width / 2)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    random.shuffle(ants)
    i = 0
    for a in ants:
        n = None
        if a.edge:
            n = a.edge.nodes[a.edge_i]
        else:
            n = a.vertex.node
        pygame.draw.circle(screen,led_color_off,(n.x * led_width,n.y * led_width),led_width / 2)
        a.do()
        n = None
        if a.edge:
            n = a.edge.nodes[a.edge_i]
        else:
            n = a.vertex.node
        pygame.draw.circle(screen,led_color_on,(n.x * led_width,n.y * led_width),led_width / 2)

        i += 1
        if i % 10:
            pygame.display.flip()

#        time.sleep(0.1 / len(ants))
