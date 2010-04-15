#!/usr/bin/env python

import gtk
from gtk import gdk
import gobject

import math
import time

class LineDrawer(gtk.DrawingArea):
    def __init__(self):
        super(LineDrawer, self).__init__()
        self.connect("expose_event", self.expose)

        self.last_update = time.time()
        self.update()
        self.offset = 0
        gobject.timeout_add(10, self.update)

    def expose(self, widget, event):
        context = widget.window.cairo_create()

        # set a clip region for the expose event
        context.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
        context.clip()

        self.draw(context)

        return False

    def draw(self, context):
        rect = self.get_allocation()

        context.set_source_rgb(1.0,1.0,1.0)
        context.rectangle(0,0,rect.width,rect.height)
        context.fill()

        context.set_line_width(3.0)
        context.set_source_rgb(0,0,0)

        row_spacing = 4
        self.offset = (self.offset + 0.1) % row_spacing
        for row in range(rect.height / row_spacing):
            context.move_to(16,(row * row_spacing) + self.offset)
            context.line_to(rect.width - 16,(row * row_spacing) + (row_spacing + self.offset))
        context.stroke()

    def redraw_canvas(self):
        if self.window:
            alloc = self.get_allocation()
            rect = gdk.Rectangle(alloc.x, alloc.y, alloc.width, alloc.height)
            self.window.invalidate_rect(rect, True)
            self.window.process_updates(True)

    def update(self):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now
        print '%ffps' % (1/dt)

        self.redraw_canvas()
        return True # keep running this event

def main():
    window = gtk.Window()
    linedrawer = LineDrawer()

    window.add(linedrawer)
    window.connect("destroy", gtk.main_quit)
    window.show_all()

    gtk.main()

if __name__ == "__main__":
    main()
