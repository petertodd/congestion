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

        gobject.timeout_add(self.dt * 1000, self.do_sim)

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
        print self.fps
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
        self.R = 1000

    def do(self,dt):
        # Add points randomly, probability based on proximity to mass, with a
        # repulsion term
        n = 0
        while n < 1:
            p = random(2) * world_shape 

            d = distance_matrix((p,),self.p)[0]

            g = sum(self.G*(self.m/d**2.7))
            r = sum(self.R*(self.m/d**4))

            print g,r
            if random() < (g - r):
                print 'new at',p,g,r
                self.p.append(p)
                self.m.append(1)
                n += 1

        # Generate traffic

def run_ui(dt):
    window = gtk.Window()
    ui = UserInterface(World(),dt)

    window.add(ui)
    window.connect("destroy", gtk.main_quit)
    window.show_all()

    gtk.main()

run_ui(1/25.0)
