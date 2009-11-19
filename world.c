// Copyright (c) 2009 Peter Todd
#include <common.h>

#include <world.h>
#include <network.data>

#define NODES_PER_ANT (10)
#define NUM_ANTS (NUM_NODES / NODES_PER_ANT)

uint8_t ant_presence[(NUM_NODES / 8) + 1];
uint8_t ant_goals[(NUM_NODES / 8) + 1];

void init_world(){
    int i,k;

    printf("sizeof(ant_presence) = %ld sizeof(ant_goals) = %ld sizeof(vertex_rams) = %ld total = %ld\n",
            sizeof(ant_presence),sizeof(ant_goals),sizeof(vertex_rams),
            (sizeof(ant_presence) + sizeof(ant_goals) + sizeof(vertex_rams)));

    // Add the ants, evenly distributed amoung the nodes.
    i = 0;
    assert(NUM_ANTS < NUM_NODES - NUM_VERTEXES);
    do {
        k = random() % NUM_NODES;
        if (!ant_on_node(k)){
            set_ant_on_node(k,1);
            assert(ant_on_node(k));
            i++;
        };
    } while (i < NUM_ANTS);

    // Randomize goals
    //
    // This is even easier, as a goal is only valid if a corresponding
    // ant_presence bit is set, so basically we can just fill the whole array
    // with random data.
    for (i = 0; i < NUM_NODES / 8; i++){
        ant_goals[i] = random();
    }
}

void do_world(){
}
