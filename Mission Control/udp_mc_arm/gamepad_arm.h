#ifndef GAMEPAD_ARM_H
#define GAMEPAD_ARM_H

#include <QObject>

class gamepad_arm : public QObject
{
    Q_OBJECT
public:
    explicit gamepad_arm(QObject *parent = nullptr);

signals:

public slots:
};

#endif // GAMEPAD_ARM_H