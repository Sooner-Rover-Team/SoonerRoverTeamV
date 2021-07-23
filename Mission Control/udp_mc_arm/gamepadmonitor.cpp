#include "gamepadmonitor.h"
#include <cmath>
#include <QtGamepad/QGamepad>
#include <QDebug>
#include <stdio.h>
// 149 73
#define CLAW_L_OPEN 149
#define CLAW_L_CLOSED 87
#define CLAW_R_OPEN 73
#define CLAW_R_CLOSED 28

GamepadMonitor::GamepadMonitor( QObject *parent)
    : QObject(parent)
    , m_gamepad(0)
{
    auto gamepads = QGamepadManager::instance()->connectedGamepads();
    if (gamepads.isEmpty()) {
        return;
    }

    m_gamepad = new QGamepad(*gamepads.begin(), this);
    /*connect(m_gamepad, &QGamepad::axisLeftXChanged, this, [](double value){
        qDebug() << "Left X" << value;
    });*/
    connect(m_gamepad, SIGNAL(axisLeftXChanged(double)), this, SLOT(onXAxis(double)));
    connect(m_gamepad, SIGNAL(axisLeftYChanged(double)), this, SLOT(onYAxis(double)));
    connect(m_gamepad, SIGNAL(axisRightYChanged(double)), this, SLOT(onRYAxis(double)));
    connect(m_gamepad, SIGNAL(axisRightXChanged(double)), this, SLOT(onRXAxis(double)));
    connect(m_gamepad, SIGNAL(buttonBChanged(bool)), this, SLOT(onButtonB(bool)));
    connect(m_gamepad, SIGNAL(buttonYChanged(bool)), this, SLOT(onButtonY(bool)));
    connect(m_gamepad, SIGNAL(buttonXChanged(bool)), this, SLOT(onButtonX(bool)));
    connect(m_gamepad, SIGNAL(buttonUpChanged(bool)), this, SLOT(onButtonUp(bool)));
    connect(m_gamepad, SIGNAL(buttonDownChanged(bool)), this, SLOT(onButtonDown(bool)));
    connect(m_gamepad, SIGNAL(buttonL2Changed(double)), this, SLOT(onL2(double)));
    connect(m_gamepad, SIGNAL(buttonR2Changed(double)), this, SLOT(onR2(double)));
    connect(&mySocket, SIGNAL(UDPrecived(QByteArray)), this, SLOT(message(QByteArray)));
    /*
    connect(m_gamepad, &QGamepad::buttonAChanged, this, [](bool pressed){
        qDebug() << "Button A" << pressed;
    });
     connect(m_gamepad, &QGamepad::buttonXChanged, this, [](bool pressed){
        qDebug() << "Button X" << pressed;
    });
    connect(m_gamepad, &QGamepad::buttonYChanged, this, [](bool pressed){
        qDebug() << "Button Y" << pressed;
    });
    connect(m_gamepad, &QGamepad::buttonL1Changed, this, [](bool pressed){
        qDebug() << "Button L1" << pressed;
    });
    connect(m_gamepad, &QGamepad::buttonR1Changed, this, [](bool pressed){
        qDebug() << "Button R1" << pressed;
    });
    connect(m_gamepad, &QGamepad::buttonL2Changed, this, [](double value){
        qDebug() << "Button L2: " << value;
    });
    connect(m_gamepad, &QGamepad::buttonR2Changed, this, [](double value){
        qDebug() << "Button R2: " << value;
    });
    connect(m_gamepad, &QGamepad::buttonSelectChanged, this, [](bool pressed){
        qDebug() << "Button Select" << pressed;
    });
    connect(m_gamepad, &QGamepad::buttonStartChanged, this, [](bool pressed){
        qDebug() << "Button Start" << pressed;
    });
    connect(m_gamepad, &QGamepad::buttonGuideChanged, this, [](bool pressed){
        qDebug() << "Button Guide" << pressed;
    });*/

    // initialize stuff
    // values dependent of previous inputs over time:
    clawL = CLAW_L_OPEN;           // claw servo angle
    clawR = CLAW_L_CLOSED;
    coord_u = 18.5;       // wrist position
    coord_v = 9.5;
    phi = 0.0;            // wrist angle
    theta = 0.0;
    // physical values of arm:
    base_rotation = 0;    // between 0 and 180
    shoulder_length = 0;
    elbow_length = 0;
    wrist_rotation = 0.0; // in degrees
    wrist_angle = 0.0;
    // direct controller values:
    left_x_axis = 0.0;
    left_y_axis = 0.0;
    right_x_axis = 0.0;
    right_y_axis = 0.0;

    alt_arm_config = false;

    // timer for sending data (currently at 10 Hz)
    udpTimer = new QTimer();
    connect(udpTimer, SIGNAL(timeout()), this, SLOT(sendUDP()));
    udpTimer->start(100);
}

