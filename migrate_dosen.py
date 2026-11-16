from config.database import Database

def run_migration():
    conn = Database.get_connection()
    cursor = conn.cursor()

    try:
        # Drop corrupted dosen table if exists
        cursor.execute("DROP TABLE IF EXISTS dosen")

        # Create table dosen
        cursor.execute("""
        CREATE TABLE dosen (
            id_dosen INT NOT NULL AUTO_INCREMENT,
            nip VARCHAR(30) NOT NULL,
            nama_dosen VARCHAR(100) NOT NULL,
            email VARCHAR(120) DEFAULT NULL,
            prodi VARCHAR(100) NOT NULL,
            jabatan VARCHAR(100) NOT NULL DEFAULT 'Dosen Wali / Pembimbing Akademik',
            tanda_tangan_digital VARCHAR(255) DEFAULT NULL,
            PRIMARY KEY (id_dosen),
            UNIQUE KEY (nip)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
        """)

        # Add sample dosen
        sample_dosen = [
            ('198204122008121001', 'Dr. Lukman Syafie, S.Kom., M.Kom.', 'lukman@untad.ac.id', 'Sistem Informasi', 'Koordinator Program Studi & Dosen Wali', 'DS-SIG-LUKMAN-2026'),
            ('198711052014041002', 'Fitrawan Umar, S.T., M.Kom.', 'fitrawan@untad.ac.id', 'Sistem Informasi', 'Dosen Pembimbing Akademik', 'DS-SIG-FITRAWAN-2026'),
            ('199002162019032014', 'Nismawaty, S.Kom., M.Kom.', 'nismawaty@untad.ac.id', 'Sistem Informasi', 'Dosen Wali Akademik', 'DS-SIG-NISMAWATY-2026')
        ]

        cursor.executemany("""
            INSERT INTO dosen (nip, nama_dosen, email, prodi, jabatan, tanda_tangan_digital)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, sample_dosen)

        # Alter pengajuan table to add columns if they don't exist
        cursor.execute("DESCRIBE pengajuan")
        existing_cols = [r[0] for r in cursor.fetchall()]

        cols_to_add = [
            ("id_dosen", "INT NULL AFTER id_admin"),
            ("status_dosen", "VARCHAR(30) NOT NULL DEFAULT 'Menunggu' AFTER status"),
            ("tanda_tangan_digital", "VARCHAR(255) NULL AFTER status_dosen"),
            ("tanggal_disetujui", "DATETIME NULL AFTER tanda_tangan_digital"),
            ("catatan_dosen", "TEXT NULL AFTER tanggal_disetujui"),
            ("keperluan", "TEXT NULL AFTER catatan_admin")
        ]

        for col_name, col_def in cols_to_add:
            if col_name not in existing_cols:
                print(f"Adding column {col_name}...")
                cursor.execute(f"ALTER TABLE pengajuan ADD COLUMN {col_name} {col_def}")

        # Add foreign key constraint if not exists
        cursor.execute("""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.TABLE_CONSTRAINTS 
            WHERE TABLE_SCHEMA = 'db_pengajuan_surat' 
              AND TABLE_NAME = 'pengajuan' 
              AND CONSTRAINT_NAME = 'fk_pengajuan_dosen'
        """)
        if not cursor.fetchone():
            print("Adding foreign key fk_pengajuan_dosen...")
            cursor.execute("""
                ALTER TABLE pengajuan 
                ADD CONSTRAINT fk_pengajuan_dosen 
                FOREIGN KEY (id_dosen) REFERENCES dosen(id_dosen) 
                ON DELETE SET NULL ON UPDATE CASCADE
            """)

        # Set default dosen and sample status
        cursor.execute("UPDATE pengajuan SET id_dosen = 1 WHERE id_dosen IS NULL")
        cursor.execute("""
            UPDATE pengajuan 
            SET status_dosen = 'Disetujui',
                tanda_tangan_digital = 'SIPAS-DS-20261011-8F39D21C',
                tanggal_disetujui = '2026-10-11 15:30:00',
                catatan_dosen = 'Disetujui dan ditandatangani secara digital untuk persyaratan beasiswa.'
            WHERE id_pengajuan = 1
        """)
        cursor.execute("""
            UPDATE pengajuan 
            SET status_dosen = 'Menunggu',
                catatan_dosen = 'Menunggu pemeriksaan berkas oleh dosen pembimbing.'
            WHERE id_pengajuan = 2
        """)
        cursor.execute("""
            UPDATE pengajuan 
            SET status_dosen = 'Menunggu',
                keperluan = 'Keperluan permohonan surat permohonan cuti akademik semester ganjil.'
            WHERE id_pengajuan = 4
        """)

        conn.commit()
        print("Migration executed successfully!")

        cursor.execute("DESCRIBE dosen")
        print("Dosen schema:", cursor.fetchall())

        cursor.execute("SELECT id_dosen, nip, nama_dosen, jabatan FROM dosen")
        print("Dosen data:", cursor.fetchall())

    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()

