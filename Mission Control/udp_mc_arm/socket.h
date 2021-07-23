#ifndef SOCKET_H
#define SOCKET_H

#include <QObject>
#include <QUdpSocket>
#include <QTimer>

class socket : public QObject
{
    Q_OBJECT
public:
    explicit socket(QObject *parent = nullptr);
    void sendUDP(QByteArray message);

signals:
    void UDPrecived(QByteArray buff);
public slots:
    void readUDP();
private:
    QUdpSocket* socketIn;
    QUdpSocket* socketOut;
    QTimer* resetTimer;
};

#endif // SOCKET_H
