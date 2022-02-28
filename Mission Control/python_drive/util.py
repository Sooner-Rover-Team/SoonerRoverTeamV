from math import hypot, sqrt, cos, atan, acos, pi
import pygame
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

def arm_calc(alt_arm_config, temp_u, temp_v):
    #default configuration
    #make sure it stays in cylindrical bounds:
    # x^2 + y^2 <= 945.7103
    if not alt_arm_config:
        if( hypot(temp_u, temp_v) > 30.75 ):
            temp_u += temp_u*((30.75/hypot(temp_u, temp_v))-1)
            temp_v += temp_v*((30.75/hypot(temp_u, temp_v))-1)
                    # x^2 + y^2 >= 324.6326
        if( hypot(temp_u, temp_v) < 18.02 ):
            temp_u += temp_u*((18.02/hypot(temp_u, temp_v))-1)
            temp_v += temp_v*((18.02/hypot(temp_u, temp_v))-1)
                    # (x-17.8513)^2 + (y-2.3858)^2 <= 324.3601 ***only for the bottom part of the circle***
        if( hypot(temp_u-17.8513, temp_v-2.3858) > 18.01 and temp_v < 0 ):
            temp_u += (temp_u-17.8513)*((18.01/hypot((temp_u-17.8513), (temp_v-2.3858)))-1)
            temp_v += (temp_v-2.3858)*((18.01/hypot((temp_u-17.8513), (temp_v-2.3858)))-1)
                    # (x-1.4631)^2 + (y-17.9505)^2 >= 324.3601
        if( hypot(temp_u-1.4631, temp_v-17.9505) < 18.01 ):
            temp_u += (temp_u-1.4631)*((18.01/hypot((temp_u-1.4631), (temp_v-17.9505)))-1)
            temp_v += (temp_v-17.9505)*((18.01/hypot((temp_u-1.4631), (temp_v-17.9505)))-1)
                            # calculate the actuator lengths
        hypot2 = pow(temp_u, 2) + pow(temp_v, 2)
        x_len = sqrt(160.6811-77.8123*cos( acos( (99.3601-hypot2)/(-30.0*sqrt(hypot2)) ) + atan(temp_v/temp_u)+.40602 ))
        y_len = sqrt(168.5116-(85.8577*cos(2.91186-acos((hypot2-549.3601)/(-540.3)))))
    else:
        # configuration for the equipment servicing task
        # make sure it stays in cylindrical bounds:
        # x^2 + y^2 <= 956.4557
        if( hypot(temp_u, temp_v) > 30.93 ):
            temp_u += temp_u*((30.93/hypot(temp_u, temp_v))-1)
            temp_v += temp_v*((30.93/hypot(temp_u, temp_v))-1)
        # x^2 + y^2 >= 427.3300
        if( hypot(temp_u, temp_v) < 20.67 ):
            temp_u += temp_u*((20.67/hypot(temp_u, temp_v))-1)
            temp_v += temp_v*((20.67/hypot(temp_u, temp_v))-1)
        # (x-14.8678)^2 + (y-1.9870)^2 <= 324.3601 ***only for the bottom part of the circle***
        if( hypot(temp_u-14.8678, temp_v-1.9870) > 18.01 and temp_v < 0 ):
            temp_u += (temp_u-14.8678)*((18.01/hypot((temp_u-14.8678), (temp_v-1.9870)))-1)
            temp_v += (temp_v-1.9870)*((18.01/hypot((temp_u-14.8678), (temp_v-1.9870)))-1)
        # (x-1.2187)^2 + (y-14.9504)^2 >= 324.3601
        if( hypot(temp_u-1.2187, temp_v-14.9504) < 18.01 ):
            temp_u += (temp_u-1.2187)*((18.01/hypot((temp_u-1.2187), (temp_v-14.9504)))-1)
            temp_v += (temp_v-14.9504)*((18.01/hypot((temp_u-1.2187), (temp_v-14.9504)))-1)
        # the collision stuff doesnt work as well at such sharp corners
        if( temp_v > 0 ):
            if( temp_v > 27.5 ):
                temp_v = 27.5
            if( temp_u < 14.25 ):
                temp_u = 14.25

        # calculate the length of each actuator based on the coordinate (u,v)
        hypot2 = pow(temp_u, 2) + pow(temp_v, 2);
        x_len = sqrt(160.6811-77.8123*cos(acos((99.3601-hypot2)/(-30.0*sqrt(hypot2)))+atan(temp_v/temp_u)+.40602));
        y_len = sqrt(180.5948-(100.9791*cos(2.96241-acos((hypot2-549.3601)/(-540.3)))));

    return x_len,y_len, temp_u, temp_v

