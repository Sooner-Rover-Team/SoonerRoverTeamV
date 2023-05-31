PYTHON_VERSION = 3.6

all: edc sbp gps gpsmain

edc:
	swig -python edc.i
	gcc -fpic -c -I/usr/include/python$(PYTHON_VERSION) edc.c edc_wrap.c
	gcc -shared edc.o edc_wrap.o -o _edc.so

sbp:
	swig -python sbp.i
	gcc -fpic -c -I/usr/include/python$(PYTHON_VERSION) sbp.c sbp_wrap.c
	gcc -shared sbp.o sbp_wrap.o -o _sbp.so edc.o 

gps:
	swig -python gps.i
	gcc -fpic -c -I/usr/include/python$(PYTHON_VERSION) gps.c gps_wrap.c
	gcc -shared gps.o gps_wrap.o -o _gps.so edc.o sbp.o

gpsmain:
	swig -python main.i
	gcc -fpic -c -I/usr/include/python$(PYTHON_VERSION) main.c main_wrap.c
	gcc -shared main.o main_wrap.o -o _gpsmain.so gps.o sbp.o edc.o

clean:
	rm *.o
	rm *.so
	rm *_wrap.c
	rm sbp.py
	rm gps.py
	rm gpsmain.py
	rm edc.py
