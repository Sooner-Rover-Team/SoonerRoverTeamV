%module edc
%{
    #include "edc.h"
    static const u16 crc16tab[256];
    extern u16 crc16_ccitt(const u8 *buf, u32 len, u16 crc);
%}
    
    static const u16 crc16tab[256];
    extern u16 crc16_ccitt(const u8 *buf, u32 len, u16 crc);
