#include "gps.h"
#include <iostream>
#include <stdio.h>

int main()
{
    char **ip = (char**)"192.168.1.123";
    char **host = (char**)"555555";
    std::cout << "About to init\n";
    gps_init(ip, host);
        // temporary print statements for the sake of testing
          
        /* Print GPS time. */
        printf("GPS Time:\n");
        printf("\tWeek\t\t: %6d\n", (int)gps_time.wn);
        printf("%6.2f", ((float)gps_time.tow)/1e3);
        printf("\n\n\n");

        /* Print absolute position. */
        printf("Absolute Position:\n");
        printf("%4.10lf", pos_llh.lat);
        printf("%4.10lf", pos_llh.lon);
        printf("%4.10lf", pos_llh.height);
        printf("\tSatellites\t:     %02d\n", pos_llh.n_sats);
        printf("\n\n\n");

        /* Print NED (North/East/Down) baseline (position vector from base to rover). */
        printf("Baseline (mm):\n");
        printf("\tNorth\t\t: %6d\n", (int)baseline_ned.n);
        printf("\tEast\t\t: %6d\n", (int)baseline_ned.e);
        printf("\tDown\t\t: %6d\n", (int)baseline_ned.d);
        printf("\n\n\n");

        /* Print NED velocity. */
        printf("Velocity (mm/s):\n");
        printf("\tNorth\t\t: %6d\n", (int)vel_ned.n);
        printf("\tEast\t\t: %6d\n", (int)vel_ned.e);
        printf("\tDown\t\t: %6d\n", (int)vel_ned.d);
        printf("\n\n\n");
    gps_finish();
}
