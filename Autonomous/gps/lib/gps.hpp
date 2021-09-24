#pragma once


        /****** VARIABLES RELATED TO GPS STUFF *******/
        
        
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

// thread bitch
pthread_t gps_update_thread;

// state structure
sbp_state_t s;
    
// Socket descriptor; status of the socket
int socket_desc;


        /****** FUNCTION DECLARATIONS BITCH *******/
        

/* This function does the following: Opens a socket connecting to Piksi,
 * initializes the Swift Binary Protocol library's structures, 
 * then starts a thread that will constantly call the sbp_process()
 * function, thereby allowing the structs holding GPS data
 * to be constantly updated and accessed.
 */
void gps_init(char **ip, char **port);

/* The gps_finish function wraps up all the shit that is left hanging
 * after the gps stuff is started. This includes closing the socket
 * ending that pesky thread.
 */
void gps_finish();

/* The legendary gps_thread_task function: Serves as the argument
 * to the thread constructor. That will pass this function
 * (which continues indefinitely) to the thread to execute.
 * In this case, the thread will need to be joined to make it stop.
 */
void *gps_thread();

// socket maintenance functions. These take care of low-level C stuff
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
        
          















