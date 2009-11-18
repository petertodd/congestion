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

#define get_bit(a,n) \
    ({ typeof (n) _n = (n); \
       ((a)[_n / 8] >> _n) & (1 << _n) >> _n; })

#endif
