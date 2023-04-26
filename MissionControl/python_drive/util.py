from math import hypot, sqrt, cos, sin, atan, atan2, acos, pi, dist
from turtle import distance
import pygame
from pygame import gfxdraw
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

pygame.display.init() # Initialize display module
pygame.display.set_mode((1200,600)) # width/ height of window in pixels
initialize = True

baseImage = pygame.image.load("backgroundPics\\RotatingBase.png")
bicepImage = pygame.image.load("backgroundPics\\ProximalMemberandActuators.png")
bicepImage = pygame.transform.rotate(bicepImage, -90)

forearmImage = pygame.image.load("backgroundPics\\DistalMember.png")
wristAndClawImage = pygame.image.load("backgroundPics\\WristAndClaw.png")
armBackground = pygame.image.load("backgroundPics\\armBackground.png")

bicepLength = 30 # in inches
forearmLength = 30 
bicepAngle = 0
forearmAngle = 0

scale = 13
origin_x = 150
origin_y = 375
# bicep_len = 18.01*scale
# forearm_len = (30.75-18.01)*scale
line_width = 4


bicep_len = 15*scale
forearm_len = 15.5*scale
oldX = 18.5
oldY = 9.5

oldIK = False

armBoundaries = pygame.image.load("backgroundPics\\armBoundaries.png")


# this function will remap a value from one range to another. ex: map(5, 0, 10, 0, 100) will return 50
def val_map(value, fromLow, fromHigh, toLow, toHigh):
    # Figure out how 'wide' each range is
    leftSpan = fromHigh - fromLow
    rightSpan = toHigh - toLow

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - fromLow) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return toLow + (valueScaled * rightSpan)

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

    global oldX
    global oldY
    global bicepAngle
    global forearmAngle

    y = -temp_v*scale
    x = temp_u*scale

    if alt_arm_config == 0:

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
            
    elif alt_arm_config==1:
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
    
    if(oldIK):

        # alt_arm_config == 2 removes GUI boundaries
        # calculate the actuator lengths - good luck making sense of this
        hypot2 = pow(temp_u, 2) + pow(temp_v, 2)
        x_len = sqrt(160.6811-77.8123*cos(acos((99.3601-hypot2) /
                        (-30.0*sqrt(hypot2))) + atan(temp_v/temp_u)+.40602))
        y_len = sqrt(
            168.5116-(85.8577*cos(2.91186-acos((hypot2-549.3601)/(-540.3)))))
        
        shoulder_length = int(round((x_len-9.69)*(95/3.93))+40) & 0xff
        elbow_length = int(round((y_len-9.69)*(95/3.93))+40) & 0xff
        return shoulder_length, elbow_length, temp_u, temp_v # old implementation
    
    else:
    # CALCULATE ANGLES BASED ON END EFFECTOR
        # This math is the geometric implementation of a 2-joint arm based on resources found online
        hypotenuse = sqrt(pow(y, 2) + pow(x, 2))
        forearmAngle = acos((hypotenuse**2 - bicep_len**2 - forearm_len**2 )/(2*bicep_len*forearm_len))
        bicepAngle = -(atan2(y,x) - atan2((forearm_len*sin(forearmAngle)),(bicep_len+(forearm_len*cos(forearmAngle))))) * (180/pi)
        forearmAngle = 180-(forearmAngle * (180/pi))

        # prevents the arm from going in a bad spot and damage itself
        if(forearmAngle > 130 or forearmAngle < 30 or bicepAngle < 13 or bicepAngle > 83): 
            temp_u = oldX 
            temp_v = oldY
        else: 
            oldX = temp_u
            oldY = temp_v

        # CONVERT ANGLES TO SERVO OUTPUTS BY REMAPING VALUES
        b = int(val_map(bicepAngle, 13, 83, 0, 180)) # bicep can move between 13 and 83 degrees from x-axis (ground)
        f = int(val_map(forearmAngle, 30, 130, 180, 0)) # forearm inner angle can move between 30 and 130 degrees from bicep
        if(b < 0): b = 0
        if(b > 180): b = 180
        if(f < 0): f = 0
        if(f > 180): f = 180
        #print(shoulder_length, elbow_length, b, f, bicepAngle, forearmAngle, temp_u, temp_v)

        return b, f, temp_u, temp_v # new implementation


