%module gps
%{
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <unistd.h>
    #include <arpa/inet.h>
    #include <sys/socket.h>
    #include <pthread.h>
    #include "sbp.h"
    #include "system.h"
    #include "navigation.h"
    #include "gps.h"
    extern msg_pos_llh_t      pos_llh;
    extern msg_baseline_ned_t baseline_ned;
    extern msg_vel_ned_t      vel_ned;
    extern msg_dops_t         dops;
    extern msg_gps_time_t     gps_time; 
    extern msg_imu_raw_t      imu_raw;
    extern pthread_mutex_t mutex;
    extern void gps_init(char *ip, char *port);
    extern void gps_finish();
    extern void setup_socket(); 
    extern void close_socket();
    extern u32 socket_read(u8 *buff, u32 n, void *context);
    extern void *gps_thread();
    extern void sbp_pos_llh_callback(u16 sender_id, u8 len, u8 msg[], void *context);

    extern void sbp_baseline_ned_callback(u16 sender_id, u8 len, u8 msg[],
        void *context);
    extern void sbp_vel_ned_callback(u16 sender_id, u8 len, u8 msg[], void *context);
    extern void sbp_dops_callback(u16 sender_id, u8 len, u8 msg[], void *context);
    extern void sbp_gps_time_callback(u16 sender_id, u8 len, u8 msg[], void *context);
    extern void sbp_imu_raw_callback(u16 sender_id, u8 len, u8 msg[], void *context);
%}
extern pthread_mutex_t mutex;
extern void gps_init(char *ip, char *port);
extern void gps_finish();
extern void setup_socket(); 
extern void close_socket();
extern u32 socket_read(u8 *buff, u32 n, void *context);
extern void *gps_thread();
extern void sbp_pos_llh_callback(u16 sender_id, u8 len, u8 msg[], void *context);
extern void sbp_baseline_ned_callback(u16 sender_id, u8 len, u8 msg[],
    void *context);
extern void sbp_vel_ned_callback(u16 sender_id, u8 len, u8 msg[], void *context);
extern void sbp_dops_callback(u16 sender_id, u8 len, u8 msg[], void *context);
extern void sbp_gps_time_callback(u16 sender_id, u8 len, u8 msg[], void *context);
extern void sbp_imu_raw_callback(u16 sender_id, u8 len, u8 msg[], void *context);
extern msg_pos_llh_t      pos_llh;
extern msg_baseline_ned_t baseline_ned;
extern msg_vel_ned_t      vel_ned;
extern msg_dops_t         dops;
extern msg_gps_time_t     gps_time; 
extern msg_imu_raw_t      imu_raw;