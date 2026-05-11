import cv2
import time
import numpy as np

face_cascade = cv2.CascadeClassifier('/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
filtro = 'normale'  # 'normale', 'grigio', 'bordi', 'blur', 'sfocato_sfondo'

_,primo = cap.read()

ys,xs, _ = primo.shape

tempo = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    if filtro == 'grigio':
        output = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    elif filtro == 'bordi':
        grigio = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        output = cv2.Canny(grigio, 20, 50)

    elif filtro == 'blur':
        output = cv2.GaussianBlur(frame, (21, 21), 0)

    elif filtro == 'termo':
        output = cv2.applyColorMap(frame, cv2.COLORMAP_JET)

    elif filtro == 'faccia':
        grigio = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        facce = face_cascade.detectMultiScale(grigio, scaleFactor=1.1, minNeighbors=4)
        for (x, y, w, h) in facce:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, 'Faccia', (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f'Facce: {len(facce)}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        output = frame

    elif filtro == 'sfocato_sfondo':
        grigio = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        facce = face_cascade.detectMultiScale(grigio, scaleFactor=1.1, minNeighbors=4)
        
        sfocato = cv2.GaussianBlur(frame, (51, 51), 30)          
        maschera = np.zeros(frame.shape[:2], dtype=np.uint8)
        
        for (x, y, w, h) in facce:
            cv2.rectangle(maschera, (x, y), (x+w, y+h), 255, -1)
        
        output = cv2.bitwise_and(frame, frame, mask=maschera)
        sfocato_maschera = cv2.bitwise_and(sfocato, sfocato, mask=cv2.bitwise_not(maschera))
        output = cv2.add(output, sfocato_maschera)
        
        for (x, y, w, h) in facce:
            cv2.putText(output, f'Facce: {len(facce)}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    else:
        output = frame

 
    fps = int(1/(time.time() - tempo))


    cv2.putText(output, f'FPS: {fps}', (10, ys-10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


    cv2.imshow('Webcam', output)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('1'):
        filtro = 'normale'
    elif key == ord('2'):
        filtro = 'grigio'
    elif key == ord('3'):
        filtro = 'bordi'
    elif key == ord('4'):
        filtro = 'blur'
    elif key == ord('5'):
        filtro = 'termo'
    elif key == ord('6'):
        filtro = 'faccia'
    elif key == ord('7'):  
        filtro = 'sfocato_sfondo'
    tempo = time.time()

cap.release()
cv2.destroyAllWindows()   
