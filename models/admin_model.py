from config.database import Database


class AdminModel:
    def autentikasi(self, username, password):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT id_admin, nama_admin, username
                FROM admin
                WHERE username = %s AND password = %s
            """
            cursor.execute(query, (username, password))
            return cursor.fetchone()
        finally:
            conn.close()

    def semua(self):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_admin, nama_admin, username
                FROM admin
                ORDER BY id_admin
            """)
            return cursor.fetchall()
        finally:
            conn.close()

    def tambah(self, nama_admin, username, password):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO admin (nama_admin, username, password)
                VALUES (%s, %s, %s)
                """,
                (nama_admin, username, password),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()