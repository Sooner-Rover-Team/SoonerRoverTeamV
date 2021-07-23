#ifndef GAMEPADMONITOR_H
#define GAMEPADMONITOR_H

#include <QtCore/QObject>
#include <QtCore/QTimer>
#include "socket.h"
#include <cmath>

QT_BEGIN_NAMESPACE
class QGamepad;
QT_END_NAMESPACE

class GamepadMonitor : public QObject
{
    Q_OBJECT
public:
    //int buttons[10];
    explicit GamepadMonitor(QObject *parent = 0);
    ~GamepadMonitor();

private:
    QGamepad *m_gamepad;
    socket mySocket;
    QTimer *udpTimer;

    void printVals();

    uint8_t base_rotation; // all these numbers are between 0 and 180
    uint8_t shoulder_length;
    uint8_t elbow_length;
    float wrist_rotation; // in degrees
    float wrist_angle;
    uint8_t clawL;
    uint8_t clawR;

    float phi;// for the wrist
    float theta;// for the wrist
    float left_x_axis;
    float left_y_axis;
    float right_x_axis;
    float right_y_axis;

    float coord_u;
    float coord_v;

    bool alt_arm_config;

public slots:
    void onXAxis(double value);
    void onYAxis(double value);
    void onRYAxis(double value);
    void onRXAxis(double value);
    void onButtonB(bool pressed);
    void onButtonY(bool pressed);
    void onButtonX(bool pressed);
    void onL2(double value);
    void onR2(double value);
    void onButtonUp(bool pressed);
    void onButtonDown(bool pressed);
    void sendUDP();
    void message(QByteArray arr);
    void updateArmConfig(bool alt);

signals:
    void clawPosUpdated(float x, float y);
};

#endif // GAMEPADMONITOR_H
