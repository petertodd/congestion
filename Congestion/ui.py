# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

"""User interface."""

import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

import time

def ip(pos):
    x,y = pos
    return (int(x),int(y))

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
        self.fps = 25

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

        # Display the world

        all_rails = []
        for track in self.world.tracks:
            all_rails.extend(track.left_rails)
            all_rails.extend(track.right_rails)

        for intersection in self.world.intersections:
            all_rails.extend(intersection.rails)

        context.set_line_width(1.5)
        context.set_source_rgb(0.5,0.5,0.5)
        for rail in all_rails:
            context.move_to(rail.a.pos[0],rail.a.pos[1])
            context.line_to(rail.b.pos[0],rail.b.pos[1])
        context.stroke()

        # draw the trains on the track
        context.set_line_width(2.5)
        context.set_source_rgb(0.0,0.0,0.0)
        for rail in all_rails: 
            # determine slope for later
            a = rail.a.pos
            b = rail.b.pos
            dx = b[0] - a[0]
            dy = b[1] - a[1]
            for p,t in rail.trains:
                def pos_to_v(pos):
                    f = pos / rail.length
                    return (rail.a.pos[0] + (dx * f),rail.a.pos[1] + (dy * f))

                train_start = pos_to_v(max(0,p))
                train_end = pos_to_v(min(rail.length,max(0,p + t.l)))
                #buffer_end = pos_to_v(min(rail.length,max(0,p + t.l + t.b)))

                if train_start != train_end:
                    context.move_to(train_start[0],train_start[1])
                    context.line_to(train_end[0],train_end[1])
        context.stroke()

        context.move_to(10,10)
        context.show_text("%.1ffps" % self.fps)

def run_ui(world,dt):
    window = gtk.Window()
    ui = UserInterface(world,dt)

    window.add(ui)
    window.connect("destroy", gtk.main_quit)
    window.show_all()

    gtk.main()
