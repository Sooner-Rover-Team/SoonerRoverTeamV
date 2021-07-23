#include "arm_view.h"
#include "ui_arm_view.h"

arm_view::arm_view(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::arm_view)
{
    ui->setupUi(this);

    claw_x = 18.5; //same initial value as in gamepadmonitor.h, except the y coordinate is *(-1)
    claw_y = -9.5;

    alt_arm_config = false;

    frame_timer = new QTimer(this);
    connect(frame_timer, SIGNAL(timeout()), this, SLOT(update()));
    frame_timer->start(33); // about 30 fps
}

arm_view::~arm_view()
{
    delete ui;
}

void arm_view::updateClawPos(float x, float y)
{
    claw_x = x;
    claw_y = -y;
}

void arm_view::paintEvent(QPaintEvent *event)
{
    QPainter painter(this);
    float scale = 12.0;
    QPointF origin(150, 375);

    //origin
    painter.drawLine(origin.x()-10, origin.y(), origin.x()+10, origin.y());
    painter.drawLine(origin.x(), origin.y()-10, origin.x(), origin.y()+10);

    if(!alt_arm_config)
    {
        // bounds for default configuration
        painter.drawArc(origin.x()-30.75*scale, origin.y()-30.75*scale, 30.75*scale*2, 30.75*scale*2, -25*16, 80*16);
        painter.drawArc(origin.x()-18.02*scale, origin.y()-18.02*scale, 18.02*scale*2, 18.02*scale*2, -60*16, 90*16);
        painter.drawArc((origin.x()+17.8513*scale)-18.01*scale, (origin.y()-2.3858*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -120*16, 70*16);
        painter.drawArc((origin.x()+1.4631*scale)-18.01*scale, (origin.y()-17.9505*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -40*16, 65*16);
    } else {
        // bounds for equipment servicing configuration
        painter.drawArc(origin.x()-30.93*scale, origin.y()-30.93*scale, 30.93*scale*2, 30.93*scale*2, -20*16, 90*16);
        painter.drawArc(origin.x()-20.67*scale, origin.y()-20.67*scale, 20.67*scale*2, 20.67*scale*2, -60*16, 90*16);
        painter.drawArc((origin.x()+14.8678*scale)-18.01*scale, (origin.y()-1.9870*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -100*16, 70*16);
        painter.drawArc((origin.x()+1.2187*scale)-18.01*scale, (origin.y()-14.9504*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -20*16, 65*16);
    }

    //claw position
    painter.drawLine(origin.x()+claw_x*scale-5, origin.y()+claw_y*scale-5, origin.x()+claw_x*scale+5, origin.y()+claw_y*scale+5);
    painter.drawLine(origin.x()+claw_x*scale-5, origin.y()+claw_y*scale+5, origin.x()+claw_x*scale+5, origin.y()+claw_y*scale-5);
}

void arm_view::on_altConfigCheck_stateChanged(int state)
{
    if(state == 2)
    {
        alt_arm_config = true;
        emit armConfigUpdated(true);
    }
    else if(state == 0)
    {
        alt_arm_config = false;
        emit armConfigUpdated(false);
    }
}
