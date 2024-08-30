import sqlite3

class dbMan():
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()

    def create_table(self, table_name, columns):
        self.cur.execute('CREATE TABLE IF NOT EXISTS {0} ({1})'.format(table_name, columns))

    def insert_data(self, table_name, columns, values):
        self.cur.execute('INSERT INTO {0} ({1}) VALUES ({2})'.format(table_name, columns, values))
        self.conn.commit()

    def select_data(self, table_name, columns, condition):
        self.cur.execute('SELECT {0} FROM {1} WHERE {2}'.format(columns, table_name, condition))
        return self.cur.fetchall()

    def update_data(self, table_name, columns, values, condition):
        self.cur.execute('UPDATE {0} SET {1} WHERE {2}'.format(table_name, columns, values, condition))
        self.conn.commit()

    def delete_data(self, table_name, condition):
        self.cur.execute('DELETE FROM {0} WHERE {1}'.format(table_name, condition))
        self.conn.commit()

    def close(self):
        self.conn.close()