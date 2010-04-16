#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

import time

from pylab import *
from scipy.spatial import distance_matrix
from scipy.spatial.distance import pdist,squareform

world_shape = (1920,1080)

class UserInterface(gtk.DrawingArea):
    """The user interface."""

    screen = False
    world = False

    def __init__(self,world,dt):
        super(UserInterface,self).__init__()
        self.connect("expose_event",self.expose)

        self.dt = dt
        self.world = world

        self.last = time.time()
        self.draw_interval = 0

        gobject.timeout_add(int(self.dt * 1000), self.do_sim)

    def expose(self, widget, event):
        context = widget.window.cairo_create()

        # Restrict Cairo to the exposed area; avoid extra work
        context.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
        context.clip()

        self.draw(context)

    def do_sim(self):
        now = time.time()
        self.fps = (1/(now - self.last))
        self.world.do((now - self.last) / 2)
        self.redraw_canvas()
        self.last = now

        return True

    def redraw_canvas(self):
        if self.window:
            alloc = self.get_allocation()
            rect = gtk.gdk.Rectangle(alloc.x,alloc.y,alloc.width,alloc.height)
            self.window.invalidate_rect(rect,True)
            self.window.process_updates(True)

    def draw(self, context):
        rect = self.get_allocation()

        context.set_source_rgb(1.0, 1.0 , 1.0 )
        context.rectangle(0, 0, rect.width, rect.height)
        context.fill()
        context.set_source_rgb(0.0,0.0,0.0)

        for p,m in zip(self.world.p,self.world.m):
            context.move_to(p[0],p[1])
            context.arc(p[0],p[1],m,0,2*pi)
            context.fill()

        for (a,b),m in self.world.r.iteritems():
            a = self.world.p[a]
            b = self.world.p[b]
            context.set_line_width(1.0)
            context.move_to(a[0],a[1])
            context.line_to(b[0],b[1])
            context.stroke()

class World:
    def __init__(self):
        # Point locations
        self.p = [array(world_shape) / 2]

        # Point masses
        self.m = [1]

        # Roads connect points, specifically act as a distance multiplier to
        # reduce effective distance
        self.r = {}


        # gravitational constant
        self.G = 100 

        # repulsion constant
        self.R = 300

    def do(self,dt):
        # Add points randomly, probability based on proximity to mass, with a
        # repulsion term
        n = 0
        while n < 1:
            p = random(2) * world_shape 

            d = distance_matrix((p,),self.p)[0]

            g = sum(self.G*(self.m/d**2.7))
            r = sum(self.R*(self.m/d**4))

            if random() < (g - r):
                self.p.append(p)
                self.m.append(1)
                n += 1

        def mkroad(a,b):
            # create road between a and b
            #
            # in doing so, create intermediate nodes spaced l apart
            l = 10.0

            ap = self.p[a]
            bp = self.p[b]

            d_ap_bp = array(bp) - ap
            d = sqrt(dot(d_ap_bp,d_ap_bp))
            n = int(d / l) + 1

            path = array([linspace(ap[0],bp[0],num=n),
                          linspace(ap[1],bp[1],num=n)]).transpose()

            # create new nodes for the intermediate points on the path
            old_p_end = len(self.p)
            self.p.extend(path[1:-1])
            self.m.extend((1,) * (len(path) - 2))

            last = a
            for i in range(old_p_end,len(self.p)) + [b,]:
                self.r[tuple(sorted((last,i)))] = 0

        # Generate traffic
        for j in range(25):
            dists = squareform(pdist(self.p))

            pos = randint(len(self.p))
            dest = randint(len(self.p))
            while pos != dest:
                # pick the closest node, that gets us closer to our destination
                dist_to_goal = dists[pos,dest]
                closest_to_us = argsort(dists[pos])
                for i in closest_to_us:
                    if dists[i,dest] < dist_to_goal:
                        new_pos = i
                        break
                assert pos != new_pos
                if not tuple(sorted((pos,new_pos))) in self.r:
                    mkroad(pos,new_pos)
                self.r[tuple(sorted((pos,new_pos)))] += 1

                pos = new_pos







def run_ui(dt):
    window = gtk.Window()
    ui = UserInterface(World(),dt)

    window.add(ui)
    window.connect("destroy", gtk.main_quit)
    window.show_all()

    gtk.main()

run_ui(1/25.0)