""" draw all the arm garbage on screen """
def draw_arm_stuff(screen, alt_arm_config, claw_x, claw_y):
    global initialize
    global bicepImage
    global bicepAngle
    global forearmAngle
    if(initialize):
        bicepImage = bicepImage.convert_alpha()
        bicepImage.set_at((200, 120), (0, 0, 0, 0))
        initialize = False

    len = 30.5
    #print(origin_x+claw_x*scale, origin_y+claw_y*scale)

    # origin
    pygame.draw.line(screen, BLACK, (origin_x-10, origin_y),
                     (origin_x+10, origin_y))
    pygame.draw.line(screen, BLACK, (origin_x, origin_y-10),
                     (origin_x, origin_y+10))

    if alt_arm_config == 0:
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

    elif alt_arm_config == 1:
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
    else:
        """ bounds for default configuration """
        screen.blit(armBoundaries, (0,0))
        #pygame.gfxdraw.pixel(screen, int(origin_x+claw_x*scale), int(origin_y+claw_y*scale), BLACK)
        #pygame.draw.line(screen, BLACK, (0, 527), (700, 527), width=2)
        # # painter.drawArc(origin_x-30.75*scale, origin_y-30.75*scale, 30.75*scale*2, 30.75*scale*2, -25*16, 80*16);
        # r = pygame.rect.Rect(origin_x-len*scale, origin_y -
        #                      len*scale, len*scale*2, len*scale*2)
        # pygame.draw.arc(screen, BLACK, r, -24*pi/180, 55*pi/180, line_width) # big arc

        # # painter.drawArc(origin_x-18.02*scale, origin_y-18.02*scale, 18.02*scale*2, 18.02*scale*2, -60*16, 90*16);
        # r = pygame.rect.Rect(origin_x-bicep_len, origin_y -
        #                      bicep_len, bicep_len*2, bicep_len*2)
        # pygame.draw.arc(screen, BLACK, r, -52*pi/180, 25*pi/180, line_width) # bottom arc

        # # painter.drawArc((origin.x()+17.8513*scale)-18.01*scale, (origin.y()-2.3858*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -120*16, 70*16);
        # r = pygame.rect.Rect((origin_x+17.8513*scale)-bicep_len,
        #                      (origin_y-2.3858*scale)-bicep_len, bicep_len*2, 18.01*scale*2)
        # pygame.draw.arc(screen, BLACK, r, -113*pi/180, -55*pi/180, line_width) # floor arc

        # #painter.drawArc((origin_x+1.4631*scale)-18.01*scale, (origin_y-17.9505*scale)-18.01*scale, 18.01*scale*2, 18.01*scale*2, -40*16, 65*16);
        # r = pygame.rect.Rect(origin_x+bicep_len,
        #                      (origin_y-bicep_len), bicep_len*2, bicep_len*2) #left,top,height,width
        # pygame.draw.arc(screen, BLACK, r, -20*pi/180, 65*pi/180, line_width) # top arc

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
    
    # calculate position and rotation angle of bicep image
    x, y = midpoint(origin_x, origin_y, elbowJointPosition[0], elbowJointPosition[1])
    moddedbicepImage, bicepRect = rot_center(bicepImage, 90+bicepAngle, x, y)
    # same idea for forearm image but getting the angle of the image takes more geometry. forearmAngle is the angle between the bicep and forearmm
    #    the image needs the angle that the forearm makes with the ground. make a right triangle using the ground and do theta = acos(adjacent/hypotenuse)
    x, y = midpoint(elbowJointPosition[0], elbowJointPosition[1], origin_x+claw_x*scale, origin_y+claw_y*scale)
    d = distance(x, y, origin_x+claw_x*scale, y)
    phi = distance(x, y, origin_x+claw_x*scale, origin_y+claw_y*scale)
    theta = -acos(d/phi)*(180/pi)
    # look at the acos graph online or print theta before this if() to see why this theta correction is needed
    if(origin_x+claw_x*scale < x): theta = 180-theta
    if(origin_y+claw_y*scale < y): theta = -theta

    moddedforearmImage, forearmRect = rot_center(forearmImage, theta, x, y) 

    moddedWristAndClawImage, wristAndClawRect = rot_center(wristAndClawImage, theta, origin_x+claw_x*scale, origin_y+claw_y*scale)
    # add arm pictures to GUI
    screen.blits(((baseImage, (origin_x-75, origin_y-20)), (moddedbicepImage, bicepRect), (moddedforearmImage, forearmRect), (moddedWristAndClawImage, wristAndClawRect)))

def rot_center(image, angle, x, y):
    
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect

def midpoint(x1,y1, x2,y2):
    return ((x1+x2)/2, (y1+y2)/2)

def distance(x1, y1, x2, y2):
    dist = sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist

def cosine_angle(x1, y1, x2, y2, x3, y3):
    # Calculate the lengths of the sides of the triangle
    a = sqrt((x2 - x3)**2 + (y2 - y3)**2)
    b = sqrt((x1 - x3)**2 + (y1 - y3)**2)
    c = sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    # Find the angle opposite to vertex 1 (assuming it's the right angle)
    if a > b and a > c:
        cos_angle = b / a
    elif b > a and b > c:
        cos_angle = a / b
    else:
        cos_angle = c / a
    
    return cos(cos_angle)
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
    labels = ['Actuator', 'Microscope Zoom', 'Fan']
    directions = ['Up', 'Down', 'Out', 'In', 'On', 'Off']
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
