// Copyright (c) 2009 Peter Todd

#ifndef WORLD_H
#define WORLD_H

#include <stdint.h>


// Goals. Using just two goals right now, simple and clean, and good for a
// horizontal presentaiton.
#define NUM_GOALS 2
typedef enum {
    Light = 0,
    Dark = 1
} goal_t;

typedef uint16_t goal_dist_t;
typedef uint16_t node_idx_t;
typedef uint16_t ant_idx_t;
#define INVALID_ANT_IDX (65535)

#include <network.defs>

struct ant {
    node_idx_t node;

    // Current goal
    goal_t goal;

    // How long it has taken since we started going to our current goal.
    uint16_t time_taken;
};
extern struct ant ants[];


// An individual led that an ant may be on. Only one ant may be present on a
// node at any time.
//
// The nodes really refers to which led we want to light up, so "x" and "y"
// could be something like chip select and index, especially given that 256 led
// controllers are available.
struct node {
    // Fixed data
    uint16_t x;
    uint16_t y;

    // Neighboring nodes
    node_idx_t neighbors[MAX_NODE_NEIGHBORS];

    int16_t goal_dists[NUM_GOALS];

    // Volatile data
    ant_idx_t ant;

    int16_t frustration[NUM_GOALS];
};
extern struct node nodes[];

void init_world();

void do_world();

#endif
