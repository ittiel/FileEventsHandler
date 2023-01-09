"""
Tester Class for creating, deleting, moving and renaming files automatically,
for testing the project logic.
"""
import os
import shutil
import time
import random
import logging


class Tester:

    def __init__(self):
        """
        Class Constructor
        """
        self.SOURCE_DIR = r"Test_Files"
        self.DESTINATION_DIR = r"/home/user/Downloads"
        self.DEFAULT_SLEEP_TIME = 2
        logging.basicConfig(filename='tester_logs.txt', filemode='w', level=logging.INFO,
                            format='[%(asctime)s] - [%(levelname)s] --- %(message)s', datefmt='%d/%m/%y %H:%M:%S')

    def create_file(self, file, content):
        """
        Method for creating new file.
        :param file: For the file name.
        :param content: For the file content.
        """
        try:
            created_file = open(self.DESTINATION_DIR + '/' + str(file), 'w')
            created_file.write(content)
            created_file.close()
            print(f"   - Creating file '{file}'.")
            time.sleep(self.DEFAULT_SLEEP_TIME)
            logging.info(f"File '{file}' has been created successfully.")
        except Exception as err:
            logging.error(f"Unable to create file '{file}', Error: {err}.")

    def delete_file(self, file):
        """
        Method for deleting a given file.
        :param file: For the file to delete.
        """
        try:
            os.remove(str(file))
            print(f"   - Deleting file '{file}'.")
            time.sleep(self.DEFAULT_SLEEP_TIME)
            logging.info(f"File '{file}' has been deleted successfully.")
        except (FileNotFoundError, FileExistsError) as err:
            logging.error(f"Unable to delete file '{file}', Error: {err}.")

    def rename_file(self, file, new_name):
        """
        Method for renaming a given file.
        :param file: For the file to rename.
        :param new_name: For the new file name.
        """
        try:
            os.rename(self.DESTINATION_DIR + '/' + file, self.DESTINATION_DIR + '/' + new_name)
            print(f"   - Renaming file '{file}' to '{new_name}'.")
            time.sleep(self.DEFAULT_SLEEP_TIME)
            logging.info(f"File '{file}' has been renamed to '{new_name}' successfully.")
        except (FileNotFoundError, FileExistsError) as err:
            logging.error(f"Unable to rename file '{file}', Error: {err}.")

    def move_file(self, file, new_path):
        """
        Method for moving a given file.
        :param file: For the file to move.
        :param new_path: For the path to move the file to.
        """
        try:
            shutil.move(file, new_path)
            print(f"   - Moving file '{file}' to '{new_path}'.")
            time.sleep(self.DEFAULT_SLEEP_TIME)
            logging.info(f"File '{file}' has been moved to '{new_path} successfully.'")
        except (shutil.Error, FileNotFoundError, FileExistsError) as err:
            logging.error(f"Unable to move file '{file}', Error: {err}.")

    def copy_file(self, file, destination):
        try:
            shutil.copy(file, destination)
            print(f"   - Copying file '{file}' to '{destination}'.")
            time.sleep(self.DEFAULT_SLEEP_TIME)
            logging.info(f"File '{file}' has been copied to '{destination}' successfully.")
        except (FileNotFoundError, FileExistsError) as err:
            logging.error(f"Unable to copy file '{file}', Error: {err}.")

    def tester_run(self):
        print("[+] Tester has started...")
        print(f"[+] Testing files creation...")
        # For checking files creation with duplicates
        file1 = "test.txt"
        file2 = "test.txt"
        file3 = "test2.txt"
        self.create_file(file1, "im a txt file")
        self.create_file(file2, "im a txt file")
        self.create_file(file3, "im a txt file2")
        self.create_file("test.pdf", "im a pdf file")
        self.create_file("test.pdf", "im a pdf file")
        self.create_file("test2.pdf", "im a pdf file2")
        self.create_file("test.ppt", "im a ppt file")
        self.create_file("test.ppt", "im a ppt file")
        self.create_file("test2.ppt", "im a ppt file2")

        # For checking file rename scenarios
        print(f"[+] Testing files renaming...")
        self.rename_file(file1, 'rename.txt')
        self.rename_file(file2, 'rename.txt')
        self.rename_file(file3, 'rename2.txt')

        # For checking deletion of files scenarios
        # files = os.listdir(self.DESTINATION_DIR)
        # print(f"[+] Testing files deletion...")
        # for file in files:
        #     path = os.path.join(self.DESTINATION_DIR, file)
        #     self.delete_file(path)

        # For checking unsupported file types
        print(f"[+] Testing files unsupported types...")
        self.create_file("unsupported.1", "im an unsupported file type.")
        self.create_file("unsupported.sadf", "im an unsupported file type1.")
        self.create_file("unsupported.info", "im an unsupported file type2.")

        # For checking download or moved or modified scenarios on supported files format
        files = os.listdir(self.SOURCE_DIR)
        print(f"[+] Testing files moving or modified...")
        for file in files:
            path = os.path.join(self.SOURCE_DIR, file)
            self.copy_file(path, self.DESTINATION_DIR)

        # Copy again a random number of files to check same file hash scenarios
        print(f"[+] Testing files duplicates...")
        for file in random.sample(files, 4):
            path = os.path.join(self.SOURCE_DIR, file)
            self.move_file(path, self.DESTINATION_DIR)


tester = Tester()
tester.tester_run()
