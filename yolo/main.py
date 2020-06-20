# -*- coding: utf-8 -*-

import cv2 as cv 

VIDEO_SRC = 0 # Take via arguments

if __name__ == '__main__':

    cap = cv.VideoCapture(VIDEO_SRC)
    
    while True and cap.isOpened():

        _, frame = cap.read()

        cv.imshow('Main', frame)

        if cv.waitKey(1) == ord('q') & 0xFF:
            break

    cap.release()
    cv.destroyAllWindows()
