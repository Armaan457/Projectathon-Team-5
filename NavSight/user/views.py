import threading
from django.http import StreamingHttpResponse
from django.shortcuts import render
import cv2
from ultralytics import YOLO
import math
from django.views.decorators import gzip

# Create your views here.

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

@gzip.gzip_page
def yolo(request):
    try:
        model = YOLO("yolov9s.pt")

        classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
                    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
                    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
                    "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
                    "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
                    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
                    "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
                    "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
                    "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
                    "teddy bear", "hair drier", "toothbrush"]
        
        cam = VideoCamera()

        def gen(camera):
            res = set()
            while True:
                success, img = camera.video.read()
                if not success:
                    break

                results = model(img, stream=True, conf = 0.7)

                for r in results:
                    boxes = r.boxes

                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)

                        cls = int(box.cls[0])
                        res.add(classNames[cls])
                        print(res)

                        org = [x1, y1-7]
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        fontScale = 1
                        color = (255, 0, 0)
                        thickness = 2

                        cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness)
                    

                        _ , jpeg = cv2.imencode('.jpg', img)
                        frame = jpeg.tobytes()
                        yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                    
        return StreamingHttpResponse(gen(cam), content_type='multipart/x-mixed-replace; boundary=frame')

    except:
        print("An error occured")
        pass
    
    return render(request, 'yolo.html')