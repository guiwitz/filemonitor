"""
Monitoring addition of files in folder
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
#from .watcher import Watcher

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import threading
import asyncio

def run_in_thread(method):
    """
    Decorator to run a class method in a new thread.

    :param method: Class method to be executed in a new thread.
    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=method, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper

class Filemonitor(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.folder = None
        main_box = toga.Box()

        self.max_sec_no_file = toga.NumberInput(min_value=1, max_value=60, step=1, value=5)
        self.select_folder_btn = toga.Button('Select Folder', on_press=self.select_folder)
        self.start_monitor_btn = toga.Button('Start Monitoring', on_press=self.start_monitoring)
        self.stop_monitor_btn = toga.Button('Stop Monitoring', on_press=self.stop_monitoring)

        self.display_folder_label = toga.Label('Folder: ')
        self.display_current_state_label = toga.Label('Current State: ')


        main_box.add(self.max_sec_no_file)
        main_box.add(self.select_folder_btn)
        main_box.add(self.start_monitor_btn)
        main_box.add(self.stop_monitor_btn)
        main_box.add(self.display_folder_label)
        main_box.add(self.display_current_state_label)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

        ## observer
        self.last_email_sent_time = None
        self.directory_to_watch = None

        self.max_sec_no_file = 10

        self.running = True
        self.CHECK_INTERVAL = 1
        self.status = 'idle'
        self.task = None

    async def start_monitoring(self, widget):
        
        if self.directory_to_watch is None:
            self.main_window.info_dialog('Select Folder', 'Please select a folder to monitor')
            return
        
        self.display_folder_label.text = f'Folder: {self.directory_to_watch}'
        self.status = 'Monitoring'
        self.display_current_state_label.text = self.status
        '''if self.task:# and not self.task.done():
            try:
                # Wait for the cancellation to complete
                await self.task
            except asyncio.CancelledError:
                print("Current task cancelled.")'''
        print("new task")
        self.running = True
        self.observer = Observer()
        self.last_modified_time = datetime.now()
        self.task = asyncio.create_task(self.run())
        #result = await self.task
        self._on_completion()

    def _on_completion(self):
        
        self.observer.stop()
        self.display_current_state_label.text = self.status

    def stop_monitoring(self, widget):
        self.running = False
        self.observer.unschedule_all()

    async def select_folder(self, widget):
        self.directory_to_watch = await self.main_window.select_folder_dialog('Select Folder')
        #print(self.folder)
    
    #@run_in_thread
    async def run(self):
        event_handler = Handler(self)
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()
        try:
            while self.running:
                time.sleep(self.CHECK_INTERVAL)
                if (datetime.now() - self.last_modified_time) > timedelta(seconds=self.max_sec_no_file):
                    self.send_email()
                    self.running = False
                    self.observer.unschedule_all()
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    # send_email remains the same ...
    def send_email(self):
        '''msg = MIMEText("No new files added in the last hour.")
        msg['Subject'] = 'Alert: No new files detected'
        msg['From'] = 'your_email@example.com'
        msg['To'] = 'receiver_email@example.com'

        # Set up the SMTP server
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login('your_email@example.com', 'your_password')
        server.send_message(msg)
        server.quit()'''

        print("Email sent")
        self.status = "Email sent"

class Handler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher

    def on_any_event(self, event):
        print("event")
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # When a file is created, update the last_modified_time of the watcher.
            print(f"Received created event - {event.src_path}.")
            self.watcher.last_modified_time = datetime.now()


def main():
    return Filemonitor()

