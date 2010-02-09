# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
#
# Trains - train network thingy
# Copyright (C) 2010 Peter Todd <pete@petertodd.org>

"""Train class and related logic."""

from collections import deque

class Train:
    v = 10.0 # current velocity, m/s
    b = 0.0 # current buffer distance, m

    # intrinsic characteristics
    l = 10.0 # length, m
    m = 100.0 # mass, kg
    df = 10.0 # driving force, newtons
    bf = 50.0 # braking force, newtons
    cd = 1.0 # drag coefficient, unitless, Fd = v^2 * cd

    # Safety margin for the buffer, m
    buffer_safety_margin = 10

    def __init__(self,net,location,**kwargs):
        self.net = net

        self.occupying = deque((location,))
        location.add_train(self,10)

    def do_extend_buffers(self,dt):
        pass

    def do_move(self,dt):
        pass
