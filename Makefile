# Copyright (C) 2009 Peter Todd <pete@petertodd.org>

# Makefile for 18F1320 compilation w/ SDCC.

ALLEGRO_LDFLAGS=$(shell allegro-config --libs)

CC=gcc
CFLAGS=-I. $(SDL_CFLAGS)

ODIR=obj

LIBS=-lm $(ALLEGRO_LDFLAGS)

_OBJ = main.o display.o world.o
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))


$(ODIR)/%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS)

thesis: $(OBJ)
	gcc -o $@ $^ $(CFLAGS) $(LIBS)

depend: ${SRCS}
	makedepend -f.depend -D$(PROCESSOR) ${INCLUDE} *.c 

include .depend

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(INCDIR)/*~ 
