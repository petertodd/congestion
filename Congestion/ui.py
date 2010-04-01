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

        gobject.timeout_add(dt * 1000, self.do_sim)

    def expose(self, widget, event):
        context = widget.window.cairo_create()

        # Restrict Cairo to the exposed area; avoid extra work
        context.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
        context.clip()

        self.draw(context)

    def do_sim(self):
        print 'do_sim'
        self.world.do(self.dt)
        self.redraw_canvas()

        return True

    def redraw_canvas(self):
        if self.window:
            alloc = self.get_allocation()
            rect = gtk.gdk.Rectangle(alloc.x,alloc.y,alloc.width,alloc.height)
            self.window.invalidate_rect(rect,True)
            self.window.process_updates(True)

    def draw(self, context):
        rect = self.get_allocation()
        now = time.time()
        print 'draw',rect,now - self.last
        self.last = now

        # Fill the background with white
        context.set_source_rgb(0.0, 0.0, 0.0)
        context.rectangle(0, 0, rect.width, rect.height)
        context.fill()
        context.set_line_width(1.50)
        print context

        def line(a,b,color,width=1.0):
            context.save()
            context.set_line_width(width * context.get_line_width())
            context.set_source_rgb(*color)
            context.move_to(a[0],a[1])
            context.line_to(b[0],b[1])
            context.stroke()
            context.restore()

        # Display the world

        if False:
            for n in self.world.nodes: 
                x,y = n.pos
                c = (100,100,100)
                size = 2
                if n.occupying is not None:
                    c = (255,0,0)
                #pygame.draw.circle(self.screen,c,ip((x + 1,y + 1)),size)

        all_rails = []
        for track in self.world.tracks:
            #line(track.a.pos,track.b.pos,(0.3,0.3,0.4))
            #pygame.draw.aaline(self.screen,(30,30,40),ip(track.a.pos),ip(track.b.pos))
            all_rails.extend(track.left_rails)
            all_rails.extend(track.right_rails)

        for intersection in self.world.intersections:
            all_rails.extend(intersection.rails)

        for rail in all_rails:
            line(rail.a.pos,rail.b.pos,(0.2,0.2,0.3))
            pass
            #pygame.draw.aaline(self.screen,(50,50,60),ip(rail.a.pos),ip(rail.b.pos))

        # draw the trains on the track
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
                buffer_end = pos_to_v(min(rail.length,max(0,p + t.l + t.b)))

                if train_start != train_end:
                    line(train_start,train_end,(1.0,0.0,0.0),width=2.0)
                    #pygame.draw.aaline(self.screen,(255,0,0),ip(train_start),ip(train_end))
                #line(train_end,buffer_end,(0.0,0.0,1.0))
                #pygame.draw.aaline(self.screen,(0,0,255),ip(train_end),ip(buffer_end))

        # where the mouse is, equivilent to node id
        #pos = pygame.mouse.get_pos()
        #pygame.event.clear()

        #font = pygame.font.Font(None, 12)
        #text = font.render(str(pos), 1, (10, 10, 10))
        #self.screen.blit(text,(1,1,0,0))
        
        #pygame.display.flip()


def run_ui(world,dt):
    window = gtk.Window()
    ui = UserInterface(world,dt)

    window.add(ui)
    window.connect("destroy", gtk.main_quit)
    window.show_all()

    gtk.main()
