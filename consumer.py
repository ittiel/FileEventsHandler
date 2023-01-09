"""
Consumer Class for running the main project logic, see readme for more details.
"""
import pathlib
import time
import hashlib
import os
import pika
import pika.exceptions
import enum
from threading import Thread
from logger import Logger
from database import DB


class Consumer(Thread):
    def __init__(self, host, queue="file-box"):
        """
        Class Constructor.
        :param host: For the IP Address to configure.
        :param queue: For the RabbitMQ queue name.
        """
        super(Consumer).__init__()
        self.host = host
        self.queue = queue
        self.connection = None
        self.channel = None
        self.SOURCE_DIR = f'/home/user/Downloads'
        self.file_types = [".ppt", ".pptx", ".pdf", ".txt", ".html", ".mp4",
                           ".jpg", ".png", ".xls", ".xlsx", ".xml", ".vsd", ".py",
                           ".doc", ".docx", ".json"]
        self.chunk_size = 1024
        self.RECONNECTING_BUFFER = 10
        self.DEFAULT_PROCESSING_TIME = 1
        self.hash = hashlib.md5()
        self.connect()
        self.class_logger = Logger('Consumer')
        self.db = DB()

    def connect(self):
        """
        Establish connection to RabbitMQ Server.
        """
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
            self.channel = self.connection.channel()
            self.channel.queue_declare(self.queue)
            print(f"[+] Consumer connected successfully to RabbitMQ queue '{self.queue}'.")
        except pika.exceptions.AMQPConnectionError as err:
            print(f"[!] Unable to connect to RabbitMQ Server.")
            self.class_logger.logger.error(f"Unable to Connect to RabbitMQ Server, Error: {err}")

    def close_connection(self):
        """
        Closes connection to rabbitMQ Server.
        """
        self.connection.close()
        print(f"[+] Consumer connection has been closed.")

    def setup_consumer_db(self):
        """
        Method For setting up the consumer database.
        """
        if self.db.setup_db('Consumer_DB'):
            self.db.create_table('Files', 'File_Name, File_Hash')
        else:
            print("[!] Error creating consumer database.")

    def on_notification_receive(self, channel, method, properties, body):
        """
        This method will do the following on the received events:
        1. if 'created':
          - generate file md5 hash,
          - if file hash already in db the consumer will change file name and add the appropriate suffix,
          - otherwise stores the hash into consumer db.
        2. if 'deleted':
          - delete file from db.
        3. if 'moved' or 'modified':
          - save to log file.
        :param channel: For RabbitMQ channel.
        :param method: For RabbitMQ delivery method.
        :param properties: For RabbitMQ properties.
        :param body: For received event message.
        """
        global file_hash, file_name
        self.channel.basic_ack(delivery_tag=method.delivery_tag)
        decoded_msg = body.decode().split()

        # Getting file path and hash
        try:
            file_name = decoded_msg[1]
            file_hash = self.hash_file(file_name)
        except FileNotFoundError as err:
            self.class_logger.logger.error(f"[!] Unable to get file path or hash, Error: {err}")

        # Validating file type
        file_type = self.validate_file_type(file_name)

        # Main method logic
        if file_type:
            # For create event
            if EventTypes.CREATED in decoded_msg:
                # Getting file size to calculate consumer processing time
                size = self.get_file_size_in_bytes(file_name)
                processing_time = self.get_file_process_time(size)
                print(f"[+] Received created event, processing time will be {processing_time} seconds.")
                # Insert hash value only if it does not exist in db
                if self.db.insert_if_not_exists('Files', 'File_Hash', file_hash):
                    self.db.update_table('Files', 'File_Name', file_name, 'File_Hash', file_hash)
                # If md5 hash already exists in db, change file name
                else:
                    try:
                        new_name = f"{file_name}{'_dup_#'}"
                        os.rename(file_name, new_name)
                        self.class_logger.logger.info(f"Changed {file_name} to {new_name}")
                    except FileNotFoundError as err:
                        self.class_logger.logger.error(f"Unable to rename {file_name}, Error: {err}")
                time.sleep(processing_time)
            # For delete event
            elif EventTypes.DELETED in decoded_msg:
                # Getting file size to calculate consumer processing time
                size = self.get_file_size_in_bytes(file_name)
                processing_time = self.get_file_process_time(size)
                print(f"[+] Received deleted event, processing time will be {processing_time} seconds.")
                try:
                    # file_hash = self.db.select_value('Files', 'File_Hash')
                    self.db.delete_value('Files', 'File_Name', file_name)
                    self.db.delete_value('Files', 'File_Name', file_hash)
                    time.sleep(processing_time)
                except TypeError as err:
                    self.class_logger.logger.error(f"Unable to delete '{file_hash}' from db, Error: {err}.")
            # For moved or modified event
            elif EventTypes.MOVED in decoded_msg or EventTypes.MODIFIED in decoded_msg:
                print(f"[+] Received modified or moved event, processing time will be {self.DEFAULT_PROCESSING_TIME} seconds.")
                self.class_logger.logger.info(f"Received '{decoded_msg}'.")

    def run(self):
        """
        Method to run the consumer with reconnecting ability.
        """
        self.setup_consumer_db()
        try:
            self.channel.basic_consume(queue=self.queue, on_message_callback=self.on_notification_receive)
            print(f"[+] Consumer is now listening to RabbitMQ queue '{self.queue}'...")
            self.channel.start_consuming()
        except (pika.exceptions.ConnectionClosedByBroker, pika.exceptions.ConnectionClosed,
                pika.exceptions.AMQPConnectionError) as err:
            print(f"[!] Connection closed due to {err}, Trying to reconnect...")
            self.class_logger.logger.error(f"Connection to RabbitMQ Server forcibly closed, Error: {err}")
            time.sleep(self.RECONNECTING_BUFFER)
            self.connect()

    def hash_file(self, file):
        """
        Generating md5 hash for a given file.
        :param file: For the file to hash.
        :return: The given file md5 hash code.
        """
        try:
            file_to_hash = open(file, 'rb')
            # For file first block
            chunk = file_to_hash.read(self.chunk_size)
            # Read until EOF
            while chunk:
                self.hash.update(chunk)
                chunk = file_to_hash.read(self.chunk_size)
        except (FileNotFoundError, FileExistsError) as err:
            self.class_logger.logger.error(f"Unable to read '{file}', Error: {err}")

        try:
            # Returns the file hash
            hash_result = self.hash.hexdigest()
            self.class_logger.logger.info(f"File '{file}' md5 hash is: '{hash_result}'.")
            return hash_result
        except FileNotFoundError as err:
            self.class_logger.logger.error(f"Unable to generate md5 hash for '{file}', Error: {err}")

    def validate_file_type(self, file):
        """
        Auxiliary method for validating file type according to supported file types list.
        :param file: For the file to validate.
        :return: True if file type is supported, False otherwise.
        """
        file_type = pathlib.Path(file).suffix
        if file_type in self.file_types:
            self.class_logger.logger.info(f"File type '{file_type}' is supported.")
            return True
        else:
            self.class_logger.logger.error(f"File type '{file_type}' is NOT supported.")
            return False

    def get_file_size_in_bytes(self, file):
        """
        Auxiliary method for getting the file size in bytes.
        :param file: For the given file to check.
        :return: The file size in bytes.
        """
        try:
            file_size = os.path.getsize(file)
            self.class_logger.logger.info(f"File '{file}' size is: {file_size}")
            return file_size
        except FileNotFoundError as err:
            self.class_logger.logger.error(f"Unable to get file '{file}' size, Error: {err}")

    @staticmethod
    def get_file_process_time(size_in_bytes):
        """
        Auxiliary method for converting size of bytes to units representation.
        :param size_in_bytes: For the size of bytes to calculate.
        :return: The processing time according to the unit size.
        """
        if size_in_bytes in SizeUnits.KB_RANGE.value:
            return SizeUnits.KB.value
        elif size_in_bytes in SizeUnits.MB_RANGE.value:
            return SizeUnits.MB.value
        elif size_in_bytes in SizeUnits.GB_RANGE.value:
            return SizeUnits.GB.value
        elif size_in_bytes in SizeUnits.TB_RANGE.value:
            return SizeUnits.TB.value


"""
Auxiliary class for handling event types.
"""


class EventTypes:
    CREATED = 'created'
    DELETED = 'deleted'
    MOVED = 'moved'
    MODIFIED = 'modified'


"""
Auxiliary class for file size units and ranges.
"""


class SizeUnits(enum.Enum):
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4
    TB = 5
    KB_RANGE = range(0, 1024)
    MB_RANGE = range(1024, 1048576)
    GB_RANGE = range(1048576, 1073741824)
    TB_RANGE = range(1073741824, 1099511627776)
