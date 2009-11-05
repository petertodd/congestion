// Copyright (c) 2009 Peter Todd
#include <stdio.h>

#include <world.h>
#include <network.data>

void init_world(){
    int i,k;
    // The pointers in the network data tables are initialized as offsets from
    // the beginning, we need to go through them all and convert them into
    // proper absolute pointers.
    for (i = 0; i < NUM_EDGES; i++){
        edges[i].start = &vertexes[(long)edges[i].start];
        edges[i].end = &vertexes[(long)edges[i].end];
        edges[i].nodes = &nodes[(long)edges[i].nodes];
    }
    for (i = 0; i < NUM_VERTEXES; i++){
        vertexes[i].node = &nodes[(long)vertexes[i].node];
        for (k = 0; k < NUM_VERTEX_EDGES; k++){
            // Index is offset by one, so that 0 can represent NULL
            if (!vertexes[i].edges[k].e){
                vertexes[i].edges[k].e = NULL;
            } else {
                vertexes[i].edges[k].e = &edges[(long)vertexes[i].edges[k].e - 1];
            }
        }
    }
}

void do_world(){
}
