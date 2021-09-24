#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <thread>
#include <vector>

#include "sbp.h"
#include "system.h"
#include "navigation.h"

class GPS
{
    /* SBP structs that messages from Piksi will feed. */
    msg_pos_llh_t      pos_llh;
    msg_baseline_ned_t baseline_ned;
    msg_vel_ned_t      vel_ned;
    msg_dops_t         dops;
    msg_gps_time_t gps_time; 

    /*
     * SBP callback nodes must be statically allocated. Each message ID / callback
     * pair must have a unique sbp_msg_callbacks_node_t associated with it.
     */
    sbp_msg_callbacks_node_t pos_llh_node;
    sbp_msg_callbacks_node_t baseline_ned_node;
    sbp_msg_callbacks_node_t vel_ned_node;
    sbp_msg_callbacks_node_t dops_node;
    sbp_msg_callbacks_node_t gps_time_node;

    // IP address and port that of the Piksi Multi
    char *tcp_ip_addr;
    char *tcp_ip_port;

    // location vector
    std::vector<float> abs_location;

    // state structure
    sbp_state_t s;
        



    // Socket descriptor; status of the socket
    int socket_desc;

    void thread_task();

    GPS(char **ip, char **port);
    ~GPS();

    // socket maintenance functions
    void setup_socket();
    void close_socket();
    // socket read function: Reference to this is also passed to sbp_process()
    u32 socket_read(u8 *buff, u32 n, void *context);

    /* Callback functions. References to these functions are passed
     * as one of the arguments in the sbp_register_callback() function.
     * As far as I know, that is what sets up the structs which continue
     * to update with new location data as sbp_process() is 
     * repeatedly called.
     */
    void sbp_pos_llh_callback(u16 sender_id, u8 len, u8 msg[], void *context);
    void sbp_baseline_ned_callback(u16 sender_id, u8 len, u8 msg[], void *context);
    void sbp_vel_ned_callback(u16 sender_id, u8 len, u8 msg[], void *context);
    void sbp_dops_callback(u16 sender_id, u8 len, u8 msg[], void *context);
    void sbp_gps_time_callback(u16 sender_id, u8 len, u8 msg[], void *context);
};
          















