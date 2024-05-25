import tkinter as tk
from tkinter import ttk
import json
import os
import shutil
import logging
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import functools
import concurrent.futures

# Setup logging
logging.basicConfig(filename='file_organizer.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def retry(operation):
    @functools.wraps(operation)
    def wrapper(*args, **kwargs):
        retries = 3
        delay = 2
        while retries > 0:
            try:
                return operation(*args, **kwargs)
            except (IOError, shutil.Error) as e:
                logging.warning(f"Error during '{operation.__name__}': {e}, retries left: {retries}")
                time.sleep(delay)
                retries -= 1
        logging.error(f"Failed all retries for '{operation.__name__}'")
    return wrapper

class FileOrganizer(FileSystemEventHandler):
    def __init__(self, config_path):
        try:
            with open(config_path, 'r') as config_file:
                self.config = json.load(config_file)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse config file: {e}")
            raise
        except FileNotFoundError:
            logging.error(f"Config file not found: {config_path}")
            raise

        self.download_path = self.config.get('download_path', '')
        self.folder_paths = self.config.get('folder_paths', {})

    def flatten_folder_paths(self, folder_paths):
        flat_paths = {}
        for key, value in folder_paths.items():
            if isinstance(value, dict):
                for sub_key, extensions in value.items():
                    flat_paths[f"{key}\\{sub_key}"] = extensions
            else:
                flat_paths[key] = value
        return flat_paths

    @retry
    def move_file(self, src, dst):
        shutil.move(src, dst)

    def organize_file(self, filename):
        src = os.path.join(self.download_path, filename)
        if os.path.isfile(src):
            _, extension = os.path.splitext(filename)
            extension = extension.lower().strip('.')
            folder_paths = self.flatten_folder_paths(self.folder_paths)
            for folder, extensions in folder_paths.items():
                if extension in extensions:
                    target_path = os.path.join(self.download_path, folder, filename)
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    try:
                        self.move_file(src, target_path)
                        logging.info(f"Moved: {filename} -> {target_path}")
                        break
                    except Exception as e:
                        logging.error(f"Failed to move {filename}: {e}")

    def organize_files(self):
        files = [f for f in os.listdir(self.download_path) if os.path.isfile(os.path.join(self.download_path, f))]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(self.organize_file, files)

    def on_created(self, event):
        if not event.is_directory:
            self.organize_file(os.path.basename(event.src_path))

# GUI Components
def update_log_display(log_widget, log_path):
    try:
        with open(log_path, 'r') as file:
            log_content = file.read()
        log_widget.config(state=tk.NORMAL)
        log_widget.delete(1.0, tk.END)
        log_widget.insert(tk.END, log_content)
        log_widget.config(state=tk.DISABLED)
    except Exception as e:
        logging.error(f"Error reading log file: {e}")

def update_file_list(file_list_widget, download_path):
    try:
        files = []
        for root, dirs, filenames in os.walk(download_path):
            files.extend([os.path.join(root, file) for file in filenames])
        file_list_widget.delete(0, tk.END)
        for file in sorted(files):
            file_list_widget.insert(tk.END, file)
    except Exception as e:
        logging.error(f"Error updating file list: {e}")

def open_file(event):
    widget = event.widget
    index = widget.curselection()
    if index:
        file_path = widget.get(index[0])
        try:
            os.startfile(file_path)
        except Exception as e:
            logging.error(f"Error opening file: {e}")

def periodic_update(log_widget, file_list_widget, download_path, log_path):
    while True:
        update_log_display(log_widget, log_path)
        update_file_list(file_list_widget, download_path)
        time.sleep(10)  # update every 10 seconds

def main_gui(organizer):
    root = tk.Tk()
    root.title("File Organizer GUI")

    # Log display setup
    log_frame = ttk.Frame(root, padding="3 3 12 12")
    log_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    log_label = ttk.Label(log_frame, text="Log Output:")
    log_label.pack()
    log_display = tk.Text(log_frame, height=15, width=75, state=tk.DISABLED)
    log_display.pack()

    # File list display setup
    file_frame = ttk.Frame(root, padding="3 3 12 12")
    file_frame.grid(column=0, row=1, sticky=(tk.W, tk.E, tk.N, tk.S))
    file_label = ttk.Label(file_frame, text="All Files in Download Path and Subdirectories:")
    file_label.pack()
    file_list = tk.Listbox(file_frame, height=15, width=75)
    file_list.pack()
    file_list.bind('<Double-1>', open_file)  # Bind double click event

    # Start a thread for periodic GUI updates
    update_thread = Thread(target=periodic_update, args=(log_display, file_list, organizer.download_path, 'file_organizer.log'))
    update_thread.daemon = True
    update_thread.start()

    # Set up and start the watchdog observer
    observer = Observer()
    observer.schedule(organizer, path=organizer.download_path, recursive=True)
    observer.start()

    root.mainloop()
    observer.stop()
    observer.join()

if __name__ == "__main__":
    config_path = r'config.json'
    organizer = FileOrganizer(config_path)
    main_gui(organizer)
