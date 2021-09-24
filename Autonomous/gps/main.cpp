#include "lib/gps.h"
#include "position.h"
#include <iostream>
#include <string>

int main() {
    std::string swift_ip = "127.0.0.1";
    std::string swift_port = "55556";
    char* ip = &swift_ip[0];
    char* port = &swift_port[0];
    gps_init(ip, port);
    // while (1)
    // {
    //     longitude = pos_llh.lat;
    //     printf("longitude: %f",longitude);
    // }
    
}