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
    'Dokumente': {
        'PDFs': ['pdf'],
        'Word': ['doc', 'docx', "dotx"],
        'Excel': ['xls', 'xlsx', "xlsm", "xltx", "xls"]
    },
    'Musik': ['mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a']
}

def is_file_accessible(filepath):
    """Prüft, ob die Datei von keinem anderen Prozess verwendet wird und daher verschoben werden kann."""
    try:
        with open(filepath, 'rb+', buffering=0):
            return True
    except IOError:
        return False

def generate_unique_filename(target_path, filename):
    """Generiert einen einzigartigen Dateinamen, wenn eine Datei mit demselben Namen bereits existiert."""
    base, extension = os.path.splitext(filename)
    counter = 1
    while os.path.exists(target_path):
        target_path = os.path.join(os.path.dirname(target_path), f"{base}_{counter}{extension}")
        counter += 1
    return target_path

class DownloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        time.sleep(2)  # Kurze Verzögerung
        for filename in os.listdir(download_path):
            src = os.path.join(download_path, filename)
            if os.path.isfile(src) and is_file_accessible(src):
                _, extension = os.path.splitext(filename)
                extension = extension.lower().strip('.')
                for ordner, extensions in ordner_paths.items():
                    ziel_pfad = None
                    if isinstance(extensions, dict):  # Hat Unterordner
                        for subordner, subextensions in extensions.items():
                            if extension in subextensions:
                                ziel_pfad = os.path.join(download_path, ordner, subordner, filename)
                                break
                    elif extension in extensions:
                        ziel_pfad = os.path.join(download_path, ordner, filename)

                    if ziel_pfad:
                        ziel_pfad = generate_unique_filename(ziel_pfad, filename)
                        os.makedirs(os.path.dirname(ziel_pfad), exist_ok=True)
                        shutil.move(src, ziel_pfad)
                        print(f"Verschoben: {filename} -> {ziel_pfad}")
                        break

if __name__ == "__main__":
    for ordner, extensions in ordner_paths.items():
        if isinstance(extensions, dict):  # Hat Unterordner
            for subordner in extensions:
                os.makedirs(os.path.join(download_path, ordner, subordner), exist_ok=True)
        else:
            os.makedirs(os.path.join(download_path, ordner), exist_ok=True)

    path = download_path
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
