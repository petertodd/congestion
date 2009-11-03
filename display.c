// Copyright (c) 2009 Peter Todd

#include <allegro.h>
#include <world.h>

void init_display(){
    allegro_init();
    install_keyboard();

    set_gfx_mode(GFX_AUTODETECT_WINDOWED, 500, 500, 0, 0);

    clear_to_color(screen,makecol(0,0,0));
}

void do_display(){

}
