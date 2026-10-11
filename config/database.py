import mysql.connector
from mysql.connector import Error


class Database:
    @staticmethod
    def get_connection():
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="db_pengajuan_surat",
            )

            if connection.is_connected():
                return connection

        except Error as error:
            raise RuntimeError(
                f"Gagal terhubung ke database: {error}"
            ) from error