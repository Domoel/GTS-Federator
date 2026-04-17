# Dockerfile
FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Abhängigkeiten kopieren und installieren
# Sicherstellen, dass requirements.txt im Repo existiert (Inhalt: requests)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- JETZT MIT UNTERSTRICH ---
# Kopiere das Skript aus deinem Repository in das Image
COPY gts_holmirdas.py .
# -----------------------------

# Datenverzeichnis für Persistenz (falls das Skript dort etwas speichert)
RUN mkdir -p /app/data

# Non-Root User für die Sicherheit
RUN useradd -r -u 1000 holmirdas
RUN chown -R holmirdas:holmirdas /app

# Wechsel zum User
USER holmirdas

# Startbefehl (ebenfalls mit Unterstrich)
CMD ["python", "gts_holmirdas.py"]
