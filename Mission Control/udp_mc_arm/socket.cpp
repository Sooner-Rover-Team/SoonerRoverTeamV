#include "socket.h"
// craptop is 10.0.0.3 (on wifi)
// soro desktop is 192.168.1.100
// mission-control-2 is 192.168.1.103
// mission-control-1 is 192.168.1.102

socket::socket(QObject *parent) : QObject(parent)
{
    socketIn = new QUdpSocket(this);
    socketOut = new QUdpSocket(this);//"192.168.1.103"), 1237))
    if(socketIn->bind(QHostAddress("10.0.0.3"), 1234))
    {
        qDebug() << "Bound to port 1234";
    } else {
        qDebug() << "Error binding to port:" << socketIn->errorString();
    }
    connect(socketIn, SIGNAL(readyRead()), this, SLOT(readUDP()));

    resetTimer = new QTimer(); // this timer is used to stop sending data for a second when this computer recieves -124 at the start of a udp message. To be used when communications become unstable.

    /*
    // request data from accelerometer
    //eventually, this can just be put on a timer for every 5 seconds or something
    QByteArray buffer; // sends: -126 (start), 4 (device id), 192.168.1.100 (ip), 1237 (port)
    buffer.append(char(-126));
    buffer.append(uint8_t(4));
    buffer.append(uint8_t(192));
    buffer.append(uint8_t(168));
    buffer.append(uint8_t(1));
    buffer.append(uint8_t(100));
    buffer.append(uint8_t(4));
    buffer.append(uint8_t(213));
    socketOut->writeDatagram(buffer, QHostAddress("192.168.1.102"), 1234);
    */
}

void socket::sendUDP(QByteArray Data)
{
    if(!resetTimer->isActive())
    {
        socketOut->writeDatagram(Data, QHostAddress("10.0.0.102"), 1002);//"192.168.1.102"), 1234);
    }
}

void socket::readUDP()
{
    // when data comes in
    QByteArray buffer;
    buffer.resize(socketIn->pendingDatagramSize());

    QHostAddress sender;
    quint16 senderPort; //can probably take sender and senderPort out

    socketIn->readDatagram(buffer.data(), buffer.size(), &sender, &senderPort);

    for(int i = 0; i < buffer.size(); i++)
    {
        int8_t temp = buffer.at(i);
        printf("%d,\t", temp);
    }
    printf("\n");

    if(buffer.at(0) == -124)
    {
        resetTimer->start(1000);
    }
    //emit UDPrecived(buffer);
}
