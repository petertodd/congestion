# Copyright (C) 2009 Peter Todd <pete@petertodd.org>

# Makefile for 18F1320 compilation w/ SDCC.

ALLEGRO_LDFLAGS=$(shell allegro-config --libs)

CC=gcc
INCLUDE=-I.
CFLAGS=$(INCLUDE) $(SDL_CFLAGS) -g -Wall

ODIR=obj

LIBS=-lm $(ALLEGRO_LDFLAGS)

SRCS=main.c display.c world.c

_OBJS =${SRCS:%.c=%.o}
OBJS = $(patsubst %,$(ODIR)/%,$(_OBJS))

all: thesis

$(ODIR)/%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS)

world.h: network.defs
network.data: network.defs
network.defs: gen_network.py network.png
	./gen_network.py network.png network.defs network.data 0

thesis: $(OBJS)
	gcc -o $@ $^ $(CFLAGS) $(LIBS)

depend: ${SRCS}
	makedepend -pobj/ -f.depend ${INCLUDE} *.c 

include .depend

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(INCDIR)/*~ network.defs network.data
