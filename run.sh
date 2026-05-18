# Script di avvio per progetto-webcam qwertyuiop
# Installa le dipendenze (se necessario) e avvia l'applicazione.

set -e

PYTHON=python3

echo "=== Filtri Webcam in Real Time ==="

# Controlla che Python sia disponibile
if ! command -v "$PYTHON" &>/dev/null; then
    echo "Errore: python3 non trovato. Installalo."
    exit 1
fi

# Installa dipendenze se mancano
echo "Installazione dipendenze..."
$PYTHON -m pip install --quiet -r requirements.txt

# Avvia l'app
echo "Avvio webcam... (H = lista comandi, Q = termina programma)"
$PYTHON main.py