void GamepadMonitor::updateArmConfig(bool alt)
{
    alt_arm_config = alt;
}

void GamepadMonitor::message(QByteArray arr){
    printf(arr);
}

void GamepadMonitor::onXAxis(double value){
    left_x_axis = value;

}

void GamepadMonitor::onYAxis(double value){
    left_y_axis = value;

}

void GamepadMonitor::onRYAxis(double value){
    right_y_axis = value;
}

void GamepadMonitor::onRXAxis(double value){
    //printf("hello");
    phi = value;
    //qDebug() << phi;
    //else phi = 0;
}

 void GamepadMonitor::onButtonB(bool pressed){
     if(pressed)
     {
        clawL = CLAW_L_CLOSED;
        clawR = CLAW_R_CLOSED;
     } else {
        clawL = CLAW_L_OPEN;
        clawR = CLAW_R_OPEN;
     }
 }

 void GamepadMonitor::onButtonY(bool pressed){
     if(pressed)
     {
        clawL -= 1;
        clawR += 1;
     }
 }

 void GamepadMonitor::onButtonX(bool pressed){
     if(pressed)
     {
        clawL += 1;
        clawR -= 1;
     }
 }

void GamepadMonitor::onL2(double value){
    theta = -value;
}

void GamepadMonitor::onR2(double value){

    //if(value > .1)
    theta = value;
    //else theta = 0;

}

void GamepadMonitor::onButtonUp(bool pressed){
    /*
    if( pressed){
        gimbleUD = 1;
    }else{
        gimbleUD = 0;
    }
    //printVals();
    //sendUDP();
    */
}

void GamepadMonitor::onButtonDown(bool pressed){
/*
        if( pressed){
            gimbleUD = -1;
        }else{
            gimbleUD = 0;
        }
        //printVals();
        //sendUDP();
*/
}

