"""
Producer Class for publish file changes events to RabbitMQ queue.
"""
import pika
import pika.exceptions


class Producer:

    def __init__(self, host, queue='file-box'):
        """
        Class Constructor.
        :param host: For the hot ip address.
        :param queue: FOr the RabbitMQ queue name.
        """
        self.host = host
        self.queue = queue
        self.connection = None
        self.channel = None
        self.RECONNECTING_BUFFER = 10
        self.connect()

    def connect(self):
        """
        Establish connection to RabbitMQ Server.
        """
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)
        print(f"[+] Producer connected successfully to RabbitMQ queue '{self.queue}'.")

    def close_connection(self):
        """
        Closes the RabbitMQ connection.
        """
        self.connection.close()
