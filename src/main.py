import cv2
import mediapipe as mp 
import math
import time
from picamera2 import Picamera2
import RPi.GPIO as GPIO

# Configuração do GPIO para o buzzer
GPIO.setmode(GPIO.BCM)
led_green = 27
led_red = 17
buzzer_pin = 18  
GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.setup(led_green, GPIO.OUT)
GPIO.setup(led_red, GPIO.OUT)

# Inicializar Picamera2
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (1000, 720)})
picam2.configure(camera_config)
picam2.start()

mpFaceMesh = mp.solutions.face_mesh
faceMesh = mpFaceMesh.FaceMesh()
mp_drawing = mp.solutions.drawing_utils
inicio = 0
status = ""

try:
    while True:
        img = picam2.capture_array()

        if img is None:
            print("Falha ao capturar a imagem. Pulando este quadro.")
            continue

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

        if img.shape[2] != 3:
            print("A imagem capturada não contém três canais BGR. Pulando este quadro.")
            continue

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = faceMesh.process(imgRGB)
        h, w, _ = img.shape
        if results.multi_face_landmarks:

            # Rosto detectado
            GPIO.output(led_green, GPIO.HIGH) 
            GPIO.output(led_red, GPIO.LOW)
            
            for face in results.multi_face_landmarks:
               
                # Olho direito
                di1_supx, di1_supy = int((face.landmark[160].x) * w), int((face.landmark[160].y) * h)
                di1_infx, di1_infy = int((face.landmark[144].x) * w), int((face.landmark[144].y) * h)
                di2_supx, di2_supy = int((face.landmark[159].x) * w), int((face.landmark[159].y) * h)
                di2_infx, di2_infy = int((face.landmark[145].x) * w), int((face.landmark[145].y) * h)
                di3_supx, di3_supy = int((face.landmark[158].x) * w), int((face.landmark[158].y) * h)
                di3_infx, di3_infy = int((face.landmark[153].x) * w), int((face.landmark[153].y) * h)

                # Olho esquerdo
                es1_supx, es1_supy = int((face.landmark[387].x) * w), int((face.landmark[387].y) * h)
                es1_infx, es1_infy = int((face.landmark[373].x) * w), int((face.landmark[373].y) * h)
                es2_supx, es2_supy = int((face.landmark[386].x) * w), int((face.landmark[386].y) * h)
                es2_infx, es2_infy = int((face.landmark[374].x) * w), int((face.landmark[374].y) * h)
                es3_supx, es3_supy = int((face.landmark[385].x) * w), int((face.landmark[385].y) * h)
                es3_infx, es3_infy = int((face.landmark[380].x) * w), int((face.landmark[380].y) * h)
                
                # Distancia entre os pontos
                distDi1 = math.hypot(di1_supx - di1_infx, di1_supy - di1_infy)
                distDi2 = math.hypot(di2_supx - di2_infx, di2_supy - di2_infy)
                distDi3 = math.hypot(di3_supx - di3_infx, di3_supy - di3_infy)
                distEs1 = math.hypot(es1_supx - es1_infx, es1_supy - es1_infy)
                distEs2 = math.hypot(es2_supx - es2_infx, es2_supy - es2_infy)
                distEs3 = math.hypot(es3_supx - es3_infx, es3_supy - es3_infy)
                
                situacao = "A"
                if (distDi1 <= 8 and distEs1 <= 8) and (distDi2 <= 10 and distEs2 <= 10) and (distDi3 <= 8 and distEs3 <= 8): 
                    situacao = "F"
                    if situacao != status:
                        inicio = time.time()

                if situacao == "F":
                    tempo = int(time.time() - inicio)
                else:
                    inicio = time.time()
                    tempo = int(time.time() - inicio)

                status = situacao

                # Olhos fechados por mais de 3s
                if tempo >= 3:
                    # Acionar o buzzer
                    GPIO.output(buzzer_pin, GPIO.HIGH)
                else:
                    # Desligar o buzzer
                    GPIO.output(buzzer_pin, GPIO.LOW)
        else:
            # Rosto não detectado
            GPIO.output(led_red, GPIO.HIGH)
            GPIO.output(led_green, GPIO.LOW)
            GPIO.output(buzzer_pin, GPIO.LOW)

        cv2.imshow('IMG', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
finally:
    GPIO.output(buzzer_pin, GPIO.LOW)
    GPIO.cleanup()
    picam2.stop()
    cv2.destroyAllWindows()