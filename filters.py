"""
filters.py — Filtri visivi applicabili al frame della webcam.
Ogni funzione riceve il frame come primo parametro e restituisce il frame modificato.
Non viene modificato il frame originale: si lavora sempre su una copia.
"""

import cv2
import numpy as np


def apply_grayscale(frame):
    """Converte il frame in scala di grigi (3 canali per compatibilità)."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def apply_negative(frame):
    """Inverte i colori del frame (effetto negativo fotografico)."""
    return cv2.bitwise_not(frame.copy())


def apply_sepia(frame):
    """Applica un tono seppia caldo simulando una fotografia vintage."""
    img = frame.copy().astype(np.float32)
    r = img[:, :, 2] * 0.393 + img[:, :, 1] * 0.769 + img[:, :, 0] * 0.189
    g = img[:, :, 2] * 0.349 + img[:, :, 1] * 0.686 + img[:, :, 0] * 0.168
    b = img[:, :, 2] * 0.272 + img[:, :, 1] * 0.534 + img[:, :, 0] * 0.131
    sepia = np.stack([
        np.clip(b, 0, 255),
        np.clip(g, 0, 255),
        np.clip(r, 0, 255)
    ], axis=2).astype(np.uint8)
    return sepia


def apply_heatmap(frame):
    """Converte il frame in scala di grigi e applica una colormap termica INFERNO."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)


def apply_cartoon(frame):
    """
    Effetto fumetto: bilateral filter per appiattire i colori
    + bordi Canny sovrapposti in nero.
    """
    img = frame.copy()
    for _ in range(3):
        img = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1=50, threshold2=150)
    edges_inv = cv2.bitwise_not(edges)
    edges_colored = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
    return cv2.bitwise_and(img, edges_colored)


def apply_pixelate(frame, pixel_size=12):
    """Rimpicciolisce il frame e lo riingrandisce con nearest — effetto pixel art."""
    h, w = frame.shape[:2]
    small = cv2.resize(frame, (w // pixel_size, h // pixel_size),
                       interpolation=cv2.INTER_LINEAR)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def apply_vignette(frame):
    """
    Scurisce progressivamente i bordi del frame
    con una maschera circolare sfumata costruita con NumPy.
    """
    img = frame.copy()
    h, w = img.shape[:2]
    cx, cy = w // 2, h // 2
    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    max_dist = np.sqrt(cx ** 2 + cy ** 2)
    mask = 1.0 - np.clip(dist / (max_dist * 0.75), 0, 1)
    mask = mask[:, :, np.newaxis]
    return np.clip(img * mask, 0, 255).astype(np.uint8)


def apply_mirror(frame):
    """Capovolgimento orizzontale in real time — modalità selfie."""
    return cv2.flip(frame.copy(), 1)


# Registro dei filtri: nome → funzione
# Usato da main.py per ciclare i filtri con i tasti
FILTERS = {
    "normale":   lambda f: f.copy(),
    "grigio":    apply_grayscale,
    "negativo":  apply_negative,
    "sepia":     apply_sepia,
    "heatmap":   apply_heatmap,
    "cartoon":   apply_cartoon,
    "pixelate":  apply_pixelate,
    "vignetta":  apply_vignette,
    "specchio":  apply_mirror,
}

FILTER_KEYS = list(FILTERS.keys())
