"""
File Change Handler Class for watch the wanted folder for file changes.
"""
import pika
import time
import pika.exceptions
from typing import Union
from producer import Producer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


class FileChangeWatcher(FileSystemEventHandler):

    def __init__(self, host):
        """
        Class Constructor.
        """
        self.producer = Producer(host)
        self.file_paths = []

    def on_any_event(self, event: Union[FileCreatedEvent]):
        """
        Method to send to RabbitMQ queue the file change event.
        :param event: For the event to send.
        """
        # Avoid directory changes
        if event.is_directory:
            return None

        # Add the file creation path to path lists
        if isinstance(event, FileCreatedEvent):
            self.file_paths.append(event.src_path)

        # Send event type and file path to RabbitMQ queue for further processing
        try:
            msg = f"{event.event_type} {event.src_path}"
            self.producer.channel.basic_publish(exchange='', routing_key=self.producer.queue, body=msg)
        except (pika.exceptions.ConnectionClosed, pika.exceptions.StreamLostError, AttributeError) as err:
            print(f"[!] Unable to send event to RabbitMQ, Error: {err}, Trying to reconnect...")
            # In case connection will be terminated
            time.sleep(self.producer.RECONNECTING_BUFFER)
            self.producer.connect()
