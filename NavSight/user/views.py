from django.http import StreamingHttpResponse
from django.shortcuts import render ,redirect
import cv2
from ultralytics import YOLO
from django.views.decorators import gzip
from transformers import BlipProcessor, BlipForConditionalGeneration
from django.shortcuts import render
from django.contrib.auth.models import User , auth
from django.contrib import messages

# Create your views here.
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

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


@gzip.gzip_page
def blip(request):
    try:
        cam = VideoCamera()
        def gen(camera):
            success, img = camera.video.read()
            if success: 
                processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
                model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

                image = img

                inputs = processor(image, return_tensors="pt")

                out = model.generate(**inputs)
                print(processor.decode(out[0], skip_special_tokens=True))

                _ , jpeg = cv2.imencode('.jpg', img)
                frame = jpeg.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        return StreamingHttpResponse(gen(cam), content_type='multipart/x-mixed-replace; boundary=frame')

    except:
        print("An error occured")
        pass
    
    return render(request, 'blip.html')


from django.http import HttpResponse , HttpRequest
from .models import UniqueID

def members(request):
  return render(request , "index1.html" )

def home(request):
  return render(request , "welcome_page.html")

def id(request):
  return render(request ,"uniqueid_create.html")

def log_signup(request):
  return render (request , "login_signup.html")

from django.contrib import messages, auth

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            request.session['username'] = username
            return redirect('uniqueid2')  # Replace 'uniqueid2' with your actual URL name or path
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('login')  # Replace 'login' with your actual login page URL name or path
    else:
        return render(request, 'login.html')
    


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already in use.')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'Registration successful. Please log in.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

         
def number(request):
  total = request.POST['name']
  totalw = len(total.split())
  context ={
    "total":totalw
  }
  return render(request , "number.html" ,context)

import json
import requests
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def uniqueid1(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            # Get the client's public IP address
            response = requests.get('https://api64.ipify.org?format=json')
            ip = response.json().get('ip')
            
            # Check if the IP already has a unique ID
            unique_id_obj = UniqueID.objects.filter(ip=ip).first()
            if unique_id_obj:
                # If IP already has a unique ID, return it
                response_data = {
                    'status': 'success',
                    'latitude': unique_id_obj.latitude,
                    'longitude': unique_id_obj.longitude,
                    'ip': unique_id_obj.ip,
                    'unique_id': unique_id_obj.unique_id
                }
            else:
                # Generate a new unique ID
                new_unique_id = generate_unique_id()
                
                # Save new unique ID to the database
                unique_id_obj = UniqueID.objects.create(
                    unique_id=new_unique_id,
                    latitude=latitude,
                    longitude=longitude,
                    ip=ip
                )
                
                # Return the newly generated unique ID
                response_data = {
                    'status': 'success',
                    'latitude': latitude,
                    'longitude': longitude,
                    'ip': ip,
                    'unique_id': new_unique_id
                }
            
            return JsonResponse(response_data)
        
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    
    elif request.method == 'GET':
        # Render a form or generate a unique ID for testing
        unique_id = generate_unique_id()
        return render(request, "uniqueid_create.html", {"uniqueid": unique_id})
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, statu0s=405)

def generate_unique_id():
    # Generate a random unique ID
    return str(random.randint(100000, 999999))

def uniqueid2(request):
    if request.method == 'POST':
        unique_id = request.POST.get('uniqueid')

        if UniqueID.objects.filter(unique_id=unique_id).exists():
            request.session['unique_id'] = unique_id
            return redirect('navigatorhome')  # Redirect to 'navigatorhome' if UniqueID exists
        else:
            messages.error(request, 'Invalid ID')  # Display error message if UniqueID does not exist

    return render(request, 'unique_id_enter.html')
def navigatorhome(request):
   username = request.session.get('username')
   unique_id = request.session.get('unique_id')
   context = {
       "username":username,
        "unique_id":unique_id,
   }
   return render(request , "navigator.html" , context)

def location(request):
   unique_id = request.session.get('unique_id')

   if unique_id:
        # Query the UniqueID model for the given unique_id
        try:
            unique_id_obj = UniqueID.objects.get(unique_id=unique_id)
            unique_id_data = {
                'unique_id': unique_id_obj.unique_id,
                'created_at': unique_id_obj.created_at,
                'latitude': unique_id_obj.latitude,
                'longitude': unique_id_obj.longitude,
            }
        except UniqueID.DoesNotExist:
            unique_id_data = None
   else:
        unique_id_data = None
        
   return render(request , "location.html")