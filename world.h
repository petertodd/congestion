// Copyright (c) 2009 Peter Todd

#ifndef WORLD_H
#define WORLD_H

#include <stdint.h>

#include <network.defs>

// All data structures are split into the parts that can go in ROM, and the
// parts that can go in RAM.

// Bit field of ant presence, IE, is an ant on an led?
//
// Doubles as the led table in essence.
extern uint8_t ant_presence[(NUM_NODES / 8) + 1];

#define ant_on_node(n) (get_bit(ant_presence,n))

// The goals of the ants. Note that a given goal bit may not actually
// correspond to a valid ant if the corresponding ant_presence bit isn't set.
extern uint8_t ant_goals[(NUM_NODES / 8) + 1];

#define ants_goal_on_node(n) (get_bit(ant_goals,n))

struct vertex_rom {
    uint16_t led;
    struct {
        unsigned int valid : 1;
        // Start and end leds
        unsigned int start : 15;
        unsigned int end : 16;

        // The vertex at the other end of the edge, may be ourselves.
        uint16_t vertex;

        // Relative dists from either goal if an ant starts going down the edge
        // to the given neighbor. By relative, we mean the neighbor with the
        // lowest distance will be zero. Maxes out at 256 of course.
        //
        // Note that this has to be the distance you'd be from the goal at the
        // vertex at the other end of the edge, not the start node. If the
        // latter is measured, all distances are different by exactly 0 or 2...
        uint8_t goal_dists[2];
    } neighbors[4];
} __attribute__ ((__packed__));
extern const struct vertex_rom vertex_roms[NUM_VERTEXES];

struct vertex_ram {
    uint16_t next_node[2];
    uint8_t edge_dirs[4];
};
extern struct vertex_ram vertex_rams[NUM_VERTEXES];


void init_world();

void do_world();

#endif
