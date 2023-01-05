from math import hypot, sqrt, cos, sin, atan, acos, pi
import pygame
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

""" helper function for calculate_third_corner """
def check_triangle(a, b, c):
    if a <= 0 or b <= 0 or c <= 0:
        return False  # one of the sides has a non-positive length
    if a + b <= c or a + c <= b or b + c <= a:
        return False  # the triangle inequality is not satisfied
    return True  # the triangle is valid

""" Just some linear algebra to find the elbow joint location for GUI arm """
def calculate_third_corner(Ax, Ay, Cx, Cy, a, c, alt=False):
    Bx = None
    By = None
    b = sqrt((Cx-Ax)**2 + (Cy-Ay)**2)
    if check_triangle(a,b,c):
        A = acos((c**2 + b**2 - a**2) / (2 * c * b)) # angle A (base angle between bicep and hypotenuse)
        #unit vector
        uACx = (Cx - Ax) / b
        uACy = (Cy - Ay) / b
        if alt:
            #rotated vector
            uABx = uACx * cos(A) - uACy * sin(A)
            uABy = uACx * sin(A) + uACy * cos(A)

            #B position uses length of edge
            Bx = Ax + c * uABx
            By = Ay + c * uABy
        else:
            #vector rotated into another direction
            uABx = uACx * cos(A) + uACy * sin(A)
            uABy = - uACx * sin(A) + uACy * cos(A)

            #second possible position
            Bx = Ax + c * uABx
            By = Ay + c * uABy
        #print(Ax, Ay, Bx, By, Cx, Cy)
        return (Bx, By)
    else:
        return (Cx, Cy) #if the lengths are not a valid triangle or lengths are negative, just don't update lines

def to_radians(angle):
    return angle * (pi / 180)

