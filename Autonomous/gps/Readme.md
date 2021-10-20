# GPS stuff

Gonna keep this updated as a working log of what I'm doing in the gps folder

---

## Current build and run instructions

If SWIG is not installed, install it and python3 dev tools with

```bash
sudo apt install swig python3-dev gcc
```

### Overview

Process:

1. wrap edc.c into a library
2. use edc.c to wrap sbc.c into a library
3. use sbc.c to wrap gps.c into a library
4. Then use gps.c library to wrap main.c or main.cpp

### Automatic Wrapping Instructions

Run

```bash
make all
```

### Manual Rewrapping instructions

#### edc.c

```bash
swig -python edc.i
gcc -fpic -c -I/usr/include/python3.8 edc.c edc_wrap.c
gcc -shared edc.o edc_wrap.o -o _edc.so
```

#### sbp.c

```bash
swig -python sbp.i
gcc -fpic -c -I/usr/include/python3.8 sbp.c sbp_wrap.c
gcc -shared sbp.o sbp_wrap.o -o _sbp.so edc.o 
```

#### gps.c

```bash
swig -python gps.i
gcc -fpic -c -I/usr/include/python3.8 gps.c gps_wrap.c
gcc -shared gps.o gps_wrap.o -o _gps.so sbp.o edc.o
```

#### main.c

```bash
swig -python main.i
gcc -fpic -c -I/usr/include/python3.8 main.c main_wrap.c
gcc -shared main.o main_wrap.o -o _gpsmain.so gps.o sbp.o edc.o
```

---

## Todo List

- [x] Copy gps code over
- [x] Figure out what is necessary to running the code and what can be disposed of (bye bye cpp and hpp files)
- [x] Write a main function that can call gps methods just to see if the damn thing even works
- [x] Get it all to at least build correctly
- [x] Figure out how to wrap the gps code and turn it into a python module
- [x] See if that module can be imported into another python script and the correct information from the Swift can be accesssed
- [ ] See if it will actually communicate with the Swift
