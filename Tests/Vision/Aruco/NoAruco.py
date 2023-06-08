import os
import sys
import datetime

sys.path.insert(1, r'/')

from Utils.Control.cardalgo import *

initial_flag = 0

"""This Code is use to record a video"""
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"/home/roblab20/Desktop/videos/oron_videos/oron_{timestamp}.avi"
# frames_per_second = 60
res = '720p'

def change_res(cap, width, height):
    cap.set(3, width)
    cap.set(4, height)

# Standard Video Dimensions Sizes
STD_DIMENSIONS =  {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}

def get_dims(cap, res='1080p'):
    width, height = STD_DIMENSIONS["480p"]
    if res in STD_DIMENSIONS:
        width,height = STD_DIMENSIONS[res]
    ## change the current caputre device
    ## to the resulting resolution
    change_res(cap, width, height)
    return width, height


VIDEO_TYPE = {
    'avi': cv2.VideoWriter_fourcc(*'XVID'),
    #'mp4': cv2.VideoWriter_fourcc(*'H264'),
    'mp4': cv2.VideoWriter_fourcc(*'XVID'),
}

def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
      return  VIDEO_TYPE[ext]
    # return VIDEO_TYPE['mp4']
    return VIDEO_TYPE['avi']


"""This part responsible for the close loop control using CV2 circle detection"""
#==========================
#Defines camera parameters#
#==========================
cam = cv2.VideoCapture(0)
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter(filename, fourcc, 5, (640, 480))
out = cv2.VideoWriter(filename, get_video_type(filename), 8, get_dims(cam, res))
cam.set(3,1280)
cam.set(4,720)
# cam.set(cv2.CAP_PROP_AUTOFOCUS,0)

# start_time = time.time()
# times = []
# angles = []
# frame_numbers = []

## Set the card class and open the serial communication
mycard = Card(x_d=0,y_d=0,a_d=-1,x=-1,y=-1,a=-1,baud=115200,port='/dev/ttyACM0')
mycard.set_motor_angle(0.0001) ## it was 0.0001 ## Update the motor angle value
mycard.send_data(key='motor') ## Send data to the motor/ this func in package
algo = card_algorithms(x_d=0,y_d=0) # Define the card algorithm object


# Define the set desired paramter and tell the code that user didnt init it yet
set_des = 0


flag = 0

j = 0
while cam.isOpened():
    ret, img = cam.read()
    if ret:
        state_data = []
        circle_center, circle_radius = algo.detect_circle_info(img)
        aruco_centers, ids = algo.detect_aruco_centers(img)
        # print(circle_center, circle_radius)

        # algo.display_image(img, circle_center, circle_radius)
        # center, Img = algo.filter_camera(cam=cam, filter=3)
        # center, Img = algo.filter_camera(cam=cam, filter=3) ## Update the card center
        algo.finger_position(img,calibration=False) ## If Main axis system need calibartion change to True and calibrate the xy point
        # Capturing each frame of our video stream

        if set_des == 0: ## If user didnt input a value yet
            print("No des yet")

            algo.y_d = 227 ## 220
            algo.x_d = 668
            start = time.perf_counter()
            print('the goal position is', algo.x_d,algo.y_d)
            set_des = 1
            # print(set_des)

        elif circle_center is not None and set_des == 1: ## If the first card_center is not updated yet
            if (algo.card_initialize(circle_center)) == 1:
            # if (algo.card_initialize(circle_center[:-1], )) == 1:
                set_des = 2
                # print(set_des)
                mycard.vibrate_on()

        elif circle_center is not None:
            algo.plot_desired_position(img)
            algo.update(circle_center)
            # print('a',circle_center)
            # algo.update(circle_center.tolist())
            algo.plot_path(img)

            if ids is not None and len(ids) > 0:
                orientation_angle = algo.ids_to_angle(ids, circle_center, aruco_centers)
                # state_data.append((algo.path[:-1], algo.path[:-1], orientation_angle))
                # Draw arrowed line indicating orientation
                cv2.putText(img, f"Angle: {orientation_angle}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


            origin = tuple(algo.finger_position(img)) #green point on screen
            scale = 50
            # Define the endpoints of the X-axis and Y-axis relative to the origin
            x_axis_end = (origin[0] - int(scale), origin[1])
            y_axis_end = (origin[0], origin[1] - int(scale))

            # Draw coordinate system
            cv2.line(img, origin, x_axis_end, (0, 0, 0), 2)  # X-axis (red)
            cv2.line(img, origin, y_axis_end, (0, 0, 0), 2)

            # Draw coordinate system
            cv2.line(img, origin, x_axis_end, (0, 0, 0), 2)  # X-axis (red)
            cv2.line(img, origin, y_axis_end, (0, 0, 0), 2)  # Y-axis (green)

            if algo.check_distance(epsilon=10) is not True and set_des == 2: #there is a problem
                ## If you want to choose control law number 1
                output = algo.law_1()
                # print(algo.path)
                ###############################################

                mycard.set_encoder_angle(output) ## Update the motor output
                algo.plot_arrow(img) ## Plot the direction of motor
                mycard.send_data('encoder') ## Send the motor output to the hardware

                time.sleep(0.1)
            elif algo.check_distance(10) is True:
                print('arive to the goal', algo.path[-1])
                for i in range(30):
                    mycard.send_data('vibrate')

                    set_des = 3

            if set_des == 3:
                time.sleep(3) # a delay of a sec between each iteration

                for i in range(30):

                    mycard.send_data('st') # or set des 3 or this is stop the vibration
                # mycard.send_data('st')
                # time.sleep(1)
                algo.next_iteration()
                j = j + 1
                # print(j)
                algo.package_data()


                # algo.clear()
                # with open('state_data.txt', 'w') as file:
                #     for state in state_data:
                #         file.write(f"{state[0]}, {state[1]}, {state[2]}\n")
                algo.random_input()
                print('the new goal is',algo.random_input())
                set_des = 2

            # time.sleep(0.1)
            # algo.draw_circle(self,Img,ret)
            # algo.detect_aruco_centers(img)
            # algo.display_image(img, circle_center, circle_radius)
            # algo.draw_circle(Img, center)
            # algo.detect_circle(self,Img,ret)
            # print("output")
            # print("set des is" , set_des)
            out.write(img)
            algo.display_image(img, circle_center, circle_radius)
        # cv2.imshow('QueryImage', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('Interupt by user')
            break
        if cv2.waitKey(1) & 0xFF == ord('i'):
            algo.position_user_input(img)

cam.release()
out.release()
cv2.destroyAllWindows()
# plt.show()