def arm_calc(alt_arm_config, temp_u, temp_v):
    # default configuration
    # make sure it stays in cylindrical bounds:
    # x^2 + y^2 <= 945.7103
    """
    These numbers are some kind of conversion between arm measurements and graph that plots the arm graphics
    30.75
    18.02
    17.8513 / 17.9505
    2.3858 / 1.4631
    160.6811
    77.8213
    99.3601
    168.5116
    85.8577
    2.91186
    549.3601
    540.3
    """

    if not alt_arm_config:

        # these basically keep the end point within the movement boundaries
        if(hypot(temp_u, temp_v) > 30.75):
            temp_u += temp_u*((30.75/hypot(temp_u, temp_v))-1)
            temp_v += temp_v*((30.75/hypot(temp_u, temp_v))-1)
            # x^2 + y^2 >= 324.6326
        if(hypot(temp_u, temp_v) < 18.02):
            temp_u += temp_u*((18.02/hypot(temp_u, temp_v))-1)
            temp_v += temp_v*((18.02/hypot(temp_u, temp_v))-1)
            # (x-17.8513)^2 + (y-2.3858)^2 <= 324.3601 ***only for the bottom part of the circle***
        if(hypot(temp_u-17.8513, temp_v-2.3858) > 18.01 and temp_v < 0):
            temp_u += (temp_u-17.8513) * \
                ((18.01/hypot((temp_u-17.8513), (temp_v-2.3858)))-1)
            temp_v += (temp_v-2.3858) * \
                ((18.01/hypot((temp_u-17.8513), (temp_v-2.3858)))-1)
            # (x-1.4631)^2 + (y-17.9505)^2 >= 324.3601
        if(hypot(temp_u-1.4631, temp_v-17.9505) < 18.01):
            temp_u += (temp_u-1.4631) * \
                ((18.01/hypot((temp_u-1.4631), (temp_v-17.9505)))-1)
            temp_v += (temp_v-17.9505) * \
                ((18.01/hypot((temp_u-1.4631), (temp_v-17.9505)))-1)

        # calculate the actuator lengths
        hypot2 = pow(temp_u, 2) + pow(temp_v, 2)
        x_len = sqrt(160.6811-77.8123*cos(acos((99.3601-hypot2) /
                     (-30.0*sqrt(hypot2))) + atan(temp_v/temp_u)+.40602))
        y_len = sqrt(
            168.5116-(85.8577*cos(2.91186-acos((hypot2-549.3601)/(-540.3)))))
    else:
        # configuration for the equipment servicing task
        # make sure it stays in cylindrical bounds:
        # x^2 + y^2 <= 956.4557
        if(hypot(temp_u, temp_v) > 30.93):
            temp_u += temp_u*((30.93/hypot(temp_u, temp_v))-1)
            temp_v += temp_v*((30.93/hypot(temp_u, temp_v))-1)
        # x^2 + y^2 >= 427.3300
        if(hypot(temp_u, temp_v) < 20.67):
            temp_u += temp_u*((20.67/hypot(temp_u, temp_v))-1)
            temp_v += temp_v*((20.67/hypot(temp_u, temp_v))-1)
        # (x-14.8678)^2 + (y-1.9870)^2 <= 324.3601 ***only for the bottom part of the circle***
        if(hypot(temp_u-14.8678, temp_v-1.9870) > 18.01 and temp_v < 0):
            temp_u += (temp_u-14.8678) * \
                ((18.01/hypot((temp_u-14.8678), (temp_v-1.9870)))-1)
            temp_v += (temp_v-1.9870) * \
                ((18.01/hypot((temp_u-14.8678), (temp_v-1.9870)))-1)
        # (x-1.2187)^2 + (y-14.9504)^2 >= 324.3601
        if(hypot(temp_u-1.2187, temp_v-14.9504) < 18.01):
            temp_u += (temp_u-1.2187) * \
                ((18.01/hypot((temp_u-1.2187), (temp_v-14.9504)))-1)
            temp_v += (temp_v-14.9504) * \
                ((18.01/hypot((temp_u-1.2187), (temp_v-14.9504)))-1)
        # the collision stuff doesnt work as well at such sharp corners
        if(temp_v > 0):
            if(temp_v > 27.5):
                temp_v = 27.5
            if(temp_u < 14.25):
                temp_u = 14.25

        # do inverse kinematics to find the length of each actuator based on the coordinate (u,v)
        hypot2 = pow(temp_u, 2) + pow(temp_v, 2)
        x_len = sqrt(160.6811-77.8123*cos(acos((99.3601-hypot2) /
                     (-30.0*sqrt(hypot2)))+atan(temp_v/temp_u)+.40602))
        y_len = sqrt(
            180.5948-(100.9791*cos(2.96241-acos((hypot2-549.3601)/(-540.3)))))

    return x_len, y_len, temp_u, temp_v


