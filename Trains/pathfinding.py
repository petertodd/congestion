# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# ### BOILERPLATE ###
# Trains - train network thingy
# Copyright (C) 2007 Peter Todd <pete@petertodd.org>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ### BOILERPLATE ###

"""Pathfinding for trains."""

from sys import maxint

def calc_cost(t):
    """Returns the cost to traverse track t"""
    return t.length

def pathfind(net,start,end):
    """Find the shortest path from start to end.

       Returns the next best track to follow from start
    """
    assert(start != end)

    dist = {}
    prev = {}
    for n in net.nodes:
        dist[n] = maxint
        prev[n] = None
    dist[start] = 0
    
    q = [start]
    for n in q:
        for t in n.exits:
 #           print 'eval exit ' + str(x.b) + ' from ' + str(t.b)
            alt = dist[n] + calc_cost(t)
#            print 'alt = ' + str(alt) + ' dist[x] = ' + str(dist[x])
            if alt < dist[t.b]:
                dist[t.b] = alt
                prev[t.b] = n
                q.append(t.b)

    # Walk prev backwards to get our best solution
    i = end
    print str(end)
    print str(prev)
    while prev[i] != start:
        i = prev[i]

    # i is a node, we need to return a track
    for t in start.exits:
        if t.b == i:
            return t
    assert(False)
