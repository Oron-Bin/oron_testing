import numpy as np
import cv2


cam = cv2.VideoCapture(0)
cam.set(3,1280)
cam.set(4,720)
cam.set(cv2.CAP_PROP_AUTOFOCUS,0)


while cam.isOpened():
    aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)

    # Create the ArUco parameters
    aruco_params = cv2.aruco.DetectorParameters_create()


    # Capturing each frame of our video stream
    ret, Img = cam.read()
    gray = cv2.cvtColor(Img, cv2.COLOR_BGR2GRAY) #create an img with a gray scale
    gray_blurred = cv2.blur(gray, (8,8)) #blur the img
    corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)

    if ret: #a boolian that tells if there is a call from the camera
        circles = cv2.HoughCircles(gray_blurred,
                   cv2.HOUGH_GRADIENT, 1.5, 1000,minRadius=50, maxRadius=300)
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
            # loop over the (x, y) coordinates and radius of the circles
            for (x, y, r) in circles:
                circle_center = (x, y)
                print("x is",x,"y is", y,"radius is", r)
                angle = 0
                if ids is not None:

                    for i in range(len(ids)):
                        aruco_center = np.mean(corners[i][0], axis=0)
                        # print('aruco',aruco_center)
                    print('ids is:',ids)
                    print('the center of id number',ids[-1],'is',aruco_center)
                        # print(np.mean(corners[-1][0], axis=0))
                    dx = circle_center[0] - aruco_center[0]
                    dy = circle_center[1] - aruco_center[1]
                    angle = np.degrees(np.arctan2(dy, dx))
                    axis_x = (circle_center[0]-50,circle_center[1])
                    axis_y = (circle_center[0], circle_center[1] -50)
                    cv2.arrowedLine(
                        Img,
                        tuple(circle_center),
                        axis_x,
                        (0, 0, 0),  # Red color
                        2,  # Thickness of the arrowed line
                        tipLength=0.2
                    )
                    cv2.arrowedLine(
                        Img,
                        tuple(circle_center),
                        axis_y,
                        (0, 0, 0),  # Red color
                        2,  # Thickness of the arrowed line
                        tipLength=0.2
                    )
                    print('the last ids that detected is:',ids[-1],'and the first orientation between him and the camera is', angle)

                    if ids[-1] == 43 : #define that 43 is the head of the arrow orientation
                        angle = np.degrees(np.arctan2(dy, dx))

                        cv2.arrowedLine(
                            Img,
                            tuple(circle_center),
                            tuple(aruco_center),
                            (0, 0, 255),  # Red color
                            2,  # Thickness of the arrowed line
                            tipLength=0.2
                        )

                        # matplotlib.pyplot.arrow(circle_center[0], circle_center[1], dx_43, dy_43, **kwargs) #to do - fill the arrow
                    elif ids[-1] == 44:
                        # dx = circle_center[0] - aruco_center[0]
                        # dy = circle_center[1] - aruco_center[1]
                        angle += 180
                        # arrow_head_y = (round(aruco_center[0]), round(aruco_center[1] - 110))
                        # cv2.arrowedLine(
                        #     Img,
                        #     tuple(circle_center),
                        #     arrow_head_y,
                        #     (0, 0, 255),  # Red color
                        #     3,  # Thickness of the arrowed line
                        #     tipLength=0.2
                        # )
                        # angle = np.degrees(np.arctan2(dy, dx)) +180
                    elif ids[-1] == 45:
                        # dx = circle_center[0] - aruco_center[0]
                        # dy = circle_center[1] - aruco_center[1]
                        angle += 90
                        # arrow_head_y = (round(aruco_center[0]), round(aruco_center[1]))
                        # cv2.arrowedLine(
                        #     Img,
                        #     tuple(circle_center),
                        #     arrow_head_y,
                        #     (0, 0, 255),  # Red color
                        #     3,  # Thickness of the arrowed line
                        #     tipLength=0.2
                        # )
                    elif ids[-1] == 46:
                        angle -= 90

                    if angle < 0:
                        angle += 360
                    print('the orientation is:', angle)
                else:
                    print('ids is none')
                    angle = angle


                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(Img, (x, y), r, (0, 255 ,0), 4) # the color is in RGB and the last parameter is the thickness
                cv2.rectangle(Img, (x - 1, y - 1), (x + 1, y + 1), (0, 255, 0), -1) #thickness of -1 means to fill the rectangle
        cv2.imshow('QueryImage', Img)
        cv2.waitKey(1) #shows continuous live video

        # plt.imshow(cv2.cvtColor(Img, cv2.COLOR_BGR2RGB))
        # plt.axis('off')
        # plt.show()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('Interupt by user')
            break







