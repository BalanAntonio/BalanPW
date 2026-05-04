import cv2

face_cascade = cv2.CascadeClassifier('/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml')

 
cap = cv2.VideoCapture(0)
filtro = 'normale'  # 'normale', 'grigio', 'bordi', 'blur'
 
while True:
    ret, frame = cap.read()
    if not ret:
        break
 
    # Applica il filtro scelto
    if filtro == 'grigio':
        output = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    elif filtro == 'bordi':
        grigio = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        output = cv2.Canny(grigio, 50, 150)
    elif filtro == 'blur':
        output = cv2.GaussianBlur(frame, (21, 21), 0)
    elif filtro == 'termo':
        output = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
    elif filtro == 'faccia':
        grigio = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Trova le facce: restituisce lista di (x, y, w, h)
        facce = face_cascade.detectMultiScale(grigio, scaleFactor=1.1, minNeighbors=4)

    # Disegna un rettangolo per ogni faccia trovata
        for (x, y, w, h) in facce:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, 'Faccia', (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Conta le facce rilevate
        cv2.putText(frame, f'Facce: {len(facce)}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        output = frame
        
    else:
        output = frame
 
    cv2.imshow('Webcam', output)
 
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    elif key == ord('1'): filtro = 'normale'
    elif key == ord('2'): filtro = 'grigio'
    elif key == ord('3'): filtro = 'bordi'
    elif key == ord('4'): filtro = 'blur'
    elif key == ord('5'): filtro = 'termo'
    elif key == ord('6'): filtro = 'faccia'

 
cap.release()
cv2.destroyAllWindows()

