// Copyright (c) 2009 Peter Todd

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

#include <world.h>
#include <display.h>

int main(int argc,char *argv[]){
    srandom(time(NULL));

    init_world();
    init_display();

    while (!(keypressed())){
        do_world();
        do_display();

        usleep(50000);
    }
}
