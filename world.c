// Copyright (c) 2009 Peter Todd
#include <common.h>

#include <world.h>
#include <network.data>

#define NODES_PER_ANT (10)
#define NUM_ANTS 1 // (NUM_NODES / NODES_PER_ANT)

struct ant ants[NUM_ANTS];

node_idx_t node_neighbor(node_idx_t n,int i){
    return nodes[n].neighbors[i];
}

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
    int ant_idx,n;
    struct ant *ant;
    struct node *node;

    for (ant_idx = 0; ant_idx < NUM_ANTS; ant_idx++){
        ant = &ants[ant_idx];
        // Random chance the ant will do nothing
        if (random() % 100 < 25)
            continue;

        ant->time_taken++;

        // Build the cost table for the possible moves
        int costs[MAX_NODE_NEIGHBORS];
        int num_node_neighbors;
        for (n = 0; n < MAX_NODE_NEIGHBORS; n++){
            if (node_neighbor(ant->node,n) == INVALID_NODE_IDX){
                num_node_neighbors = n;
                break;
            } else {
                costs[n] = nodes[node_neighbor(ant->node,n)].goal_dists[ant->goal] +
                           nodes[node_neighbor(ant->node,n)].frustration[ant->goal];
            }
        }

        // Find the lowest cost node
        int lowest_cost = 65535; // FIXME: should be max int or whatever that constant is
        node_idx_t new_node = INVALID_NODE_IDX;
        for (n = 0; n < num_node_neighbors; n++){
            if (costs[n] < lowest_cost){
                lowest_cost = costs[n];
                new_node = node_neighbor(ant->node,n);
            }
        }
        assert(new_node != INVALID_NODE_IDX);

        // Attempt to move to it. Note that the lowest cost node may have an
        // ant on it, in which case we are blocked.
        if (nodes[new_node].ant == INVALID_ANT_IDX){
            nodes[new_node].ant = ant_idx;
            nodes[ant->node].ant = INVALID_ANT_IDX;
            ant->node = new_node;

            // Did we reach the objective?
            if (nodes[ant->node].goal_dists[ant->goal] == 0){
                // New goal
                ant->goal = ant->goal == Light ? Dark : Light;
            }
        }
    }
}
