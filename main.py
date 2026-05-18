"""
main.py — Loop principale dell'applicazione.
Gestisce: acquisizione webcam, tasti, filtri attivi, effetti, HUD e screenshot.

Tasti:
  F / →       filtro successivo
  ←           filtro precedente
  B           blur sfondo on/off
  M           rilevamento movimento on/off
  G           ghost effect on/off
  L           motion blur simulato on/off
  R           avvia/ferma registrazione video
  A           modalità automatica (ciclo filtri ogni N secondi)
  S           screenshot
  H           mostra/nascondi pannello aiuto
  Q / ESC     esci
"""

import cv2
import time
import datetime
import os

from filters import FILTERS, FILTER_KEYS
from effects import (
    detect_faces,
    apply_background_blur,
    apply_overlay_png,
    apply_motion_detection,
    apply_ghost_effect,
    apply_motion_blur,
)
from ui import (
    draw_hud,
    draw_filter_bar,
    draw_help,
    draw_screenshot_flash,
)

# ── Configurazione ─────────────────────────────────────────────────────────────

SCREENSHOTS_DIR = "screenshots"
RECORDINGS_DIR = "recordings"
AUTO_MODE_INTERVAL = 4       # secondi tra un filtro e l'altro in modalità auto
WEBCAM_INDEX = 0             # indice della webcam (0 = predefinita)
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# ── Stato applicazione ─────────────────────────────────────────────────────────

filter_index = 0
blur_bg_on = False
motion_on = False
ghost_on = False
motion_blur_on = False
recording = False
auto_mode = False
show_help = False
hat_on = False

prev_frame = None
video_writer = None
flash_frames = 0           # fotogrammi rimasti di flash screenshot

fps = 0.0
fps_counter = 0
fps_timer = time.time()

auto_timer = time.time()


def get_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def start_recording(width, height):
    """Crea un VideoWriter per la registrazione su file .mp4."""
    filename = os.path.join(RECORDINGS_DIR, f"rec_{get_timestamp()}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
    print(f"[REC] Registrazione avviata: {filename}")
    return writer


def stop_recording(writer):
    """Rilascia il VideoWriter e chiude il file."""
    if writer is not None:
        writer.release()
        print("[REC] Registrazione salvata.")
    return None


# ── Loop principale ────────────────────────────────────────────────────────────

cap = cv2.VideoCapture(WEBCAM_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

if not cap.isOpened():
    print("Errore: impossibile aprire la webcam.")
    exit(1)

print("Webcam avviata. Premi H per i comandi, Q per uscire.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Errore: frame non ricevuto dalla webcam.")
        break

    # ── FPS ──────────────────────────────────────────────────────────────────
    fps_counter += 1
    elapsed = time.time() - fps_timer
    if elapsed >= 0.5:
        fps = fps_counter / elapsed
        fps_counter = 0
        fps_timer = time.time()

    # ── Modalità automatica ───────────────────────────────────────────────────
    if auto_mode and (time.time() - auto_timer) >= AUTO_MODE_INTERVAL:
        filter_index = (filter_index + 1) % len(FILTER_KEYS)
        auto_timer = time.time()

    # ── Face detection (una volta per frame, riutilizzata da tutti gli effetti)
    faces = detect_faces(frame)

    # ── Pipeline filtri ───────────────────────────────────────────────────────
    output = FILTERS[FILTER_KEYS[filter_index]](frame)

    if blur_bg_on:
        output = apply_background_blur(output, faces)

    if ghost_on:
        output = apply_ghost_effect(output, prev_frame)

    if motion_blur_on:
        output = apply_motion_blur(output)

    if motion_on:
        output = apply_motion_detection(output, prev_frame)

    if hat_on and len(faces) > 0:
        output = apply_overlay_png(output, faces, "assets/cappello.png", position="top")

    # ── HUD e barra filtri ────────────────────────────────────────────────────
    output = draw_hud(output, FILTER_KEYS[filter_index],
                      len(faces), fps, recording, auto_mode)
    output = draw_filter_bar(output, FILTER_KEYS, filter_index)

    if show_help:
        output = draw_help(output)

    if flash_frames > 0:
        output = draw_screenshot_flash(output)
        flash_frames -= 1

    # ── Registrazione ─────────────────────────────────────────────────────────
    if recording and video_writer is not None:
        video_writer.write(output)

    # ── Aggiorna prev_frame ───────────────────────────────────────────────────
    prev_frame = frame.copy()

    # ── Mostra frame ──────────────────────────────────────────────────────────
    cv2.imshow("Webcam Filtri | H = aiuto | Q = esci", output)

    # ── Gestione tasti ────────────────────────────────────────────────────────
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q") or key == 27:           # Q / ESC → esci
        break

    elif key == ord("f") or key == 83:         # F / → → filtro successivo
        filter_index = (filter_index + 1) % len(FILTER_KEYS)

    elif key == 81:                             # ← → filtro precedente
        filter_index = (filter_index - 1) % len(FILTER_KEYS)

    elif key == ord("b"):                       # B → blur sfondo
        blur_bg_on = not blur_bg_on
        print(f"[BLUR BG] {'ON' if blur_bg_on else 'OFF'}")

    elif key == ord("m"):                       # M → rilevamento movimento
        motion_on = not motion_on
        print(f"[MOTION] {'ON' if motion_on else 'OFF'}")

    elif key == ord("g"):                       # G → ghost effect
        ghost_on = not ghost_on
        print(f"[GHOST] {'ON' if ghost_on else 'OFF'}")

    elif key == ord("l"):                       # L → motion blur simulato
        motion_blur_on = not motion_blur_on
        print(f"[MOTION BLUR] {'ON' if motion_blur_on else 'OFF'}")

    elif key == ord("r"):                       # R → registrazione
        if not recording:
            h_cap = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            w_cap = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            video_writer = start_recording(w_cap, h_cap)
            recording = True
        else:
            video_writer = stop_recording(video_writer)
            recording = False

    elif key == ord("a"):                       # A → modalità automatica
        auto_mode = not auto_mode
        auto_timer = time.time()
        print(f"[AUTO] {'ON' if auto_mode else 'OFF'}")

    elif key == ord("s"):                       # S → screenshot
        path = os.path.join(SCREENSHOTS_DIR, f"screenshot_{get_timestamp()}.jpg")
        cv2.imwrite(path, output)
        flash_frames = 3
        print(f"[SCREENSHOT] Salvato: {path}")

    elif key == ord("h"):                       # H → aiuto
        show_help = not show_help

    elif key == ord("c"):   # C → cappello on/off
        hat_on = not hat_on
        print(f"[CAPPELLO] {'ON' if hat_on else 'OFF'}")


# ── Cleanup ────────────────────────────────────────────────────────────────────
if recording:
    stop_recording(video_writer)

cap.release()
cv2.destroyAllWindows()
print("App chiusa correttamente.")
