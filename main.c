// Copyright (c) 2009 Peter Todd

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <data_structures.h>

#include <allegro.h>

#define SCREEN_WIDTH 500
#define SCREEN_HEIGHT 500

int main(int argc,char *argv[]){
    allegro_init();
    install_keyboard();

    set_gfx_mode(GFX_AUTODETECT_WINDOWED, 500, 500, 0, 0);

    clear_to_color(screen,makecol(0,0,0));
    acquire_screen();

    //Wait for a key to be pressed
    release_screen();
    while (!keypressed()) {}

    return 0;
    //Allegro will automatically deinitalize itself on exit
}
