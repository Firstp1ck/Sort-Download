import os
import shutil

# Pfad zu Ihrem Download-Ordner (bitte anpassen)
download_path = 'C:\Users\hdlea\Downloads'

# Zielordner für verschiedene Dateitypen
ordner_paths = {
    'Bilder': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
    'Videos': ['mp4', 'mov', 'wmv', 'flv', 'avi', 'mkv', 'webm'],
    'Dokumente': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'odt'],
    'Musik': ['mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a']
}

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
                break

print("Sortierung abgeschlossen.")
