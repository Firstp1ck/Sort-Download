import json
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import logging
import functools
import concurrent.futures
from functools import partial

# Setup logging
logging.basicConfig(filename='file_organizer.log', level=logging.DEBUG,  # Changed from INFO to DEBUG
                    format='%(asctime)s - %(levelname)s - %(message)s')

def retry(operation):
    """A decorator to retry a function upon encountering a specific set of exceptions."""
    @functools.wraps(operation)
    def wrapper(*args, **kwargs):
        retries = 3
        delay = 2  # Delay in seconds
        while retries > 0:
            try:
                return operation(*args, **kwargs)
            except (IOError, shutil.Error) as e:
                logging.warning(f"Error during operation '{operation.__name__}': {e}, retries left: {retries}")
                time.sleep(delay)
                retries -= 1
        logging.error(f"All retries failed for operation '{operation.__name__}'")
    return wrapper

class FileOrganizer:
    def __init__(self, config_path):
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        self.download_path = config['download_path']
        self.ordner_paths = config['ordner_paths']

    def is_file_accessible(self, filepath):
        try:
            with open(filepath, 'rb+', buffering=0):
                return True
        except IOError:
            return False

    def generate_unique_filename(self, target_path, filename):
        base, extension = os.path.splitext(filename)
        counter = 1
        while os.path.exists(target_path):
            target_path = os.path.join(os.path.dirname(target_path), f"{base}_{counter}{extension}")
            counter += 1
        return target_path
    
    @retry
    def move_file(self, src, dst):
        """Moves a file from src to dst. Retries on failure."""
        shutil.move(src, dst)

    def organize_file(self, filename):
        """Organize a single file based on its extension."""
        logging.debug(f"Attempting to organize file: {filename}")  # Added debug log
        src = os.path.join(self.download_path, filename)
        if os.path.isfile(src) and self.is_file_accessible(src):
            _, extension = os.path.splitext(filename)
            extension = extension.lower().strip('.')
            matched = False  # Flag to check if a match was found
            for ordner, extensions in self.ordner_paths.items():
                if extension in extensions:
                    matched = True
                    logging.debug(f"File {filename} matched category {ordner} with extension {extension}")  # Added debug log
                    ziel_pfad = os.path.join(self.download_path, ordner, filename)
                    ziel_pfad = self.generate_unique_filename(ziel_pfad, filename)
                    os.makedirs(os.path.dirname(ziel_pfad), exist_ok=True)
                    try:
                        self.move_file(src, ziel_pfad)
                        logging.info(f"Moved: {filename} -> {ziel_pfad}")
                    except Exception as e:
                        logging.error(f"Failed to move {filename}: {e}")
                    break  # Exit after finding the first match
            if not matched:
                logging.debug(f"No category match found for file: {filename} with extension: {extension}")  # Added debug log


    def organize_files(self):
        """Organize files using multiple threads."""
        files = [f for f in os.listdir(self.download_path) if os.path.isfile(os.path.join(self.download_path, f))]
        logging.debug(f"Found {len(files)} files for initial organization")  # Added debug log
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.organize_file, file) for file in files]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()  # You can handle results or exceptions here
                    # Optionally log each file processed successfully
                except Exception as e:
                    logging.error(f"Error organizing files: {e}")

class DownloadHandler(FileSystemEventHandler):
    def __init__(self, organizer):
        self.organizer = organizer

    def on_modified(self, event):
        organizer.organize_files()

if __name__ == "__main__":
    config_path = 'config.json'  # Path to the configuration file
    organizer = FileOrganizer(config_path)

    # Process existing files at startup
    organizer.organize_files()

    # Setup the event handler and observer for continuous monitoring
    event_handler = DownloadHandler(organizer)
    observer = Observer()
    observer.schedule(event_handler, organizer.download_path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
