import sqlite3

class DataCopier:
    def __init__(self, dest_conn):
        self.dest_conn = dest_conn

    def get_table_names(self, src_conn):
        cursor = src_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [table[0] for table in cursor.fetchall()]
        return table_names

    def get_table_data(self, src_conn, table_name):
        cursor = src_conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall()

    def copy_data_to_dest_db(self, src_conn):
        dest_cursor = self.dest_conn.cursor()

        table_names = self.get_table_names(src_conn)

        for table_name in table_names:
            src_data = self.get_table_data(src_conn, table_name)

            for row in src_data:
                placeholders = ", ".join(["?"] * len(row))
                dest_cursor.execute(f"INSERT OR IGNORE INTO {table_name} VALUES ({placeholders})", row)

        self.dest_conn.commit()

    def perform_copy(self, src_db_list):
        for src_db in src_db_list:
            src_conn = sqlite3.connect(src_db)
            self.copy_data_to_dest_db(src_conn)
            src_conn.close()