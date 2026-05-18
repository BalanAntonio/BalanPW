# Filtri Webcam in Real Time

Applicazione desktop Python che accede alla webcam e permette di applicare filtri visivi, effetti e overlay in tempo reale, controllabili da tastiera.

---

## Requisiti

| Componente | Versione minima |
|---|---|
| Python | 3.9+ |
| Sistema operativo | Linux, macOS, Windows |
| Hardware | Webcam USB o integrata |

---

## Installazione

### 1. Clona il repository

```bash
git clone https://github.com/tuo-utente/progetto-webcam.git
cd progetto-webcam
```

### 2. (Consigliato) Crea un ambiente virtuale

```bash
python3 -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows
```

### 3. Installa le dipendenze

```bash
pip install -r requirements.txt
```

---

## Come avviare

### Metodo rapido (Linux/macOS)

```bash
chmod +x run.sh
./run.sh
```

### Metodo manuale

```bash
python3 main.py
```

---

## Tasti disponibili

| Tasto | Azione |
|---|---|
| `F` / `→` | Filtro successivo |
| `←` | Filtro precedente |
| `B` | Blur sfondo on/off (richiede volto in campo) |
| `M` | Rilevamento movimento on/off |
| `G` | Ghost effect (scia) on/off |
| `L` | Motion blur simulato on/off |
| `R` | Avvia / ferma registrazione video (.mp4) |
| `A` | Modalità automatica (cicla filtri ogni 4 s) |
| `S` | Screenshot con filtri applicati (.jpg) |
| `H` | Mostra / nascondi pannello aiuto |
| `Q` / `ESC` | Esci |

---

## Filtri disponibili

| Numero | Nome | Descrizione |
|---|---|---|
| 0 | Normale | Nessun effetto |
| 1 | Grigio | Scala di grigi |
| 2 | Negativo | Inversione colori |
| 3 | Sepia | Tono vintage caldo |
| 4 | Heatmap | Colormap termica INFERNO |
| 5 | Cartoon | Bilateral filter + bordi Canny |
| 6 | Pixelate | Effetto pixel art |
| 7 | Vignetta | Bordi scuriti con maschera ellittica |
| 8 | Specchio | Flip orizzontale (selfie mode) |

---

## Output generati

- **Screenshots** → cartella `screenshots/` — nome formato `screenshot_YYYYMMDD_HHMMSS.jpg`
- **Registrazioni** → cartella `recordings/` — nome formato `rec_YYYYMMDD_HHMMSS.mp4`

---

## Struttura del progetto

```
progetto-webcam/
├── main.py          # Loop principale, gestione tasti, orchestrazione
├── filters.py       # Filtri colore (grigio, negativo, cartoon...)
├── effects.py       # Effetti con face detection e frame consecutivi
├── ui.py            # HUD, barra filtri, overlay testo
├── requirements.txt
├── run.sh
└── assets/          # PNG con canale alpha per overlay (cappello, occhiali...)
```

---

## Note per Raspberry Pi

```bash
# Installa le dipendenze di sistema (headless OpenCV)
sudo apt update
sudo apt install -y python3-pip python3-venv libatlas-base-dev libopencv-dev

# Crea l'ambiente virtuale e installa i package Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Avvia
python3 main.py
```

- Se la webcam non viene rilevata, prova a cambiare `WEBCAM_INDEX = 1` in `main.py`.
- Su Raspberry Pi 4 la performance è accettabile; effetti pesanti come `cartoon` possono ridurre gli FPS. Disattiva gli effetti non necessari.
- Per display headless (senza monitor), installa un server X oppure usa `--no-gui` mode con VNC.
- La registrazione `.mp4` richiede il codec `mp4v` disponibile di default con OpenCV.
