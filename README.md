# FileEventsHandler
- File events handler is a big data project for publish file events on a given directory to a consumer using RabbitMQ.
- This project is based on a MessageBus architecture.

### Usage
Written in PyCharm on Ubuntu 20.04

### Project Logic
The Handler will Identify files duplicates in a given library (implemented as a directory on this project),
based on md5 file hash code, implementing the following logic:
1. A Watcher component will observe the library for file events (Create, Move, Modified and Delete).
2. A Producer component will publish the event with the file path to a RabbitMQ queue.
3. A Consumer component will 'listen' to the same RabbitMQ queue, when an event will pop up the consumer will do the following:
  * **in 'created' event** -
    * generate md5 hash for the file.
    * check if the hash already exists in the consumer DB.
    * if exists, the consumer will add to the original file name '_dup_#' suffix.
    * otherwise will insert the md5 hash and file to the consumer DB.
  * **in 'deleted' event** - the consumer will delete the file and it's md5 hash from DB.
  * **in 'moved' or 'modified' events** - the consumer will write to it's log file.
4. RabbitMQ will continue to process event from queue.


### Project architecture

