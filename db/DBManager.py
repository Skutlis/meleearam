import psycopg2
from psycopg2 import IntegrityError
import logging


class dbManager:

    def __init__(self, db_config):
        self.db_config = db_config
        self.isOpen = False

        self.logger = None
        self.open()

    def open(self):
        if self.isOpen:
            return

        self.conn = psycopg2.connect(
            database=self.db_config["database"],
            user=self.db_config["user"],
            password=self.db_config["password"],
            host=self.db_config["host"],
            port=self.db_config["port"],
        )
        self.cursor = self.conn.cursor()
        self.isOpen = True

    def setUpLogger(self):

        self.loggerStamp = "DBManager"
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler("db/logs/dbManager.log")
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def is_locked(self, table_name: str):
        try:
            query = f"""
                SELECT relation::regclass, mode
                FROM pg_locks
                WHERE relation::regclass = '{table_name}'::regclass
            """
            self.cursor.execute(query)
            result = self.cursor.fetchall()

            if len(result) > 0:
                self.logger.info(f"{self.loggerStamp}: Table '{table_name}' is locked.")
                return True
            else:
                self.logger.info(
                    f"{self.loggerStamp}: Table '{table_name}' is not locked."
                )
                return False
        except Exception as e:
            self.logger.error(
                f"{self.loggerStamp}: Error checking table locks for '{table_name}': {str(e)}"
            )
            return False

    def close(self):
        if not self.isOpen:
            return
        try:
            self.conn.close()
            self.cursor.close()
            self.logger.info(f"{self.loggerStamp}: Database connection closed.")
            self.isOpen = False
        except Exception as e:
            self.logger.error(
                f"{self.loggerStamp}: Error closing database connection: {str(e)}"
            )

    def create_table(self, table_name: str, primary_keys: list, column_headers: dict):

        columns = []

        # Add column headers to the columns list, making the primary keys primary keys
        for column, data_type in column_headers.items():

            columns.append(f"{column} {data_type}")

        # Create the SQL query
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)}"
        if primary_keys:
            query = query + ", " + "PRIMARY KEY (" + ",".join(primary_keys) + ")"

        query = query + ");"

        try:
            self.cursor.execute(query)
            self.conn.commit()
            self.logger.info(
                f"{self.loggerStamp}: Table '{table_name}' created successfully."
            )
            return True

        except Exception as e:
            self.logger.error(
                f"{self.loggerStamp}: Error creating table '{table_name}': {str(e)}"
            )
            return False

    def add_row(self, table_name: str, data: dict):

        try:
            columns = ", ".join(data.keys())
            values = ", ".join(data.values())
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
            print(query)
            self.cursor.execute(query, list(data.values()))
            self.conn.commit()
            self.logger.info(f"{self.loggerStamp}: Row inserted successfully.")

            return True
        except IntegrityError as e:
            self.conn.rollback()
            self.logger.error(
                f"{self.loggerStamp}: Duplicate row. Insertion failed: {str(e)}"
            )

            return False
        except Exception as e:
            self.conn.rollback()
            self.logger.error(
                f"{self.loggerStamp}: Error inserting row into '{table_name}': {str(e)}"
            )
            return False

    def add_rows(self, table_name: str, data_list: list[dict]):

        try:
            if not data_list:
                return

            columns = ", ".join(data_list[0].keys())
            values = ", ".join([f"({', '.join(row.values())})" for row in data_list])

            query = f"INSERT INTO {table_name} ({columns}) VALUES {values};"
            values_list = [list(row.values()) for row in data_list]

            self.cursor.executemany(query, values_list)
            self.conn.commit()

            self.logger.info(f"{self.loggerStamp}: Rows inserted successfully.")

            return True
        except IntegrityError as e:
            self.conn.rollback()
            self.logger.error(
                f"{self.loggerStamp}: Duplicate row. Insertion failed: {str(e)}"
            )

            return False
        except Exception as e:
            self.conn.rollback()
            self.logger.error(
                f"{self.loggerStamp}: Error inserting rows into '{table_name}': {str(e)}"
            )

            return False

    def get_row(self, table_name, criteria):

        try:
            column_names = criteria.keys()
            conditions = [f"{column} = %s" for column in column_names]
            query = f"SELECT * FROM {table_name} WHERE {' AND '.join(conditions)};"
            self.cursor.execute(query, list(criteria.values()))
            row = self.cursor.fetchone()

            if row:
                return row
            else:
                self.logger.info(
                    f"{self.loggerStamp}: No row found in table {table_name} with the given criteria."
                )
                return ""

        except Exception as e:
            self.logger.error(
                f"{self.loggerStamp}: Error retrieving row from table {table_name}: {str(e)}"
            )

            return ""

    def changeColumnLength(self, table_name, column_name, new_length):

        try:

            # Construct the ALTER TABLE query
            alter_query = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE VARCHAR({new_length});"

            # Execute the query
            self.cursor.execute(alter_query)

            # Commit the changes
            self.conn.commit()

            print(
                f"Successfully extended VARCHAR column {column_name} in table {table_name} to length {new_length}."
            )
            return True
        except psycopg2.Error as e:
            print(f"Error: {e}")
            return False

    def get_column(self, table_name: str, column: str) -> list[str]:

        try:
            query = f"SELECT {column} FROM {table_name};"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            job_ids = [row[0] for row in rows]
            return job_ids
        except Exception as e:
            self.logger.error(
                f"{self.loggerStamp}: Error retrieving job IDs from '{table_name}': {str(e)}"
            )
            return []

    def exists(self, table_name: str, criteria: dict) -> bool:

        try:
            column_names = criteria.keys()
            values = criteria.values()
            conditions = [
                f"{column} = {val}" for column, val in zip(column_names, values)
            ]
            query = (
                f"SELECT COUNT(*) FROM {table_name} WHERE {' AND '.join(conditions)};"
            )
            self.cursor.execute(query)
            count = self.cursor.fetchone()[0]

            return count > 0
        except Exception as e:
            self.logger.error(
                f"{self.loggerStamp}: Error checking job ID existence in '{table_name}': {str(e)}"
            )

            return False

    def delete_table(self, table_name: str):

        try:
            query = f"DROP TABLE IF EXISTS {table_name};"
            self.cursor.execute(query)
            self.conn.commit()
            self.logger.info(
                f"{self.loggerStamp}: Table '{table_name}' deleted successfully."
            )
            return True
        except Exception as e:
            self.logger.error(
                f"{self.loggerStamp}: Error deleting table '{table_name}': {str(e)}"
            )
            return False

    def list_tables(self):

        try:
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
            self.cursor.execute(query)
            tables = self.cursor.fetchall()
            return [table[0] for table in tables]
        except Exception as e:
            self.logger.error(f"{self.loggerStamp}: Error listing tables: {str(e)}")
            return []

    def list_rows(self, table_name: str, order_by=None):

        try:
            # Construct the SQL query with the specified order of headers
            if order_by:
                columns = ", ".join(order_by)
                query = f"SELECT {columns} FROM {table_name}"
            else:
                query = f"SELECT * FROM {table_name}"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            self.logger.error(
                f"{self.loggerStamp}: Error listing rows from table '{table_name}': {str(e)}"
            )
            return []

    def add_column(self, table_name: str, column_name: str, column_type: str):

        try:
            query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};"
            self.cursor.execute(query)
            self.conn.commit()
            self.logger.info(
                f"{self.loggerStamp}: Column '{column_name}' added to table '{table_name}' successfully."
            )
        except Exception as e:
            self.logger.error(
                f"{self.loggerStamp}: Error adding column '{column_name}' to table '{table_name}': {str(e)}"
            )

    def get_headers(self, table_name: str):

        try:
            query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';"
            self.cursor.execute(query)
            headers = self.cursor.fetchall()
            return [header[0] for header in headers]
        except Exception as e:
            self.logger.error(
                f"{self.loggerStamp}: Error getting headers from table '{table_name}': {str(e)}"
            )
            return []

    def delete_row(self, table_name: str, criteria: dict):

        try:
            column_names = criteria.keys()
            values = criteria.values()
            conditions = [
                f"{column} = {val}" for column, val in zip(column_names, values)
            ]
            query = f"DELETE FROM {table_name} WHERE {' AND '.join(conditions)};"
            self.cursor.execute(query)
            self.conn.commit()
            self.logger.info(f"{self.loggerStamp}: Row(s) deleted successfully.")

            return True
        except Exception as e:
            self.logger.error(
                f"{self.loggerStamp}: Error deleting row(s) from table '{table_name}': {str(e)}"
            )

            return False

    def update_column(
        self, table_name: str, criteria: dict, column_name: str, new_value
    ):

        try:
            where = []
            for key in criteria.keys():
                s = f"{key} = '{criteria[key]}'"
                where.append(s)

            query = (
                f"UPDATE {table_name} SET {column_name} = '{new_value}' WHERE "
                + " AND ".join(where)
                + ";"
            )

            self.cursor.execute(query)
            self.conn.commit()
            self.logger.info(
                f"{self.loggerStamp}: Column '{column_name}' updated successfully."
            )
            return True

        except Exception as e:
            self.conn.rollback()
            self.logger.error(
                f"{self.loggerStamp}: Error updating column '{column_name}' in table '{table_name}': {str(e)}"
            )
            return False

    def update_row(self, table_name, criteria, new_values):

        try:
            column_names = criteria.keys()
            values = criteria.values()
            conditions = [
                f"{column} = {val}" for column, val in zip(column_names, values)
            ]
            query = f"UPDATE {table_name} SET {', '.join([f'{column} = {val}' for column, val in new_values.items()])} WHERE {' AND '.join(conditions)};"
            self.cursor.execute(query)
            self.conn.commit()
            self.logger.info(f"{self.loggerStamp}: Row updated successfully.")

        except Exception as e:
            self.conn.rollback()
            self.logger.error(
                f"{self.loggerStamp}: Error updating row in table '{table_name}': {str(e)}"
            )

    def __del__(self):
        self.close()
        self.logger.info(f"{self.loggerStamp}: DBManager object deleted.")
