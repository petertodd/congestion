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

void draw_node(int node,int color){
    ellipsefill(buffer,node_idx_to_xy[node].x * SCALE,node_idx_to_xy[node].y * SCALE,LED_WIDTH / 2 - 1,LED_WIDTH / 2 - 1,color);
}

void do_display(){
    int i,color;
    static enum {
        DEFAULT,
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
            case 'g':
                display_mode = GOALS;
                break;
        }
    }


    // Draw nodes
    for (i = 0; i < NUM_NODES; i++){
        switch (display_mode) {
            case GOALS:
                color = makecol((double)goal_dists[i][0] / (double)max_goal_dist_in_network[0] * 128.0,0,
                                (double)goal_dists[i][1] / (double)max_goal_dist_in_network[1] * 128.0);
                break;
            default:
                color = LED_COLOR_OFF;
        };

        // Ants always show up
        if (ant_on_node(i)){
            if (display_mode == GOALS){
                color = ants_goal_on_node(i) ? makecol(200,0,0) : makecol(0,0,250);
            } else {
                color = LED_COLOR_ON;
            }
        }

        draw_node(i,color);
    }

    blit(buffer, screen, 0, 0, 0, 0, WORLD_WIDTH * LED_WIDTH, WORLD_HEIGHT * LED_WIDTH);
}
