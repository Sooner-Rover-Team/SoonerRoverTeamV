%module gpsmain
%{
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <unistd.h>
    #include <arpa/inet.h>
    #include <sys/socket.h>
    #include <pthread.h>
    #include "system.h"
    #include "navigation.h"
    #include "sbp.h"
    #include "gps.h"
    extern int gpsmain();
%}
extern int gpsmain();
 %inline %{
	
    //float latitude = 0.0; //pos_llh.lat;
    //float longitude = 0.0; //pos_llh.lon;
    //unsigned long error = 0;  
%}

/*%init %{
%} */