""" draw all the arm garbage on screen """
def draw_arm_stuff(screen, alt_arm_config, claw_x, claw_y):
    scale = 13
    origin_x = 150
    origin_y = 375
    bicep_len = 18.01*scale
    forearm_len = (30.75-18.01)*scale
    line_width = 4

    # origin
    pygame.draw.line(screen, BLACK, (origin_x-10, origin_y),
                     (origin_x+10, origin_y))
    pygame.draw.line(screen, BLACK, (origin_x, origin_y-10),
                     (origin_x, origin_y+10))

    if not alt_arm_config:
        """ bounds for default configuration """
        # painter.drawArc(origin_x-30.75*scale, origin_y-30.75*scale, 30.75*scale*2, 30.75*scale*2, -25*16, 80*16);
        r = pygame.rect.Rect(origin_x-30.75*scale, origin_y -
                             30.75*scale, 30.75*scale*2, 30.75*scale*2)
        pygame.draw.arc(screen, BLACK, r, -24*pi/180, 55*pi/180, line_width)
        # painter.drawArc(origin_x-18.02*scale, origin_y-18.02*scale, 18.02*scale*2, 18.02*scale*2, -60*16, 90*16);
        r = pygame.rect.Rect(origin_x-18.02*scale, origin_y -
                             18.02*scale, 18.02*scale*2, 18.02*scale*2)
        pygame.draw.arc(screen, BLACK, r, -52*pi/180, 25*pi/180, line_width)
        # painter.drawArc((origin.x()+17.8513*scale)-18.01*scale, (origin.y()-2.3858*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -120*16, 70*16);
        r = pygame.rect.Rect((origin_x+17.8513*scale)-18.01*scale,
                             (origin_y-2.3858*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2)
        pygame.draw.arc(screen, BLACK, r, -113*pi/180, -55*pi/180, line_width)
        # painter.drawArc((origin_x+1.4631*scale)-18.01*scale, (origin_y-17.9505*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -40*16, 65*16);
        r = pygame.rect.Rect((origin_x+1.4631*scale)-18.01*scale,
                             (origin_y-17.9505*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2)
        pygame.draw.arc(screen, BLACK, r, -36*pi/180, 24*pi/180, line_width)
    else:
        """ bounds for equipment servicing configuration """
        # painter.drawArc(origin_x-30.93*scale, origin_y-30.93*scale, 30.93*scale*2, 30.93*scale*2, -20*pi/180, 90*pi/180);
        r = pygame.rect.Rect(origin_x-30.93*scale, origin_y -
                             30.93*scale, 30.93*scale*2, 30.93*scale*2)
        pygame.draw.arc(screen, BLACK, r, -15*pi/180, 63*pi/180, line_width)
        # painter.drawArc(origin_x-20.67*scale, origin_y-20.67*scale, 20.67*scale*2, 20.67*scale*2, -60*pi/180, 90*pi/180);
        r = pygame.rect.Rect(origin_x-20.67*scale, origin_y -
                             20.67*scale, 20.67*scale*2, 20.67*scale*2)
        pygame.draw.arc(screen, BLACK, r, -51*pi/180, 27*pi/180, line_width)
        # painter.drawArc((origin_x+14.8678*scale)-18.01*scale, (origin_y-1.9870*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -100*pi/180, 70*pi/180);
        r = pygame.rect.Rect((origin_x+14.8678*scale)-18.01*scale,
                             (origin_y-1.9870*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2)
        pygame.draw.arc(screen, BLACK, r, -96*pi/180, -33*pi/180, line_width)
        # painter.drawArc((origin_x+1.2187*scale)-18.01*scale, (origin_y-14.9504*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -20*pi/180, 65*pi/180);
        r = pygame.rect.Rect((origin_x+1.2187*scale)-18.01*scale,
                             (origin_y-14.9504*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2)
        pygame.draw.arc(screen, BLACK, r, -20*pi/180, 45*pi/180, line_width)

    # pygame.draw.circle(screen, BLACK, (origin_x, origin_y), bicep_len, 1)
    # pygame.draw.circle(screen, BLACK, (origin_x+claw_x*scale, origin_y +
    #                  claw_y*scale), forearm_len, 1)

    # claw position
    pygame.draw.line(screen, BLACK, (origin_x+claw_x*scale-5, origin_y +
                     claw_y*scale-5), (origin_x+claw_x*scale+5, origin_y+claw_y*scale+5), width=3)
    pygame.draw.line(screen, BLACK, (origin_x+claw_x*scale-5, origin_y +
                     claw_y*scale+5), (origin_x+claw_x*scale+5, origin_y+claw_y*scale-5), width=3)

    # calculate coordinates for elbow joint so I know where to connect the two arm segments on GUI
    elbowJointPosition = calculate_third_corner(origin_x, origin_y, origin_x+claw_x*scale, origin_y+claw_y*scale, forearm_len, bicep_len)

    #draw line from origin to elbow, then from elbow to claw position. This should animate the actual position of the arm
    pygame.draw.line(screen, BLACK, (origin_x, origin_y), elbowJointPosition, width=7)
    pygame.draw.line(screen, BLACK, elbowJointPosition, (origin_x+claw_x*scale, origin_y+claw_y*scale), width=7)
    

"""
Currently displays each individual wheel and relative speed using controller inputs. Not implementing gimbal UI because 
  camera view should be enough.
"""
def draw_drive_stuff(screen, leftwheels, rightwheels):
    w,h = (800,600)#screen.get_size()
    c_x = w/2
    c_y =h/2
    y_spacing = c_y/1.5
    top_y = c_y - y_spacing
    left_x = c_x-c_x*.4
    bar_height = y_spacing*.4
    bar_width = 60
    for i in range(6):
        if i < 3:
            height = (leftwheels[i] - 126) / -126
        else:
            height = (rightwheels[i-3] - 126) / -126
        if height > 0:
            color = (abs(height*255),0,0)
        else:
            color = (0,abs(height)*255,0)
        x_coord = left_x + (c_x*.8 if i>2 else 0)
        y_coord = top_y + y_spacing * (i % 3)
        bound = pygame.rect.Rect(x_coord - bar_width/2, y_coord - bar_height,bar_width,bar_height*2)
        pygame.draw.line(screen, color, (x_coord, y_coord), (x_coord, y_coord+height*bar_height+1), int(bar_height-25))
        pygame.draw.rect(screen, BLACK, bound, 4, 1)


"""
This function draws all science UI using the inputs from the controller
For loop creates Actuator, Microscope and Claw rectangles and uses height variable to determine length of color bar.
 Editing what the colors bar do in the future will require messing with the height variable and pygame.draw.line functions.
"""
def draw_science_stuff(screen, speeds, tp):
    w,h = (800,600)#screen.get_size()
    labels = ['Actuator', 'Microscope Zoom', 'Claw']
    directions = ['Up', 'Down', 'Out', 'In', 'Open', 'Close']
    c_x = w/2
    c_y =h/2
    x_spacing = w/3.5
    left_x = c_x - x_spacing
    bar_height = h/4
    bar_width = 60
    for i in range(len(speeds)-1):
        s = speeds[i]
        x_coord = left_x + i * x_spacing
        y_coord = c_y
        height = (s / 127) - 1
        tp.printat(screen, labels[i], BLACK, (x_coord, y_coord - bar_height*1.2))
        tp.printat(screen, directions[i*2], BLACK, (x_coord-70, y_coord*.66))
        tp.printat(screen, directions[i*2+1], BLACK, (x_coord-70, y_coord*1.2))

        bound = pygame.rect.Rect(x_coord - bar_width/2, y_coord - bar_height,bar_width,bar_height*2)
        if i == 0: # actuator
            if s > 128:
                color = (255*abs(height), 0,0,0)
            else:
                color = (0, 255*abs(height),0,0)
            pygame.draw.line(screen, color, (x_coord, y_coord), (x_coord, y_coord+height*bar_height),bar_width)
        else:
            if i == 1: # microscope
                height = s/180
                color = (255*abs(height/2), 0,255*abs(height/2),0)
                pygame.draw.line(screen, color, (x_coord, y_coord-bar_height), (x_coord, y_coord-bar_height+abs(height)*2*bar_height),bar_width)
            else: # claw
                height = (s/90) - 1
                color = (0,0,255*abs(height),0)
                pygame.draw.line(screen, color, (x_coord, y_coord), (x_coord, y_coord+height*bar_height),bar_width)

        pygame.draw.rect(screen, BLACK, bound, 4, 1)
    s = speeds[3] #carousel
    width = s - 1
    bound = pygame.rect.Rect(left_x, c_y+bar_height*1.2,x_spacing*2,bar_width)
    if width != 0:
        pygame.draw.line(screen, GREEN, (c_x,c_y+bar_height*1.2+bar_width/2), (c_x+x_spacing*width,c_y+bar_height*1.2+bar_width/2), bar_width)
    pygame.draw.rect(screen, BLACK, bound, 4, 1)
    tp.printat(screen, 'Carousel', BLACK, (c_x, c_y + bar_height*1.4 + bar_width))



    

""" This is a helper class to draw text anywhere on the GUI """
class TextPrint(object):
    def __init__(self, size):
        self.reset()
        self.font = pygame.font.Font(None, size)

    def print(self, screen, text_string, color):
        textBitmap = self.font.render(text_string, True, color)
        screen.blit(textBitmap, (self.x, self.y))
        self.x += textBitmap.get_width()

    def println(self, screen, text_string, color):
        self.print(screen, text_string, color)
        self.y += self.line_height
    
    def printat(self, screen, text_string, color, coord):
        textBitmap = self.font.render(text_string, True, color)
        x_coord = coord[0] - textBitmap.get_width()/2
        y_coord = coord[1] - textBitmap.get_height()/2
        screen.blit(textBitmap, (x_coord, y_coord))


    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10
