// Copyright (c) 2009 Peter Todd
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include <world.h>
#include <network.data>

#define NODES_PER_ANT 3
#define NUM_ANTS (NUM_NODES / NODES_PER_ANT)

struct ant ants[NUM_ANTS];

struct node *edge_idxs_node(struct edge_idx edge_idx){
    assert(edge_idx.e);
    assert(edge_idx.i < edge_idx.e->length);
    return &edge_idx.e->nodes[edge_idx.i];
}

struct node *ants_node(struct ant *ant){
    assert((ant->cur_edge.e && !ant->cur_vertex) || (!ant->cur_edge.e && ant->cur_vertex));

    if (ant->cur_edge.e){
        return edge_idxs_node(ant->cur_edge);
    } else {
        return ant->cur_vertex->node;
    }
}

void remove_ant_from_edge(struct ant *ant){
    assert(ant->cur_edge.e);
    assert(!ant->cur_vertex);

    assert(ant->cur_edge.e->ants_present > 0);
    ant->cur_edge.e->ants_present--;

    ants_node(ant)->ant = NULL;
}

void add_ant_to_edge(struct ant *ant,struct edge_idx edge){
    assert(!ant->cur_edge.e);
    assert(!ant->cur_vertex);

    ant->cur_edge = edge;
    ant->cur_edge.e->ants_present++;
    assert(!ants_node(ant)->ant);
    ants_node(ant)->ant = ant;
}

void remove_ant_from_vertex(struct ant *ant){
    assert(!ant->cur_edge.e);
    assert(ant->cur_vertex);

    ants_node(ant)->ant = NULL;
    ant->cur_vertex = NULL;
}

void add_ant_to_vertex(struct ant *ant,struct vertex *vertex){
    assert(!ant->cur_edge.e);
    assert(!ant->cur_vertex);
    assert(vertex);

    ant->cur_vertex = vertex;
    assert(!ants_node(ant)->ant);
    ants_node(ant)->ant = ant;
}


void init_world(){
    int i,k;
    for (i = 0; i < NUM_NODES; i++){
        nodes[i].ant = NULL;
    }

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

    // Add the ants, evenly distributed amoung nodes that are part of edges.
    struct edge_idx e;
    assert(NUM_ANTS < NUM_NODES - NUM_VERTEXES);
    i = 0;
    k = 0;
    do {
        e.e = &edges[k];
        for (e.i = random() % ((NUM_NODES - NUM_VERTEXES) / NUM_ANTS); e.i < e.e->length; e.i += random() % ((NUM_NODES - NUM_VERTEXES) / NUM_ANTS)){
            if (!edge_idxs_node(e)->ant){
                ants[i].cur_vertex = NULL;

                // FIXME: add ant goal initialization

                add_ant_to_edge(&ants[i],e);
                i++;
                break;
            }
        }
        k++;
        if (k >= NUM_EDGES)
            k = 0;
    } while (i < NUM_ANTS);
}

void do_world(){
}
