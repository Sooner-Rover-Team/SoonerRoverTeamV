#ifndef POSITION_H
#define POSITION_H
    
//Current latitude of the Rover
float latitude = 0.0;

//Current longitude of the Rover
float longitude = 0.0;

//Current height of the Rover
float height = 0.0;

//average of horizontal and vertical accuracies defined in msg_pos_llh_t in navigation.h
unsigned long error = 0;

//Current bearing of the rover: -180 south to -90 west to 180 south
float bearing = 0.0;

#endif