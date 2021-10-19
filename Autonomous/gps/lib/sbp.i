//sbp.i
//%import sbp.h
//%import edc.h
//%import common.h
//%include edc.i
%module sbp
%{
    #include "common.h"
    #include "edc.h"
    #include "sbp.h"
    extern s8 sbp_register_callback(sbp_state_t* s, u16 msg_type, sbp_msg_callback_t cb, void* context,
                             sbp_msg_callbacks_node_t *node);
    extern s8 sbp_remove_callback(sbp_state_t *s, sbp_msg_callbacks_node_t *node);
    extern void sbp_clear_callbacks(sbp_state_t* s);
    extern void sbp_state_init(sbp_state_t *s);
    extern void sbp_state_set_io_context(sbp_state_t *s, void* context);
    extern s8 sbp_process(sbp_state_t *s, u32 (*read)(u8 *buff, u32 n, void* context));
    extern s8 sbp_process_payload(sbp_state_t *s, u16 sender_id, u16 msg_type, u8 msg_len,
         u8 payload[]);
    extern s8 sbp_send_message(sbp_state_t *s, u16 msg_type, u16 sender_id, u8 len, u8 *payload,
                    u32 (*write)(u8 *buff, u32 n, void* context));
%}
%init%{
     
%}

extern s8 sbp_register_callback(sbp_state_t* s, u16 msg_type, sbp_msg_callback_t cb, void* context,
                         sbp_msg_callbacks_node_t *node);
extern s8 sbp_remove_callback(sbp_state_t *s, sbp_msg_callbacks_node_t *node);
extern void sbp_clear_callbacks(sbp_state_t* s);
extern void sbp_state_init(sbp_state_t *s);
extern void sbp_state_set_io_context(sbp_state_t *s, void* context);
extern s8 sbp_process(sbp_state_t *s, u32 (*read)(u8 *buff, u32 n, void* context));
extern s8 sbp_process_payload(sbp_state_t *s, u16 sender_id, u16 msg_type, u8 msg_len,
     u8 payload[]);
extern s8 sbp_send_message(sbp_state_t *s, u16 msg_type, u16 sender_id, u8 len, u8 *payload,
                    u32 (*write)(u8 *buff, u32 n, void* context));