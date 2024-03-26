from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time

class DownloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Pfad zu Ihrem Download-Ordner (bitte anpassen)
        download_path = 'C:/Users/IhrBenutzername/Downloads'
        
        # Prüfen Sie jede Datei im Download-Ordner
        for filename in os.listdir(download_path):
            src = f"{download_path}/{filename}"
            
            # Fügen Sie Ihre Logik hier ein, um die Datei zu verschieben
            # Beispiel: Wenn es ein Bild ist, verschieben Sie es in den Bilder-Ordner
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                bilder_path = f"{download_path}/Bilder"
                os.makedirs(bilder_path, exist_ok=True)
                dest = f"{bilder_path}/{filename}"
                os.rename(src, dest)
                print(f"Verschoben: {filename} -> {dest}")

if __name__ == "__main__":
    path = 'C:/Users/IhrBenutzername/Downloads'  # Ihr Download-Ordner
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
