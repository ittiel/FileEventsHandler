"""
FileHandler Class for handling the entire project in a MessageBus Architecture.
"""
import time
from threading import Thread
from consumer import Consumer
from watchdog.observers import Observer
from watcher import FileChangeWatcher
from logger import Logger


class FileHandler(Thread):

    def __init__(self, host):
        """
        Class Constructor.
        """
        super().__init__()
        self.host = host
        self.threads = []
        self.class_logger = Logger('FileHandler')
        self.observer = Observer()
        self.SOURCE_DIR = f'/home/user/Downloads'
        self.consumer = Consumer(self.host)

    def start_observer(self):
        """
        Starts watcher.
        """
        self.observer.start()
        print(f"[+] Started File Handler, observing the directory '{self.SOURCE_DIR}'.")
        self.class_logger.logger.info(f"File Handler has been started successfully.")

    def stop_observer(self):
        """
        Stopes watcher.
        """
        self.observer.stop()
        self.consumer.close_connection()
        print("[+] Stopped File Handler.")

    def run(self):
        """
        FileHandler run method to enable project logic using threads.
        """
        event_handler = FileChangeWatcher(self.host)
        self.observer.schedule(event_handler, self.SOURCE_DIR, recursive=True)
        self.threads.append(self.observer)
        self.start_observer()
        consumer_thread = Thread(target=self.consumer.run)
        self.threads.append(consumer_thread)
        consumer_thread.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt as err:
            self.stop_observer()
            print(f"[!] FileHandler stopped running, please see log file for more details.")
            self.class_logger.logger.error(f"FileHandler has stopped running, Error: {err}.")
        for thread in self.threads:
            thread.join()


