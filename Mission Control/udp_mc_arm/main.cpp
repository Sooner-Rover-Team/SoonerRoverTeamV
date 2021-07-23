#include <QApplication>
#include "socket.h"
#include <iostream>
#include "gamepadmonitor.h"
#include "arm_view.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    GamepadMonitor drivepad;

    arm_view window;
    window.show();

    QObject::connect( &drivepad, SIGNAL(clawPosUpdated(float,float)), &window, SLOT(updateClawPos(float,float)) );
    QObject::connect( &window, SIGNAL(armConfigUpdated(bool)), &drivepad, SLOT(updateArmConfig(bool)) );

    return a.exec();
}
