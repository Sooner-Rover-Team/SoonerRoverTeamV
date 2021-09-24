#include "gps2.hpp"



GPS::GPS(char **ip, char **port)
{
    tcp_ip_addr = *ip;
    tcp_ip_port = *port;
    
    // set descriptor, and call the setup function    
    socket_desc = -1;
    setup_socket();
    
    sbp_state_init(&s);
    
    /* Register a node and callback, 
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
            
    // start a thread which will keep updating location            
    std::thread thr(thread_task);
}
GPS::~GPS()
{
  close_socket();
  free(tcp_ip_addr);
  free(tcp_ip_port);
}

void GPS::setup_socket()
{
  struct sockaddr_in server;
  socket_desc = socket(AF_INET , SOCK_STREAM , 0);
  if (socket_desc == -1)
  {
    fprintf(stderr, "Could not create socket\n");
  }
  
  memset(&server, '0', sizeof(server));
  server.sin_addr.s_addr = inet_addr(tcp_ip_addr);
  server.sin_family = AF_INET;
  server.sin_port = htons(atoi(tcp_ip_port));

  if (connect(socket_desc, (struct sockaddr *)&server , sizeof(server)) < 0)
  {
    fprintf(stderr, "Connection error\n");
  }
}
void GPS::close_socket()
{
  close(socket_desc);
}

u32 GPS::socket_read(u8 *buff, u32 n, void *context)
{
  (void)context;
  u32 result;

  result = read(socket_desc, buff, n);
  return result;
}

void GPS::thread_task()
{
    // sbp process and reading of location will need to loop
    
    while(1)
    {
        sbp_process(&s, &socket_read);
        abs_location.resize(4);
        abs_location[0] = pos_llh.lat;
        abs_location[1] = pos_llh.lon;
        abs_location[2] = pos_llh.height;
        abs_location[3] = pos_llh.n_sats;
    }
    
}
/* Callback functions. References to these functions are passed
* as one of the arguments in the sbp_register_callback() function.
* As far as I know, that is what sets up the structs which continue
* to update with new location data as sbp_process() is 
* repeatedly called.
*/
void GPS::sbp_pos_llh_callback(u16 sender_id, u8 len, u8 msg[], void *context)
{
  pos_llh = *(msg_pos_llh_t *)msg;
}
void GPS::sbp_baseline_ned_callback(u16 sender_id, u8 len, u8 msg[],
  void *context)
{
  baseline_ned = *(msg_baseline_ned_t *)msg;
}
void GPS::sbp_vel_ned_callback(u16 sender_id, u8 len, u8 msg[], void *context)
{
  vel_ned = *(msg_vel_ned_t *)msg;
}
void GPS::sbp_dops_callback(u16 sender_id, u8 len, u8 msg[], void *context)
{
  dops = *(msg_dops_t *)msg;
}
void GPS::sbp_gps_time_callback(u16 sender_id, u8 len, u8 msg[], void *context)
{
  gps_time = *(msg_gps_time_t *)msg;
}
int main()
{
return 0;
}
