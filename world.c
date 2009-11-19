// Copyright (c) 2009 Peter Todd
#include <common.h>

#include <world.h>
#include <network.data>

#define NODES_PER_ANT (10)
#define NUM_ANTS 1 // (NUM_NODES / NODES_PER_ANT)

uint8_t ant_presence[(NUM_NODES / 8) + 1];
uint8_t ant_goals[(NUM_NODES / 8) + 1];

void init_world(){
    int i,k;

    printf("sizeof(ant_presence) = %ld sizeof(ant_goals) = %ld sizeof(vertex_rams) = %ld total = %ld\n",
            sizeof(ant_presence),sizeof(ant_goals),sizeof(vertex_rams),
            (sizeof(ant_presence) + sizeof(ant_goals) + sizeof(vertex_rams)));
}

void do_world(){
}
