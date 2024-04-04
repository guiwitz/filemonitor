"""
Monitoring addition of files in folder
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from .watcher import Watcher
import asyncio


class Filemonitor(toga.App):
    def startup(self):
        
        self.folder = None
        main_box = toga.Box(style=Pack(direction=COLUMN))
        options_box = toga.Box(style=Pack(direction=ROW))
        start_stop_box = toga.Box(style=Pack(direction=ROW))
        status_box = toga.Box(style=Pack(direction=ROW))
        self.email_box = toga.Box(style=Pack(direction=ROW))


        self.time_label = toga.Label('Max Time Interval (in seconds): ')
        self.max_sec_no_file = toga.NumberInput(min_value=1, max_value=60, step=1, value=5)
        self.select_folder_btn = toga.Button('Select Folder', on_press=self.select_folder)
        self.start_monitor_btn = toga.Button('Start Monitoring', on_press=self.start_monitoring)
        self.stop_monitor_btn = toga.Button('Stop Monitoring', on_press=self.stop_monitoring)

        self.display_folder_label = toga.Label('Folder: ')
        self.display_current_state_label = toga.Label('Current State: ')

        self.email_recipient_label = toga.Label('Email Destination: ')
        self.email_recipient = toga.TextInput()
        self.email_sender_label = toga.Label('Sender Email: ')
        self.email_sender = toga.TextInput()
        self.password_label = toga.Label('Sender Password: ')
        self.password = toga.PasswordInput()

        options_box.add(self.time_label)
        options_box.add(self.max_sec_no_file)
        options_box.add(self.select_folder_btn)
        start_stop_box.add(self.start_monitor_btn)
        start_stop_box.add(self.stop_monitor_btn)
        status_box.add(self.display_folder_label)
        status_box.add(self.display_current_state_label)

        self.email_box.add(self.email_recipient_label)
        self.email_box.add(self.email_recipient)
        self.email_box.add(self.email_sender_label)
        self.email_box.add(self.email_sender)
        self.email_box.add(self.password_label)
        self.email_box.add(self.password)

        main_box.add(options_box)
        main_box.add(start_stop_box)
        main_box.add(status_box)
        main_box.add(self.email_box)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    async def start_monitoring(self, widget):
        
        if self.folder is None:
            self.main_window.info_dialog('Select Folder', 'Please select a folder to monitor')
            return
        

        self.watcher = Watcher(
            max_sec_no_file=float(self.max_sec_no_file.value),
            directory_to_watch=self.folder, current_label=self.display_current_state_label)
        self.display_folder_label.text = f'Folder: {self.folder}'
        self.watcher.running = True
        self.watcher.email_recipient =self.email_recipient.value
        self.watcher.email_recipient = self.watcher.email_recipient.replace(u'\xa0', u' ')
        self.watcher.email_sender = self.email_sender.value
        self.watcher.email_sender = self.watcher.email_sender.replace(u'\xa0', u' ')
        self.watcher.email_password = self.password.value
        self.watcher.email_password = self.watcher.email_password.replace(u'\xa0', u' ')
        output = await self.watcher.run()
        self.display_current_state_label.text = output

    def stop_monitoring(self, widget):
        self.watcher.running = False
        self.watcher.observer.stop()

    async def select_folder(self, widget):
        self.folder = await self.main_window.select_folder_dialog('Select Folder')    


def main():
    return Filemonitor()

