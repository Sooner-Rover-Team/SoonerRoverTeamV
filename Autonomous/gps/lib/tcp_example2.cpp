#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include 

#include "sbp.h"
#include "system.h"
#include "navigation.h"

char *tcp_ip_addr = NULL;
char *tcp_ip_port = NULL;

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

int socket_desc = -1;

void usage(char *prog_name) {
  fprintf(stderr, "usage: %s [-a address -p port]\n", prog_name);
}

void setup_socket()
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

void close_socket()
{
  close(socket_desc);
}

void sbp_pos_llh_callback(u16 sender_id, u8 len, u8 msg[], void *context)
{
  pos_llh = *(msg_pos_llh_t *)msg;
}
void sbp_baseline_ned_callback(u16 sender_id, u8 len, u8 msg[], void *context)
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

u32 socket_read(u8 *buff, u32 n, void *context)
{
  (void)context;
  u32 result;

  result = read(socket_desc, buff, n);
  return result;
}

int main(int argc, char **argv)
{
  int opt;
  int result = 0;
  sbp_state_t s;

  if (argc <= 2) {
    usage(argv[0]);
    exit(EXIT_FAILURE);
  }

  while ((opt = getopt(argc, argv, "a:p:")) != -1) {
    switch (opt) {
      case 'a':
        tcp_ip_addr = (char *)calloc(strlen(optarg) + 1, sizeof(char));
        if (!tcp_ip_addr) {
          fprintf(stderr, "Cannot allocate memory!\n");
          exit(EXIT_FAILURE);
        }
        strcpy(tcp_ip_addr, optarg);
        break;
      case 'p':
        tcp_ip_port = (char *)calloc(strlen(optarg) + 1, sizeof(char));
        if (!tcp_ip_port) {
          fprintf(stderr, "Cannot allocate memory!\n");
          exit(EXIT_FAILURE);
        }
        strcpy(tcp_ip_port, optarg);
        break;
      case 'h':
        usage(argv[0]);
        exit(EXIT_FAILURE);
      default:
        break;
    }
  }

  if ((!tcp_ip_addr) || (!tcp_ip_port)) {
    fprintf(stderr, "Please supply the address and port of the SBP data stream!\n");
    exit(EXIT_FAILURE);
  }

  setup_socket();
  sbp_state_init(&s);

  /* Register a node and callback, and associate them with a specific message ID. */
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

  while(1) {
    sbp_process(&s, &socket_read);

    fprintf(stdout, "\n\n\n\n");

    /* Print GPS time. */
    fprintf(stdout, "GPS Time:\n");
    fprintf(stdout, "\tWeek\t\t: %6d\n", (int)gps_time.wn);
    fprintf(stdout, "%6.2f", ((float)gps_time.tow)/1e3);
    fprintf(stdout, "\n");

    /* Print absolute position. */
    fprintf(stdout, "Absolute Position:\n");
    fprintf(stdout, "%4.10lf", pos_llh.lat);
    fprintf(stdout, "%4.10lf", pos_llh.lon);
    fprintf(stdout, "%4.10lf", pos_llh.height);
    fprintf(stdout, "\tSatellites\t:     %02d\n", pos_llh.n_sats);
    fprintf(stdout, "\n");

    /* Print NED (North/East/Down) baseline (position vector from base to rover). */
    fprintf(stdout, "Baseline (mm):\n");
    fprintf(stdout, "\tNorth\t\t: %6d\n", (int)baseline_ned.n);
    fprintf(stdout, "\tEast\t\t: %6d\n", (int)baseline_ned.e);
    fprintf(stdout, "\tDown\t\t: %6d\n", (int)baseline_ned.d);
    fprintf(stdout, "\n");

    /* Print NED velocity. */
    fprintf(stdout, "Velocity (mm/s):\n");
    fprintf(stdout, "\tNorth\t\t: %6d\n", (int)vel_ned.n);
    fprintf(stdout, "\tEast\t\t: %6d\n", (int)vel_ned.e);
    fprintf(stdout, "\tDown\t\t: %6d\n", (int)vel_ned.d);
    fprintf(stdout, "\n");
  }

  close_socket();
  free(tcp_ip_addr);
  free(tcp_ip_port);
  return result;
}
