// Copyright (c) 2009 Peter Todd

#include <stdio.h>
#include <allegro.h>
#include <world.h>

#define LED_WIDTH (6)
#define SCALE (6)

int LED_COLOR_ON;
int LED_COLOR_OFF;

void init_display(){
    allegro_init();
    install_keyboard();

    set_gfx_mode(GFX_AUTODETECT_WINDOWED, WORLD_WIDTH * LED_WIDTH, WORLD_HEIGHT * LED_WIDTH, 0, 0);

    clear_to_color(screen,makecol(0,0,0));

    LED_COLOR_ON = makecol(200,0,0);
    LED_COLOR_OFF = makecol(80,80,80);
}

void draw_node(struct node *node){
    ellipsefill(screen,node->x * SCALE,node->y * SCALE,LED_WIDTH / 2 - 1,LED_WIDTH / 2 - 1,LED_COLOR_OFF);
}

void do_display(){
    int i,j;
    struct node *last_node = NULL,*node;
    // Draw nodes owned by edges
    for (i = 0; i < NUM_EDGES; i++){
        last_node = NULL;
        for (j = 0; j < edges[i].length; j++){
            node = &edges[i].nodes[j];

            draw_node(node);
            if (last_node){
                line(screen,node->x * SCALE,node->y * SCALE,last_node->x * SCALE,last_node->y * SCALE,LED_COLOR_ON);
            }

            last_node = node;
        }
    }

    // Draw nodes owned by vertexes
    for (i = 0; i < NUM_VERTEXES; i++){
       // draw_node(vertexes[i].node);
        node = vertexes[i].node;
        ellipsefill(screen,node->x * SCALE,node->y * SCALE,LED_WIDTH / 2 - 1,LED_WIDTH / 2 - 1,LED_COLOR_ON);
        for (j = 0; j < MAX_VERTEX_NEIGHBORS; j++){
            if (vertexes[i].edges[j].e){
                line(screen,vertexes[i].node->x * SCALE,vertexes[i].node->y * SCALE,
                        vertexes[i].edges[j].e->nodes[vertexes[i].edges[j].i].x * SCALE,
                        vertexes[i].edges[j].e->nodes[vertexes[i].edges[j].i].y * SCALE,
                        LED_COLOR_OFF);
            }
        }
    }
}
