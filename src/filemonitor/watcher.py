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

class Watcher:
    #DIRECTORY_TO_WATCH = ".."
    CHECK_INTERVAL = 1  # Check every hour (3600 seconds).
    #EMAIL_SEND_INTERVAL = 10  # Send an email every hour if no new file is added.

    def __init__(self, directory_to_watch=None, max_sec_no_file=30,
                 current_label=None, last_file_label=None):
        self.observer = Observer()
        self.last_modified_time = datetime.now()
        self.last_email_sent_time = None
        self.current_label = current_label
        self.last_file_label = last_file_label

        self.max_sec_no_file = max_sec_no_file
        self.directory_to_watch = directory_to_watch

        self.running = True
        self.email_recipient = ''
        self.email_sender = ''
        self.email_password = ''
        self.last_file_created = ''

    #@run_in_thread
    async def run(self):
        event_handler = Handler(self)
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()
        try:
            while self.running:
                await asyncio.sleep(self.CHECK_INTERVAL)
                if (datetime.now() - self.last_modified_time > timedelta(seconds=self.max_sec_no_file) and
                        (self.last_email_sent_time is None or datetime.now() - self.last_email_sent_time > timedelta(seconds=self.max_sec_no_file))):
                    email_return = self.send_email()
                    self.running = False
                    self.observer.stop()
                    return email_return
                else:
                    self.last_file_label.text = f'Last File Created: {self.last_file_created}'
        except KeyboardInterrupt:
            self.observer.stop()
            return "Monitoring interrupted"
        
        self.observer.join()

    # send_email remains the same ...
    def send_email(self):
        
        if self.email_recipient == '':
            return "Email not sent. Please provide email recipient, sender, and password."
        msg = MIMEText(f"No new files added in the last {self.max_sec_no_file} seconds. Last file was {self.last_file_created}.")
        msg['Subject'] = 'Alert: No new files detected'
        msg['From'] = self.email_sender
        msg['To'] = self.email_recipient

        try:
            # Set up the SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_sender, self.email_password)
            server.send_message(msg)
            server.quit()
            return "Email sent"
        except Exception as e:
            return f"Email not sent. An error occurred: {e}"

class Handler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher

    def on_any_event(self, event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # When a file is created, update the last_modified_time of the watcher.
            print(f"Received created event - {event.src_path}.")
            self.watcher.last_file_created = event.src_path
            self.watcher.last_modified_time = datetime.now()