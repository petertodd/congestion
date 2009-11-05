// Copyright (c) 2009 Peter Todd

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <world.h>
#include <display.h>

int main(int argc,char *argv[]){
    init_world();
    init_display();

    while (1){
        do_world();
        do_display();

        usleep(1000);
    }
}
