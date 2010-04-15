#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

"""User interface."""

import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

import time

from pylab import *
from scipy.spatial.distance import pdist,squareform

world_width = 1.920
world_height = 1.080

class UserInterface(gtk.DrawingArea):
    """The user interface."""

    screen = False
    world = False

    def __init__(self,dt):
        super(UserInterface,self).__init__()
        self.connect("expose_event",self.expose)

        self.dt = dt

        self.last = time.time()
        self.fps = 25
        self.draw_interval = 0

        self.x_shift = 0

        gobject.timeout_add(1000/self.fps, self.do_sim)

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

        context.set_line_width(1.0)

        x1 = 0 
        x2 = 2000.0

        y = 500.5
        loff = 3

        context.move_to(x1,y)
        context.line_to(x2,y)
        context.stroke()

        context.move_to(x1,y + loff)
        context.line_to(x2,y + loff)
        context.stroke()


        context.set_line_width(3.0)
        l =  5.0
        i = 30.0

        self.x_shift += 1
        x = self.x_shift % (l + i)
        while x < x2:
            print x,y
            context.move_to(x,y)
            context.line_to(x + l,y)
            x += l + i

        self.x_shift += 1
        x = self.x_shift % (l + i)
        while x < x2:
            print x,y
            context.move_to(x2 - x,y + loff)
            context.line_to(x2 - x + l,y + loff)
            x += l + i

        context.stroke()


def run_ui(n,dt):
    window = gtk.Window()
    ui = UserInterface(dt)

    window.add(ui)
    window.connect("destroy", gtk.main_quit)
    window.show_all()

    gtk.main()

run_ui(200,0.00001)
