cmake_minimum_required(VERSION 2.8)

project(libtest_project)

file(GLOB source_files 
    gps.c
    edc.c  
    sbp.c 
    acquisition.h 
    bootload.h 
    common.h 
    edc.h 
    ext_events.h 
    file_io.h 
    flash.h 
    gnss.h 
    gps.h 
    imu.h 
    logging.h 
    mag.h 
    navigation.h 
    ndb.h 
    observation.h 
    orientation.h 
    piksi.h 
    sbas.h 
    sbp.h 
    settings.h 
    ssr.h 
    system.h 
    tracking.h 
    user.h 
    vehicle.h 
    version.h 
)

add_library(gps STATIC ${source_files})

set_target_properties(gps PROPERTIES LINKER_LANGUAGE C)

install(TARGETS gps DESTINATION lib)
install(FILES gps.h DESTINATION include)
