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
    if (node->ant){
        ellipsefill(screen,node->x * SCALE,node->y * SCALE,LED_WIDTH / 2 - 1,LED_WIDTH / 2 - 1,LED_COLOR_ON);
    } else {
        ellipsefill(screen,node->x * SCALE,node->y * SCALE,LED_WIDTH / 2 - 1,LED_WIDTH / 2 - 1,LED_COLOR_OFF);
    }
}

void do_display(){
    int i,j;
    // Draw nodes owned by edges
    for (i = 0; i < NUM_EDGES; i++){
        for (j = 0; j < edges[i].length; j++){
            draw_node(&edges[i].nodes[j]);
        }
    }

    // Draw nodes owned by vertexes
    for (i = 0; i < NUM_VERTEXES; i++){
       draw_node(vertexes[i].node);
    }
}
