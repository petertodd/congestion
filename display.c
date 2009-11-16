// Copyright (c) 2009 Peter Todd

#include <common.h>
#include <allegro.h>
#include <world.h>

#define LED_WIDTH (6)
#define SCALE (6)

int LED_COLOR_ON;
int LED_COLOR_OFF;

BITMAP *buffer;

void init_display(){
    allegro_init();
    install_keyboard();

    set_color_depth(32);
    set_gfx_mode(GFX_AUTODETECT_WINDOWED, WORLD_WIDTH * LED_WIDTH, WORLD_HEIGHT * LED_WIDTH, 0, 0);

    buffer = create_bitmap(WORLD_WIDTH * LED_WIDTH, WORLD_HEIGHT * LED_WIDTH);

    clear_to_color(screen,makecol(0,0,0));
    clear_to_color(buffer,makecol(0,0,0));

    LED_COLOR_ON = makecol(200,0,0);
    LED_COLOR_OFF = makecol(30,30,30);
}

void draw_node(struct node *node,int color){
    ellipsefill(buffer,node->x * SCALE,node->y * SCALE,LED_WIDTH / 2 - 1,LED_WIDTH / 2 - 1,color);
}

void do_display(){
    int i,j,color;
    static enum {
        DEFAULT,
        TRAVEL_DIRECTIONS,
        GOALS
    } display_mode = DEFAULT;

    if (keypressed()){
        int key = 0xff & readkey();
        switch (key) {
            case 'q':
                exit(0);
            case 'd':
                display_mode = DEFAULT;
                break;
            case 't':
                display_mode = TRAVEL_DIRECTIONS;
                break;
            case 'g':
                display_mode = GOALS;
                break;
        }
    }


    // Draw nodes owned by edges
    for (i = 0; i < NUM_EDGES; i++){
        for (j = 0; j < edges[i].length; j++){
            switch (display_mode) {
                case TRAVEL_DIRECTIONS:
                    if (edges[i].travel_direction == 1){
                        color = (50.0 / edges[i].length) * j;
                    } else {
                        color = 50 - ((50.0 / edges[i].length) * j);
                    }
                    color += 30;
                    color = makecol(color,color,color);
                    break;
                case GOALS:
                    color = makecol((double)edges[i].nodes[j].goal_dists[0] / (double)MAX_GOAL_DIST_IN_NETWORK * 128.0,0,
                                    (double)edges[i].nodes[j].goal_dists[1] / (double)MAX_GOAL_DIST_IN_NETWORK * 128.0);
                    break;
                default:
                    color = LED_COLOR_OFF;
            };

            // Ants always show up
            if (edges[i].nodes[j].ant){
                if (display_mode == GOALS){
                    color = edges[i].nodes[j].ant->goal ? makecol(200,0,0) : makecol(0,0,250);
                } else {
                    color = LED_COLOR_ON;
                }
            }

            draw_node(&edges[i].nodes[j],color);
        }
    }

    // Draw nodes owned by vertexes
    for (i = 0; i < NUM_VERTEXES; i++){
        if (vertexes[i].node->ant){
            if (display_mode == GOALS){
                color = vertexes[i].node->ant->goal ? makecol(200,0,0) : makecol(0,0,250);
            } else {
                color = LED_COLOR_ON;
            }
        } else {
            color = LED_COLOR_OFF;
        }
        draw_node(vertexes[i].node,color);
    }

    blit(buffer, screen, 0, 0, 0, 0, WORLD_WIDTH * LED_WIDTH, WORLD_HEIGHT * LED_WIDTH);
}
