"""
ui.py — Funzioni per il rendering dell'interfaccia sovraimpressa sul frame.
Gestisce HUD, barra filtri, indicatori e testo di aiuto.
"""

import cv2
import numpy as np
import time


#font = cv2.FONT_HERSHEY_SIMPLEX
font = cv2.FONT_HERSHEY_TRIPLEX


def draw_hud(frame, filter_name, num_faces, fps, recording=False, auto_mode=False):
    """
    Sovrimprime sul frame:
    - nome del filtro attivo
    - numero di facce rilevate
    - FPS correnti
    - indicatore di registrazione (se attivo)
    - indicatore modalità automatica (se attiva)
    """
    img = frame.copy()
    h, w = img.shape[:2]

    # Sfondo semitrasparente per il testo HUD (angolo in alto a sinistra)
    overlay = img.copy()
    cv2.rectangle(overlay, (8, 8), (220, 70), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.45, img, 0.55, 0, img)

    overlay = img.copy()
    cv2.rectangle(overlay, (8, 75), (130, 107), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.45, img, 0.55, 0, img)

    # Testo HUD
    cv2.putText(img, f"Filtro: {filter_name}", (16, 32),
                font, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(img, f"Facce: {num_faces}", (16, 58),
                font, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(img, f"FPS: {fps:.1f}", (16, 97),
                font, 0.65, (255, 255, 255), 1, cv2.LINE_AA)

    # Indicatore REC
    if recording:
        cv2.circle(img, (w - 30, 28), 10, (0, 0, 220), -1)
        cv2.putText(img, "REC", (w - 75, 34),
                    font, 0.7, (0, 0, 220), 2, cv2.LINE_AA)

    # Indicatore modalità automatica
    if auto_mode:
        cv2.putText(img, "AUTO", (w - 80, 60),
                    font, 0.6, (0, 220, 220), 2, cv2.LINE_AA)

    return img


def draw_filter_bar(frame, filter_keys, active_index):
    """
    Mostra in basso una barra con tutti i filtri disponibili,
    evidenziando quello attivo con uno sfondo colorato.
    """
    img = frame.copy()
    h, w = img.shape[:2]
    bar_h = 36
    bar_y = h - bar_h

    # Sfondo barra
    overlay = img.copy()
    cv2.rectangle(overlay, (0, bar_y), (w, h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.65, img, 0.35, 0, img)

    n = len(filter_keys)
    slot_w = w // n

    for i, name in enumerate(filter_keys):
        x1 = i * slot_w
        x2 = x1 + slot_w
        cx = (x1 + x2) // 2

        if i == active_index:
            # Evidenzia il filtro attivo
            cv2.rectangle(img, (x1 + 2, bar_y + 2), (x2 - 2, h - 2), (0, 180, 255), -1)
            color = (20, 20, 20)
        else:
            color = (200, 200, 200)

        label = name[:7]  # abbrevia se troppo lungo
        tw = cv2.getTextSize(label, font, 0.45, 1)[0][0]
        cv2.putText(img, label, (cx - tw // 2, bar_y + 24),
                    font, 0.45, color, 1, cv2.LINE_AA)

    return img


def draw_help(frame):
    """
    Mostra un pannello di aiuto semitrasparente con tutti i tasti disponibili.
    """
    img = frame.copy()
    h, w = img.shape[:2]

    lines = [
        "TASTI DISPONIBILI",
        "---------------------------------",
        "F / Freccia destra  — filtro successivo",
        "Freccia sinistra    — filtro precedente",
        "B  - blur sfondo on/off",
        "M  - rilevamento movimento on/off",
        "G  - ghost effect on/off",
        "C  - cappello on/off",
        "L  - motion blur on/off",
        "R  - inizia/ferma registrazione",
        "A  - modalita automatica on/off",
        "S  - screenshot",
        "H  - mostra/nascondi aiuto",
        "Q  - esci",
    ]

    box_w, box_h = 420, len(lines) * 26 + 24
    bx = (w - box_w) // 2
    by = (h - box_h) // 2

    overlay = img.copy()
    cv2.rectangle(overlay, (bx, by), (bx + box_w, by + box_h), (10, 10, 10), -1)
    cv2.addWeighted(overlay, 0.82, img, 0.18, 0, img)
    cv2.rectangle(img, (bx, by), (bx + box_w, by + box_h), (0, 180, 255), 1)

    for i, line in enumerate(lines):
        color = (0, 200, 255) if i == 0 else (220, 220, 220)
        size = 0.55 if i == 0 else 0.48
        cv2.putText(img, line, (bx + 14, by + 24 + i * 26),
                    font, size, color, 1, cv2.LINE_AA)

    return img


def draw_screenshot_flash(frame):
    """Lampeggio bianco brevissimo per feedback visivo dello screenshot."""
    img = frame.copy()
    overlay = np.ones_like(img) * 255
    cv2.addWeighted(overlay, 0.35, img, 0.65, 0, img)
    return img
