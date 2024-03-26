import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

# Pfad zu Ihrem Download-Ordner (bitte anpassen)
download_path = r'C:\Users\hdlea\Downloads'

# Zielordner für verschiedene Dateitypen
ordner_paths = {
    'Bilder': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
    'Videos': ['mp4', 'mov', 'wmv', 'flv', 'avi', 'mkv', 'webm'],
    'Dokumente': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'odt', "xlsm", "xltx", "xls", "dotx"],
    'Musik': ['mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a']
}

class DownloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Pfad zu Ihrem Download-Ordner (bitte anpassen)
        download_path = r'C:\Users\hdlea\Downloads'
        
        # Prüfen Sie jede Datei im Download-Ordner
        for filename in os.listdir(download_path):
            src = f"{download_path}/{filename}"

# Zielordner erstellen, falls nicht vorhanden
for ordner in ordner_paths:
    os.makedirs(os.path.join(download_path, ordner), exist_ok=True)

# Durchlaufen aller Dateien im Download-Ordner
for datei in os.listdir(download_path):
    # Vollständiger Pfad zur Datei
    voller_dateipfad = os.path.join(download_path, datei)
    
    # Überprüfen, ob es eine Datei ist
    if os.path.isfile(voller_dateipfad):
        # Dateierweiterung extrahieren und in Kleinbuchstaben konvertieren
        _, extension = os.path.splitext(datei)
        extension = extension.lower().strip('.')

        # Entscheiden, wohin die Datei verschoben werden soll
        for ordner, extensions in ordner_paths.items():
            if extension in extensions:
                ziel_pfad = os.path.join(download_path, ordner, datei)
                
                # Verschieben der Datei
                shutil.move(voller_dateipfad, ziel_pfad)
                print(f"Verschoben: {datei} -> {ziel_pfad}")

if __name__ == "__main__":
    path = r'C:\Users\hdlea\Downloads'  # Ihr Download-Ordner
    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


print("Sortierung abgeschlossen.")
