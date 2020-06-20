import tensorflow as tf
import numpy as np
import cv2 as cv
from time import sleep
from threading import Thread, Event

raspberry = False

traffic_light = {
    'red':    { 'pin': 17, 'status': 0 },
    'yellow': { 'pin': 27, 'status': 0 },
    'green':  { 'pin': 22, 'status': 0 }
}

if raspberry:

    import RPi.GPIO as GPIO    

    GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
    GPIO.setup(traffic_light['red']['pin'], GPIO.OUT)
    GPIO.setup(traffic_light['yellow']['pin'], GPIO.OUT)
    GPIO.setup(traffic_light['green']['pin'], GPIO.OUT)

thread_started = False

def load_labels(path):
    with open(path, 'r') as f:
        return [line.strip() for line in f.readlines()]

def change_signal_light(color):
    global thread_started
    global raspberry
    thread_started = True
    print('Iniciando troca de cor para: ' + color)
    sleep(5)
    if raspberry:
        GPIO.output(GPIO.output(traffic_light['red']['pin'], GPIO.LOW))
        GPIO.output(GPIO.output(traffic_light['green']['pin'], GPIO.HIGH))
    print('Troca de cor do semaforo concluida com sucesso')
    thread_started = False
        

cap = cv.VideoCapture(0)

labels = load_labels('labelmap.txt')
interpreter = tf.lite.Interpreter('detect.tflite')

interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

output_data = interpreter.get_tensor(output_details[0]['index'])

if labels[0] == '???':
    del(labels[0])

threshold = 0.4
imW, imH = 640, 480
desired_labels = ['car', 'truck', 'motorcycle', 'bike']
vehicles_offset = 4
people_offset = 4

threads = []


while True:

    _, frame = cap.read()    
    frame = frame.copy()

    key = cv.waitKey(2) & 0xFF
    
    frame_rgb = frame.copy()
    frame_resized = cv.resize(frame_rgb, (300, 300))    

    input_data = np.expand_dims(frame_resized, axis=0)
    input_data = (2.0 / 255.0) * input_data - 1.0
    input_data = input_data.astype('float32')

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
    classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
    scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
    # num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)
    
    objects = []

    for i in range(len(scores)):

        if ((scores[i] > threshold) and (scores[i] <= 1.0)):

            
            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            ymin = int(max(1,(boxes[i][0] * imH)))
            xmin = int(max(1,(boxes[i][1] * imW)))
            ymax = int(min(imH,(boxes[i][2] * imH)))
            xmax = int(min(imW,(boxes[i][3] * imW)))
            
            cv.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 200, 0), 2)

            # Draw label
            object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index

            if object_name in desired_labels:
                objects.append(object_name)
                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv.FILLED) # Draw white box to put label text in
                cv.putText(frame, label, (xmin, label_ymin-7), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

    cv.putText(frame, 
        f'Numero de Objetos detectados {len(objects)}', 
        (10, 30), 
        cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 100), 2) # Draw label text

    if len(objects) >= vehicles_offset:
        if not thread_started:
            x = Thread(target=change_signal_light, args=('red',))
            x.start()
        # Apos 3 segundos mudar o semaforo de carros para verde        

    cv.imshow('Main', frame)
    
    if key == ord('q'):
        break


cap.release()
cv.destroyAllWindows()