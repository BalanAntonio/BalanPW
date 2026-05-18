"""
effects.py — Effetti visivi che sfruttano face detection e frame consecutivi.
Ogni funzione riceve il frame come primo parametro e restituisce il frame modificato.
Non viene modificato il frame originale: si lavora su una copia se necessario.
"""

import cv2
import numpy as np
import os

# Carica il classificatore Haar per il rilevamento volti
_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
_EYE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_eye.xml"

face_cascade = cv2.CascadeClassifier(_CASCADE_PATH)
eye_cascade = cv2.CascadeClassifier(_EYE_CASCADE_PATH)


def detect_faces(frame):
    """
    Rileva le facce nel frame usando Haar cascade.
    Restituisce la lista di bounding box (x, y, w, h).
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )
    return faces if len(faces) > 0 else []


def apply_background_blur(frame, faces):
    """
    Applica GaussianBlur forte su tutto il frame tranne le regioni delle facce,
    che restano nitide. Richiede la lista di facce già rilevate.
    """
    img = frame.copy()
    blurred = cv2.GaussianBlur(img, (55, 55), 0)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for (x, y, w, h) in faces:
        pad_x = int(w * 0.15)
        pad_y = int(h * 0.15)
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(img.shape[1], x + w + pad_x)
        y2 = min(img.shape[0], y + h + pad_y)
        cv2.ellipse(mask, ((x1 + x2) // 2, (y1 + y2) // 2),
                    ((x2 - x1) // 2, (y2 - y1) // 2), 0, 0, 360, 255, -1)
    mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    mask_inv = cv2.bitwise_not(mask_3ch)
    sharp_faces = cv2.bitwise_and(img, mask_3ch)
    blurred_bg = cv2.bitwise_and(blurred, mask_inv)
    return cv2.add(sharp_faces, blurred_bg)


def apply_overlay_png(frame, faces, png_path, position="top"):
    """
    Sovrappone un PNG con canale alpha sopra ogni faccia rilevata.
    position: 'top' per cappello, 'eyes' per occhiali, 'bottom' per barba.
    """
    if not os.path.exists(png_path):
        return frame.copy()
    overlay_img = cv2.imread(png_path, cv2.IMREAD_UNCHANGED)
    if overlay_img is None or overlay_img.shape[2] < 4:
        return frame.copy()

    img = frame.copy()
    for (x, y, w, h) in faces:
        ov_w = int(w * 1.4)
        ov_h = int(ov_w * overlay_img.shape[0] / overlay_img.shape[1])
        resized = cv2.resize(overlay_img, (ov_w, ov_h))

        if position == "top":
            oy = y - ov_h + int(h * 0.1)
            ox = x + (w - ov_w) // 2
        elif position == "eyes":
            oy = y + int(h * 0.25)
            ox = x + (w - ov_w) // 2
        else:  # bottom
            oy = y + int(h * 0.55)
            ox = x + (w - ov_w) // 2

        # Clamp alle dimensioni del frame
        fx1 = max(0, ox)
        fy1 = max(0, oy)
        fx2 = min(img.shape[1], ox + ov_w)
        fy2 = min(img.shape[0], oy + ov_h)
        if fx2 <= fx1 or fy2 <= fy1:
            continue
        rx1 = fx1 - ox
        ry1 = fy1 - oy
        rx2 = rx1 + (fx2 - fx1)
        ry2 = ry1 + (fy2 - fy1)

        roi = img[fy1:fy2, fx1:fx2]
        ov_roi = resized[ry1:ry2, rx1:rx2]
        alpha = ov_roi[:, :, 3:4].astype(np.float32) / 255.0
        bg = roi.astype(np.float32)
        fg = ov_roi[:, :, :3].astype(np.float32)
        img[fy1:fy2, fx1:fx2] = np.clip(fg * alpha + bg * (1 - alpha), 0, 255).astype(np.uint8)
    return img


def apply_face_label(frame, faces, label="🎥 Utente"):
    """Scrive un'etichetta personalizzata sopra ogni faccia rilevata."""
    img = frame.copy()
    for (x, y, w, h) in faces:
        cv2.putText(img, label, (x, max(y - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 200), 2, cv2.LINE_AA)
    return img


def apply_motion_detection(frame, prev_frame):
    """
    Confronta frame consecutivi con absdiff e colora in rosso le zone
    che cambiano oltre una certa soglia (rilevamento movimento).
    """
    img = frame.copy()
    if prev_frame is None:
        return img
    diff = cv2.absdiff(prev_frame, frame)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_diff, 25, 255, cv2.THRESH_BINARY)
    thresh_3ch = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    motion_mask = np.zeros_like(img)
    motion_mask[:, :, 2] = thresh  # canale rosso
    return cv2.addWeighted(img, 1.0, motion_mask, 0.5, 0)


def apply_ghost_effect(frame, prev_frame, alpha=0.4):
    """
    Sovrappone il frame corrente con una versione pesata del frame precedente
    per ottenere un effetto scia/fantasma.
    """
    if prev_frame is None:
        return frame.copy()
    return cv2.addWeighted(frame, 1.0 - alpha, prev_frame, alpha, 0)


def apply_motion_blur(frame, strength=15):
    """
    Applica un blur direzionale orizzontale con un kernel personalizzato
    che simula il mosso fotografico.
    """
    img = frame.copy()
    kernel = np.zeros((strength, strength))
    kernel[strength // 2, :] = np.ones(strength) / strength
    return cv2.filter2D(img, -1, kernel)
