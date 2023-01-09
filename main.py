"""
Project main method to run the FileHandler.
"""
from threading import Thread
from handler import FileHandler


def main():

    fh = FileHandler('localhost')
    try:
        file_handler_thread = Thread(target=fh.run)
        file_handler_thread.start()
    except KeyboardInterrupt:
        print("[!] Connection has been closed forcibly by user.")
        fh.stop_observer()


if __name__ == "__main__":
    main()
