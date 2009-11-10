// Copyright (c) 2009 Peter Todd
#ifndef COMMON_H
#define COMMON_H

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#define max(a,b) \
    ({ typeof (a) _a = (a); \
       typeof (b) _b = (b); \
       _a > _b ? a : b; })

#define min(a,b) \
    ({ typeof (a) _a = (a); \
       typeof (b) _b = (b); \
       _a < _b ? a : b; })

#endif
