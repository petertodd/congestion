// Copyright (c) 2009 Peter Todd
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include <world.h>
#include <network.data>

#define NODES_PER_ANT (5)
#define NUM_ANTS (NUM_NODES / NODES_PER_ANT)

struct ant ants[NUM_ANTS];

struct node *edge_idxs_node(struct edge_idx edge_idx){
    assert(edge_idx.e);
    assert(edge_idx.i < edge_idx.e->length);
    return &edge_idx.e->nodes[edge_idx.i];
}

void reverse_travel_direction(struct edge_idx edge){
    if (edge.e->travel_direction == 1){
        edge.e->travel_direction = -1;
    } else {
        edge.e->travel_direction = 1;
    }
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
    ant->cur_edge.e = NULL;
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

int move_ant_to_vertex_if_possible(struct ant *ant,struct vertex *vertex){
    assert(ant);
    assert(vertex);

    // Vertexes don't connect directly to vertexes
    assert(!ant->cur_vertex);

    if (!vertex->node->ant){
        remove_ant_from_edge(ant);
        add_ant_to_vertex(ant,vertex);
        return 1;
    } else {
        return 0;
    }
}

int move_ant_to_edge_if_possible(struct ant *ant,struct edge_idx edge){
    assert(ant);

    if (ant->cur_vertex){
        // Vertex to edge
        if (!edge_idxs_node(edge)->ant){
            remove_ant_from_vertex(ant);
            add_ant_to_edge(ant,edge);
            return 1;
        } else {
            return 0;
        }
    } else {
        // Edge to edge
        assert(ant->cur_edge.e == edge.e); // must be same edge, just a different index
        assert(abs(ant->cur_edge.i - edge.i) == 1); // moves must be exactly one node apart
        assert(edge.i >= 0 && edge.i < edge.e->length); // move is within bounds

        if (!edge_idxs_node(edge)->ant){
            edge_idxs_node(ant->cur_edge)->ant = NULL;
            edge_idxs_node(edge)->ant = ant;
            ant->cur_edge = edge;
            return 1;
        } else {
            return 0;
        }
    }
}

void init_world(){
    int i,j,k;
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

        // Do initialization while we're at it
        edges[i].travel_direction = random() % 2 ? 1 : -1;
        edges[i].ants_present = 0;
        for (j = 0; j < 2; j++){
            for (k = 0; k < NUM_GOALS; k++){
                edges[i].goal_dists[j][k] = MAX_GOAL_DIST;
            }
        }
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

void potentially_reverse_travel_direction(struct ant *ant,struct vertex *vertex){
    if (random() % 100 < 50){
        reverse_travel_direction(ant->cur_edge);
    }
}

void do_world(){
    int i,j;
    struct ant *ant;

    for (i = 0; i < NUM_ANTS; i++){
        ant = &ants[i];
        // Random chance the ant will do nothing
        if (random() % 100 < 25)
            continue;

        if (!ant->cur_vertex){
            struct edge_idx new_edge = ant->cur_edge;

            // The ant is on an edge, move along the edge.
            new_edge.i += new_edge.e->travel_direction;

            // Are we at the limit of travel?
            if (new_edge.i < 0){
                if (!move_ant_to_vertex_if_possible(ant,ant->cur_edge.e->start)){
                    // Blocked!
                    potentially_reverse_travel_direction(ant,ant->cur_edge.e->start);
                }
            } else if (new_edge.i >= ant->cur_edge.e->length){
                if (!move_ant_to_vertex_if_possible(ant,ant->cur_edge.e->end)){
                    // Blocked!
                    potentially_reverse_travel_direction(ant,ant->cur_edge.e->end);
                }
            } else {
                // Perform the move if possible
                if (!edge_idxs_node(new_edge)->ant){
                    edge_idxs_node(new_edge)->ant = ant;
                    edge_idxs_node(ant->cur_edge)->ant = NULL;
                    ant->cur_edge = new_edge;
                }
            }
        } else {
            // Ant is on a vertex node, choose a non-blocked edge to move to.
            //
            // First create a randomized try order, so as to not introduce
            // bias.
            assert(NUM_VERTEX_EDGES == 4);
            int try_order[] = {0,1,2,3};
            for (j = 0; j < NUM_VERTEX_EDGES; j++){
                int tmp = try_order[j];
                int k = random() % NUM_VERTEX_EDGES;
                try_order[j] = try_order[k];
                try_order[k] = tmp;
            }
            // And try the possibilities sequentially.
            for (j = 0; j < NUM_VERTEX_EDGES; j++){
                struct edge_idx candidate = ant->cur_vertex->edges[try_order[j]];
                if (candidate.e &&
                    ((candidate.i == 0 && candidate.e->travel_direction == 1) || candidate.e->travel_direction == -1) &&
                    move_ant_to_edge_if_possible(ant,candidate))
                    break;
            }
        }
    }
}
