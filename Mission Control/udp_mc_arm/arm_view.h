#ifndef ARM_VIEW_H
#define ARM_VIEW_H

#include <QWidget>
#include <QtGui>
#include <QTimer>

namespace Ui {
class arm_view;
}

class arm_view : public QWidget
{
    Q_OBJECT

public:
    explicit arm_view(QWidget *parent = 0);
    ~arm_view();

public slots:
    void updateClawPos(float x, float y);

signals:
    void armConfigUpdated(bool alt);

private:
    Ui::arm_view *ui;
    float claw_x;
    float claw_y;
    QTimer* frame_timer;
    bool alt_arm_config;

protected:
    void paintEvent(QPaintEvent *event);

private slots:
    void on_altConfigCheck_stateChanged(int arg1);
};

#endif // ARM_VIEW_H
