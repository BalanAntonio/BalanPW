#!/usr/bin/env bash
# run.sh — Script di avvio per progetto-webcam
# Installa le dipendenze (se necessario) e avvia l'applicazione.

set -e

PYTHON=python3

echo "=== Filtri Webcam in Real Time ==="

# Controlla che Python sia disponibile
if ! command -v "$PYTHON" &>/dev/null; then
    echo "Errore: python3 non trovato. Installalo prima di procedere."
    exit 1
fi

# Installa dipendenze se mancano
echo "Installazione dipendenze..."
$PYTHON -m pip install --quiet -r requirements.txt

# Avvia l'app
echo "Avvio webcam... (premi H per i comandi, Q per uscire)"
$PYTHON main.py
