"""
DB class for creating and customize the Consumer needed SQLite tables.
DB is written with SQL parameterized queries to prevent SQL Injection.
"""
import sqlite3
from logger import Logger


class DB:

    def __init__(self):
        """
        Class Constructor.
        Initializes the connection and cursor elements to None.
        """
        self.conn = None
        self.cursor = None
        self.class_logger = Logger('DB')

    def setup_db(self, name):
        """
        Setup a new database, initializing the connection and cursor elements accordingly.
        :param name: For the name of the database to setup.
        """
        try:
            self.conn = sqlite3.connect(name)
            self.cursor = self.conn.cursor()
            self.class_logger.logger.info(f"Connected to Database '{name}' successfully.")
            return True
        except sqlite3.Error as err:
            self.class_logger.logger.error(f"Error connecting to database, Error {err}.")
            return False

    def close_db(self):
        """
        Closes database elements and save the data.
        """
        try:
            self.conn.commit()
            self.class_logger.logger.info(f"Saved all database data successfully.")
            self.cursor.close()
            self.class_logger.logger.info(f"Closed '{self.cursor}' successfully.")
            self.conn.close()
            self.class_logger.logger.info(f"Closed '{self.conn}' successfully.")
        except sqlite3.Error as err:
            print("[!] Unable to close database.")
            self.class_logger.logger.error(f"Error closing database, Error: {err}")

    def create_table(self, table_name, columns):
        """
        Creates a table according to a given table name.
        :param table_name: For the table name.
        :param columns: For the table columns.
        """
        try:
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
            self.conn.commit()
            self.class_logger.logger.info(f"Created Table '{table_name}' successfully.")
        except sqlite3.Error as err:
            print(f"[!] Unable to create table '{table_name}'.")
            self.class_logger.logger.error(f"Error creating table {err}.")

    def insert_value(self, table_name, table_column, value):
        """
        Inserting a new value to a given database table.
        :param table_name: For the table to insert values to.
        :param table_column: For the column to insert values to.
        :param value: For the value to insert.
        """
        try:
            self.cursor.execute(f"INSERT INTO {table_name} ({table_column}) VALUES(?)", (value,))
            self.conn.commit()
            self.class_logger.logger.info(f"Inserted '{value}' to '{table_name}' successfully.")
        except sqlite3.Error as err:
            print(f"[!] Unable to insert '{value}' to '{table_name}'.")
            self.class_logger.logger.error(f"Error inserting '{value}' to table {err}.")

    def insert_if_not_exists(self, table_name, table_column, value):
        """
        Inserting a new value to a given database table only if it doesn't already exists.
        :param table_name: For the table to insert values to.
        :param table_column: For the column to insert values to.
        :param value: For the value to insert.
        :return: True if the value has been inserted successfully, False otherwise.
        """
        try:
            self.cursor.execute(f"SELECT * FROM {table_name} WHERE {table_column}=?", (value,))
            result = self.cursor.fetchone()
            if result is None:
                # Value does not exist and has been inserted successfully
                self.insert_value(table_name, table_column, value)
                return True
            else:
                self.class_logger.logger.info(f"'{value}' Exists in '{table_name}'")
                return False
        except sqlite3.Error as err:
            print(f"[!] Unable to insert '{value}' to '{table_name}'.")
            self.class_logger.logger.error(f"Error inserting '{value}' from '{table_name}' {err}.")

    def update_table(self, table_name, column_to_update, value, current_table_column, existing_value):
        """
        Updates an existing table with a given value.
        :param table_name: For the existing table to update.
        :param column_to_update: For the table column to update.
        :param value: For the new value to add.
        :param current_table_column: For the existing table column.
        :param existing_value: For the existing table value.
        """
        try:
            self.cursor.execute(f"UPDATE {table_name} SET {column_to_update} = ? WHERE {current_table_column} = ?", (value, existing_value))
            self.conn.commit()
            self.class_logger.logger.info(f"Inserted '{value}' to '{column_to_update}' in '{table_name}' successfully.")
        except (TypeError, sqlite3.Error) as err:
            print(f"[!] Unable to update '{value}' in '{table_name}'")
            self.class_logger.logger.error(f"Error updating table {err}.")

    def delete_value(self, table_name, table_column, value_to_delete):
        """
        Deleting a given value from a given table.
        :param table_name: For the table to delete the value from.
        :param table_column: For the table column to delete from.
        :param value_to_delete: For the value to delete.
        """
        try:
            self.cursor.execute(f"DELETE FROM {table_name} WHERE {table_column} = ?", (value_to_delete,))
            self.conn.commit()
            self.class_logger.logger.info(f"Deleted '{value_to_delete}' from '{table_name}' successfully.")
        except sqlite3.Error as err:
            print(f"[!] Unable to delete '{value_to_delete}' from '{table_name}'.")
            self.class_logger.logger.error(f"Error deleting values from '{table_name}' {err}.")

    def select_value(self, table_name, table_column):
        """
        Selects a specific table value and return it.
        :param table_name: For the table to select from.
        :param table_column: For the table column to select from.
        :return: The table value after unpacking.
        """
        try:
            self.cursor.execute(f"SELECT {table_column} FROM {table_name}")
            value = self.cursor.fetchone()[0]
            return value
        except sqlite3.Error as err:
            print(f"[!] Unable to retrieve value from '{table_name}'")
            self.class_logger.logger.error(f"Error retrieving value from '{table_name}' {err}.")

    def print_all_database(self, table_name):
        """
        Prints out to console the entire table in a customized format.
        :param table_name: For the wanted table to print out.
        """
        counter = 0
        self.cursor.execute(f"SELECT * FROM {table_name} ")
        columns = [description[0] for description in self.cursor.description]
        rows = self.cursor.fetchall()
        print(f"{'=' * 12} {table_name.upper()} TABLE: {'=' * 12}")
        for row in rows:
            counter += 1
            print(f"File #{counter}: ")
            for col, val in zip(columns, row):
                print(f"- {col}: {val}")
            print("=" * 40)