""" draw all the arm garbage on screen """
def draw_arm_stuff(screen, alt_arm_config, claw_x, claw_y):
    scale = 12
    origin_x = 150
    origin_y = 375

    #origin
    pygame.draw.line(screen,BLACK,(origin_x-10, origin_y),(origin_x+10, origin_y))
    pygame.draw.line(screen,BLACK,(origin_x, origin_y-10),(origin_x, origin_y+10))

    if not alt_arm_config:
        # bounds for default configuration
        # painter.drawArc(origin_x-30.75*scale, origin_y-30.75*scale, 30.75*scale*2, 30.75*scale*2, -25*16, 80*16);
        r = pygame.rect.Rect(origin_x-30.75*scale, origin_y-30.75*scale, 30.75*scale*2, 30.75*scale*2)
        pygame.draw.arc(screen,BLACK,r, -24*pi/180, 55*pi/180)
        # painter.drawArc(origin_x-18.02*scale, origin_y-18.02*scale, 18.02*scale*2, 18.02*scale*2, -60*16, 90*16);
        r = pygame.rect.Rect(origin_x-18.02*scale, origin_y-18.02*scale, 18.02*scale*2, 18.02*scale*2)
        pygame.draw.arc(screen,BLACK, r, -52*pi/180, 25*pi/180)
        # painter.drawArc((origin.x()+17.8513*scale)-18.01*scale, (origin.y()-2.3858*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -120*16, 70*16);
        r = pygame.rect.Rect((origin_x+17.8513*scale)-18.01*scale, (origin_y-2.3858*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2)
        pygame.draw.arc(screen,BLACK, r, -113*pi/180, -55*pi/180)
        # painter.drawArc((origin_x+1.4631*scale)-18.01*scale, (origin_y-17.9505*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -40*16, 65*16);
        r = pygame.rect.Rect((origin_x+1.4631*scale)-18.01*scale, (origin_y-17.9505*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2)
        pygame.draw.arc(screen,BLACK, r, -36*pi/180, 24*pi/180)
    else:
        # bounds for equipment servicing configuration
        # painter.drawArc(origin_x-30.93*scale, origin_y-30.93*scale, 30.93*scale*2, 30.93*scale*2, -20*pi/180, 90*pi/180);
        r = pygame.rect.Rect(origin_x-30.93*scale, origin_y-30.93*scale, 30.93*scale*2, 30.93*scale*2)
        pygame.draw.arc(screen, BLACK,r, -15*pi/180, 63*pi/180)
        # painter.drawArc(origin_x-20.67*scale, origin_y-20.67*scale, 20.67*scale*2, 20.67*scale*2, -60*pi/180, 90*pi/180);
        r = pygame.rect.Rect(origin_x-20.67*scale, origin_y-20.67*scale, 20.67*scale*2, 20.67*scale*2)
        pygame.draw.arc(screen, BLACK,r, -51*pi/180, 27*pi/180)
        # painter.drawArc((origin_x+14.8678*scale)-18.01*scale, (origin_y-1.9870*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -100*pi/180, 70*pi/180);
        r = pygame.rect.Rect((origin_x+14.8678*scale)-18.01*scale, (origin_y-1.9870*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2)
        pygame.draw.arc(screen, BLACK,r, -96*pi/180, -33*pi/180)
        # painter.drawArc((origin_x+1.2187*scale)-18.01*scale, (origin_y-14.9504*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -20*pi/180, 65*pi/180);
        r = pygame.rect.Rect((origin_x+1.2187*scale)-18.01*scale, (origin_y-14.9504*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2)
        pygame.draw.arc(screen, BLACK,r, -20*pi/180, 45*pi/180)

    #claw position
    pygame.draw.line(screen, BLACK, (origin_x+claw_x*scale-5, origin_y+claw_y*scale-5), (origin_x+claw_x*scale+5, origin_y+claw_y*scale+5))
    pygame.draw.line(screen, BLACK, (origin_x+claw_x*scale-5, origin_y+claw_y*scale+5), (origin_x+claw_x*scale+5, origin_y+claw_y*scale-5))

class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def print(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, (self.x, self.y))
        self.x += textBitmap.get_width()
        
    def println(self, screen, textString):
        self.print(screen, textString)
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10