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

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

// see header file for description
void gps_init(char *ip, char *port)
{
    // assign the chosen ip address and port of Piksi
    tcp_ip_addr = ip;
    tcp_ip_port = port;

    // set descriptor, and call the setup function    
    socket_desc = -1;
    printf("about to set up socket\n");
    setup_socket();
    
    printf("about to state_init\n");
    sbp_state_init(&s);
    
    
    /* Register nodes and callbacks, 
     * and associate them with a specific message ID. */
    sbp_register_callback(&s, SBP_MSG_GPS_TIME, &sbp_gps_time_callback,
                        NULL, &gps_time_node);
    sbp_register_callback(&s, SBP_MSG_POS_LLH, &sbp_pos_llh_callback,
                        NULL, &pos_llh_node);
    sbp_register_callback(&s, SBP_MSG_BASELINE_NED, &sbp_baseline_ned_callback,
                        NULL, &baseline_ned_node);
    sbp_register_callback(&s, SBP_MSG_VEL_NED, &sbp_vel_ned_callback,
                        NULL, &vel_ned_node);
    sbp_register_callback(&s, SBP_MSG_DOPS, &sbp_dops_callback,
                        NULL, &dops_node);
    sbp_register_callback(&s, SBP_MSG_IMU_RAW, &sbp_imu_raw_callback,
                        NULL, &imu_raw_node);
                        
    printf("about to start thread\n"); 
    
    // start a thread which will keep updating location bitch         
    pthread_create(&gps_update_thread, NULL, gps_thread, NULL);
}
// see header file for description
void gps_finish()
{
  close_socket();
  free(tcp_ip_addr);
  free(tcp_ip_port);
  
  // end that thread, bitch
  pthread_join(gps_update_thread, NULL);
}
// see header file for description
void setup_socket()
{
  struct sockaddr_in server;
  printf("entered setup_socket\n");
  socket_desc = socket(AF_INET , SOCK_STREAM , 0);
  if (socket_desc == -1)
  {
    fprintf(stderr, "Could not create socket\n");
  }
  printf("passed if\n");
  memset(&server, '0', sizeof(server));
  printf("passed memset\n");
  server.sin_addr.s_addr = inet_addr(tcp_ip_addr);
  //server.sin_addr.s_addr = htonl(INADDR_ANY);
  printf("passed server thing\n");
  server.sin_family = AF_INET;
  printf("passed server.sin thing\n");
  server.sin_port = htons(atoi(tcp_ip_port));
  printf("about to enter second if\n");
  if (connect(socket_desc, (struct sockaddr *)&server , sizeof(server)) < 0)
  {
    fprintf(stderr, "Connection error\n");
  }
  printf("done\n");
}
// see header file for description
void close_socket()
{
  close(socket_desc);
}

// see header file for description
u32 socket_read(u8 *buff, u32 n, void *context)
{
  (void)context;
  u32 result;

  result = read(socket_desc, buff, n);
  return result;
}

// see header file for description
void *gps_thread()
{
    // sbp process (hence reading of GPS data) will need to loop FOREVER
    while(1)
    {
        // Use mutual exclusion to prevent bullshit
        pthread_mutex_lock(&mutex);
        sbp_process(&s, &socket_read);
        pthread_mutex_unlock(&mutex);
    }
}
// see header file for description
void sbp_pos_llh_callback(u16 sender_id, u8 len, u8 msg[], void *context)
{
  pos_llh = *(msg_pos_llh_t *)msg;
}
void sbp_baseline_ned_callback(u16 sender_id, u8 len, u8 msg[],
  void *context)
{
  baseline_ned = *(msg_baseline_ned_t *)msg;
}
void sbp_vel_ned_callback(u16 sender_id, u8 len, u8 msg[], void *context)
{
  vel_ned = *(msg_vel_ned_t *)msg;
}
void sbp_dops_callback(u16 sender_id, u8 len, u8 msg[], void *context)
{
  dops = *(msg_dops_t *)msg;
}
void sbp_gps_time_callback(u16 sender_id, u8 len, u8 msg[], void *context)
{
  gps_time = *(msg_gps_time_t *)msg;
}
void sbp_imu_raw_callback(u16 sender_id, u8 len, u8 msg[], void *context)
{
  imu_raw = *(msg_imu_raw_t *)msg;
}