void GamepadMonitor::sendUDP(){
    // control the coordinate based on controller input
    // the number 0.2 below means its top speed is 0.2 inches/second
    float temp_u = coord_u;
    float temp_v = coord_v;
    if(abs(left_y_axis) > .1 )
        temp_u -= left_y_axis*0.2;
    if(abs(right_y_axis) > .1 )
        temp_v -= right_y_axis*0.2;

    float x_len, y_len;

    if(!alt_arm_config)
    {
        // default configuration
        // make sure it stays in cylindrical bounds:
        // x^2 + y^2 <= 945.7103
        if( hypot(temp_u, temp_v) > 30.75 )
        {
            temp_u += temp_u*((30.75/hypot(temp_u, temp_v))-1);
            temp_v += temp_v*((30.75/hypot(temp_u, temp_v))-1);
        }
        // x^2 + y^2 >= 324.6326
        if( hypot(temp_u, temp_v) < 18.02 )
        {
            temp_u += temp_u*((18.02/hypot(temp_u, temp_v))-1);
            temp_v += temp_v*((18.02/hypot(temp_u, temp_v))-1);
        }
        // (x-17.8513)^2 + (y-2.3858)^2 <= 324.3601 ***only for the bottom part of the circle***
        if( hypot(temp_u-17.8513, temp_v-2.3858) > 18.01 && temp_v < 0 )
        {
            temp_u += (temp_u-17.8513)*((18.01/hypot((temp_u-17.8513), (temp_v-2.3858)))-1);
            temp_v += (temp_v-2.3858)*((18.01/hypot((temp_u-17.8513), (temp_v-2.3858)))-1);
        }
        // (x-1.4631)^2 + (y-17.9505)^2 >= 324.3601
        if( hypot(temp_u-1.4631, temp_v-17.9505) < 18.01 )
        {
            temp_u += (temp_u-1.4631)*((18.01/hypot((temp_u-1.4631), (temp_v-17.9505)))-1);
            temp_v += (temp_v-17.9505)*((18.01/hypot((temp_u-1.4631), (temp_v-17.9505)))-1);
        }

        // calculate the actuator lengths
        float hypot2 = pow(temp_u, 2) + pow(temp_v, 2);
        x_len = sqrt(160.6811-77.8123*cos( acos( (99.3601-hypot2)/(-30.0*sqrt(hypot2)) ) + atan(temp_v/temp_u)+.40602 ));
        y_len = sqrt(168.5116-(85.8577*cos(2.91186-acos((hypot2-549.3601)/(-540.3)))));

        // convert inches to degrees for the servos
        // max: 13.62 in = 135 deg
        // min: 9.69 in = 40 deg
        shoulder_length = uint8_t(round((x_len-9.69)*(95/3.93))+40);
        elbow_length = uint8_t(round((y_len-9.69)*(95/3.93))+40);

        coord_u = temp_u;
        coord_v = temp_v;
        emit clawPosUpdated(coord_u, coord_v);
    } else {
        // configuration for the equipment servicing task
        //make sure it stays in cylindrical bounds:
        // x^2 + y^2 <= 956.4557
        if( hypot(temp_u, temp_v) > 30.93 )
        {
            temp_u += temp_u*((30.93/hypot(temp_u, temp_v))-1);
            temp_v += temp_v*((30.93/hypot(temp_u, temp_v))-1);
        }
        // x^2 + y^2 >= 427.3300
        if( hypot(temp_u, temp_v) < 20.67 )
        {
            temp_u += temp_u*((20.67/hypot(temp_u, temp_v))-1);
            temp_v += temp_v*((20.67/hypot(temp_u, temp_v))-1);
        }
        // (x-14.8678)^2 + (y-1.9870)^2 <= 324.3601 ***only for the bottom part of the circle***
        if( hypot(temp_u-14.8678, temp_v-1.9870) > 18.01 && temp_v < 0 )
        {
            temp_u += (temp_u-14.8678)*((18.01/hypot((temp_u-14.8678), (temp_v-1.9870)))-1);
            temp_v += (temp_v-1.9870)*((18.01/hypot((temp_u-14.8678), (temp_v-1.9870)))-1);
        }
        // (x-1.2187)^2 + (y-14.9504)^2 >= 324.3601
        if( hypot(temp_u-1.2187, temp_v-14.9504) < 18.01 )
        {
            temp_u += (temp_u-1.2187)*((18.01/hypot((temp_u-1.2187), (temp_v-14.9504)))-1);
            temp_v += (temp_v-14.9504)*((18.01/hypot((temp_u-1.2187), (temp_v-14.9504)))-1);
        }
        // the collision stuff doesnt work as well at such sharp corners
        if( temp_v > 0 )
        {
            if( temp_v > 27.5 )
                temp_v = 27.5;
            if( temp_u < 14.25 )
                temp_u = 14.25;
        }

        // calculate the length of each actuator based on the coordinate (u,v)
        float hypot2 = pow(temp_u, 2) + pow(temp_v, 2);
        x_len = sqrt(160.6811-77.8123*cos(acos((99.3601-hypot2)/(-30.0*sqrt(hypot2)))+atan(temp_v/temp_u)+.40602));
        y_len = sqrt(180.5948-(100.9791*cos(2.96241-acos((hypot2-549.3601)/(-540.3)))));

        // convert inches to degrees for the servos
        // max: 13.62 in = 135 deg, min: 9.69 in = 40 deg
        shoulder_length = uint8_t(round((x_len-9.69)*(95/3.93))+40);
        elbow_length = uint8_t(round((y_len-9.69)*(95/3.93))+40);

        coord_u = temp_u;
        coord_v = temp_v;
        emit clawPosUpdated(coord_u, coord_v);
    }


    wrist_angle = 127 * theta;
    if (wrist_angle < 10 && wrist_angle > -10) {
        wrist_angle = 0;
    }
    wrist_rotation = 127 * phi;
    if (wrist_rotation < 10 && wrist_rotation > -10) {
        wrist_rotation = 0;
    }

    base_rotation = 90 + (left_x_axis * 20); // between 0 and 180, centered (no motion) at 90

    // send the data
    QByteArray out;
    out.append(char(-127));
    out.append(char(1));
    out.append(base_rotation);
    out.append(shoulder_length);
    out.append(elbow_length);
    out.append(char(wrist_angle));
    out.append(char(wrist_rotation));
    out.append(clawL);
    out.append(clawR);
    out.append(uint8_t((base_rotation+shoulder_length+elbow_length+wrist_angle+wrist_rotation+clawL+clawR)/7));
    mySocket.sendUDP(out);

    qDebug() << "x:" << coord_u << "\ty:" << coord_v
             << "\tx len: " << x_len << "\ty len:"<< y_len << "\tbase rot: " << base_rotation
             << "\t1:" << shoulder_length << "\t2:" << elbow_length
             << "\tcl:" << clawL << ", " << clawR <<"\twrist ang: "<< wrist_angle << "\twrist rot: "<< wrist_rotation
             << "\thash: " << uint8_t((base_rotation+shoulder_length+elbow_length+wrist_angle+wrist_rotation+clawL+clawR)/7) << endl;
}

void GamepadMonitor::printVals(){
    /*
    int hash = (overdrive + leftSide + rightSide +gimbleUD + gimbleRL)/5;

    //sprintf(buf, "%d, %d, %d, %d, %d, %d\n", overdrive, leftSide, rightSide, gimbleUD, gimbleRL, hash);
    //qDebug(buf);
    printf("%c, %d, %d, %d, %d, %d, %d, %d\n", char(-127), 0, overdrive, leftSide, rightSide, gimbleUD, gimbleRL, hash);
    */
}

GamepadMonitor::~GamepadMonitor()
{
    delete m_gamepad;
}

