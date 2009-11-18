// Copyright (c) 2009 Peter Todd
#include <common.h>

#include <world.h>
#include <network.data>

#define NODES_PER_ANT (10)
#define NUM_ANTS (NUM_NODES / NODES_PER_ANT)

struct ant ants[NUM_ANTS];

void init_world(){
    int i,k;

    printf("sizeof(nodes) = %ld sizeof(ants) = %ld total = %ld\n",
            sizeof(nodes),sizeof(ants),
            sizeof(nodes) + sizeof(ants));

    for (i = 0; i < NUM_NODES; i++){
        nodes[i].ant = INVALID_ANT_IDX;
    }

    // Add the ants, evenly distributed amoung the nodes
    assert(NUM_ANTS < NUM_NODES);
    i = 0;
    do {
        // This is acceptably efficient as the number of ants will never be a
        // significant fraction of the number of nodes.
        k = random() % NUM_NODES;
        if (nodes[k].ant == INVALID_ANT_IDX){
            nodes[k].ant = i;
            ants[i].node = k;
            ants[i].goal = random() % NUM_GOALS;
            ants[i].time_taken = 0;
            i++;
        }
    } while (i < NUM_ANTS);
}

void do_world(){
    int i;
    struct ant *ant;

    for (i = 0; i < NUM_ANTS; i++){
        ant = &ants[i];
        // Random chance the ant will do nothing
        if (random() % 100 < 25)
            continue;
    }
}
