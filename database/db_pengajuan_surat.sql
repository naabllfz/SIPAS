-- MySQL dump 10.13  Distrib 26.7.0, for macos26.6 (arm64)
--
-- Host: localhost    Database: db_pengajuan_surat
-- ------------------------------------------------------
-- Server version	26.7.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `id_admin` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `nama_admin` varchar(100) NOT NULL,
  PRIMARY KEY (`id_admin`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'Admin SI','SI12345','Staf Admin Sistem Informasi');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detail_surat`
--

DROP TABLE IF EXISTS `detail_surat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detail_surat` (
  `id_detail_surat` bigint NOT NULL AUTO_INCREMENT,
  `id_jenis_surat` bigint NOT NULL,
  `nama_surat` varchar(80) NOT NULL,
  `deskripsi` varchar(250) NOT NULL,
  PRIMARY KEY (`id_detail_surat`),
  UNIQUE KEY `uq_detail_jenis_nama` (`id_jenis_surat`,`nama_surat`),
  UNIQUE KEY `uq_detail_nama_surat` (`nama_surat`),
  KEY `id_jenis_surat` (`id_jenis_surat`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detail_surat`
--

LOCK TABLES `detail_surat` WRITE;
/*!40000 ALTER TABLE `detail_surat` DISABLE KEYS */;
INSERT INTO `detail_surat` VALUES (1,1,'Surat Permohonan Cuti Akademik','Permohonan pemberhentian studi sementara selama semester berjalan karena alasan kesehatan'),(2,1,'Surat Permohonan Aktif Kuliah Kembali','Permohonan pengaktifan ulang status kemahasiswaan di sistem akademik setelah masa cuti berakhir'),(3,2,'Surat Permohonan Izin Penelitian','Permintaan surat pengantar resmi ke instansi atau lokasi tujuan untuk pengambilan data tugas akhir'),(4,2,'Surat Permohonan Izin Magang / Praktik Kerja Lapangan (PKL)','Permintaan surat pengantar resmi untuk melaksanakan praktik kerja lapangan di perusahaan atau instansi'),(5,3,'Surat Permohonan Seminar Proposal (Sempro)','Pendaftaran jadwal ujian proposal penelitian setelah mendapat persetujuan dari dosen pembimbing'),(6,3,'Surat Permohonan Ujian Hasil / Sidang Akhir','Pendaftaran sidang kelulusan akhir setelah seluruh revisi dan syarat akademik terpenuhi'),(7,4,'Surat Permohonan Keterangan Aktif Kuliah','Permintaan surat bukti status mahasiswa aktif untuk keperluan beasiswa, tunjangan orang tua, atau administrasi umum'),(8,4,'Surat Permohonan Keringanan / Penundaan UKT','Permohonan penurunan golongan biaya kuliah atau perpanjangan batas waktu pembayaran SPP/UKT'),(9,2,'Pengajuan-4-202611160204372415','Observasi di kabupaten parigi'),(10,1,'Pengajuan-6-202611160316017585','Surat Cuti');
/*!40000 ALTER TABLE `detail_surat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dokumen_surat`
--

DROP TABLE IF EXISTS `dokumen_surat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dokumen_surat` (
  `id_dokumen` bigint NOT NULL AUTO_INCREMENT,
  `id_pengajuan` bigint NOT NULL,
  `nama_file` varchar(255) NOT NULL,
  `path_file` varchar(500) NOT NULL,
  `hash_sha256` char(64) NOT NULL,
  `ditandatangani_oleh` bigint DEFAULT NULL,
  `waktu_tanda_tangan` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_dokumen`),
  UNIQUE KEY `id_pengajuan` (`id_pengajuan`),
  KEY `fk_dokumen_dosen` (`ditandatangani_oleh`),
  CONSTRAINT `fk_dokumen_dosen` FOREIGN KEY (`ditandatangani_oleh`) REFERENCES `dosen` (`id_dosen`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_dokumen_pengajuan` FOREIGN KEY (`id_pengajuan`) REFERENCES `pengajuan` (`id_pengajuan`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dokumen_surat`
--

LOCK TABLES `dokumen_surat` WRITE;
/*!40000 ALTER TABLE `dokumen_surat` DISABLE KEYS */;
INSERT INTO `dokumen_surat` VALUES (1,5,'surat_cuti_akademik_001.pdf','/dokumen/surat_cuti_akademik_001.pdf','afdec8bd2e56fcbc2e8189120866052041ca6b428d608dacf93aeb299beb01d2',1,'2026-11-15 00:31:14','2026-11-15 00:31:14'),(2,8,'surat_ket_aktif_kuliah_004.pdf','/dokumen/surat_ket_aktif_kuliah_004.pdf','6b03b87d71ea156b67015e97aba42a0c7755d3a744deddc9944546b0ac74133f',1,'2026-11-15 00:31:14','2026-11-15 00:31:14'),(4,6,'surat_pengajuan_006.pdf','storage/surat/surat_pengajuan_006.pdf','33863bc4fee2e8b00d478e2cd6ce19fd3a3860cbbac0f4c9db2b3f64547d6cb2',1,'2026-11-16 01:39:26','2026-11-16 01:39:26'),(5,12,'lampiran_pengajuan_012_20261116020437.jpg','storage/lampiran/lampiran_pengajuan_012_20261116020437.jpg','0cfef8ec5889eeddcca85892cee63381418affd9c78c6eaff8abf49f17e21c14',4,'2026-11-16 02:06:56','2026-11-16 02:04:37'),(8,9,'surat_pengajuan_009.pdf','storage/surat/surat_pengajuan_009.pdf','779d5337ab1335fba96c46de8ddbaf4e6a4734295df8ef499a061ec530832fe9',4,'2026-11-16 02:07:30','2026-11-16 02:07:30'),(9,13,'lampiran_pengajuan_013_20261116031601.jpg','storage/lampiran/lampiran_pengajuan_013_20261116031601.jpg','45b7bae2d5b74673a6be52545f0d7b7e540d9fa67fc7dc94911f13dac352e757',1,'2026-11-16 03:18:22','2026-11-16 03:16:01');
/*!40000 ALTER TABLE `dokumen_surat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dosen`
--

DROP TABLE IF EXISTS `dosen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dosen` (
  `id_dosen` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `nama_dosen` varchar(100) NOT NULL,
  `nidn` varchar(30) DEFAULT NULL,
  `jabatan` enum('Dosen Wali','Dosen Pembimbing','Ketua Program Studi','Ketua Jurusan') NOT NULL DEFAULT 'Dosen Wali',
  `email` varchar(120) DEFAULT NULL,
  `file_ttd` varchar(255) DEFAULT NULL,
  `status` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_dosen`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `nidn` (`nidn`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dosen`
--

LOCK TABLES `dosen` WRITE;
/*!40000 ALTER TABLE `dosen` DISABLE KEYS */;
INSERT INTO `dosen` VALUES (1,'yuda123','616c01cf3450e77b4d5d2aed9464c31da007242cbe07ece09e68a21e15e659ab','Yuda Pramesta','F5212520066','Ketua Jurusan','yuda@mail.com','storage/ttd_dosen/ttd_dosen_1.png',1,'2026-11-14 23:56:26'),(2,'trian123','82db989fff0c499a4559c74e3b624790e6ade6d9698fba517393d27e3def12f5','Moh Trian Firmansyah','F5212520079','Ketua Program Studi','trian@mail.com',NULL,1,'2026-11-14 23:56:26'),(3,'widyo123','c8469f7751229784725fca846d3f8525cfa5010a3cb5ef0c3cf5a79764fc589c','Widyo Prabowo','F5212520068','Dosen Pembimbing','widyo@mail.com',NULL,1,'2026-11-14 23:56:26'),(4,'sinan123','078a6e25b89a739daf91a4370ad474cb3f5c37214c44e57ef1edf5947ad513e4','Sinan Az-zuffar','F5212520043','Dosen Wali','sinan@mail.com','storage/ttd_dosen/ttd_dosen_4.jpg',1,'2026-11-14 23:56:26');
/*!40000 ALTER TABLE `dosen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jenis_surat`
--

DROP TABLE IF EXISTS `jenis_surat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jenis_surat` (
  `id_jenis_surat` bigint NOT NULL AUTO_INCREMENT,
  `jenis_surat` varchar(80) NOT NULL,
  `aktif` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_jenis_surat`),
  UNIQUE KEY `nama_jenis` (`jenis_surat`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jenis_surat`
--

LOCK TABLES `jenis_surat` WRITE;
/*!40000 ALTER TABLE `jenis_surat` DISABLE KEYS */;
INSERT INTO `jenis_surat` VALUES (1,'Keperluan Status Akademik & Perkuliahan',1),(2,'Keperluan Penelitian & Kegiatan Lapangan',1),(3,'Keperluan Tugas Akhir',1),(4,'Keperluan Administrasi & Keuangan',1);
/*!40000 ALTER TABLE `jenis_surat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mahasiswa`
--

DROP TABLE IF EXISTS `mahasiswa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mahasiswa` (
  `id_mahasiswa` bigint NOT NULL AUTO_INCREMENT,
  `nim` varchar(20) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `nama` varchar(100) NOT NULL,
  `prodi` varchar(100) NOT NULL,
  `email` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`id_mahasiswa`),
  UNIQUE KEY `nim` (`nim`),
  UNIQUE KEY `uq_mahasiswa_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mahasiswa`
--

LOCK TABLES `mahasiswa` WRITE;
/*!40000 ALTER TABLE `mahasiswa` DISABLE KEYS */;
INSERT INTO `mahasiswa` VALUES (1,'F5212520048','rusfaldi123','d5da3ecb54955110f1dc8a066040b4ef0ddcb3609a47f37ecacc64f721d9f56d','Rusfaldi Andika','Sistem Informasi','rusfaldi@gmail.com'),(2,'F5212520055','rizky123','12bb09e2ce02ba6652444dbacbb86499dddf0c0612f646a7f280e459f57bedfa','Muhammad Rizky Al Ghifari','Sistem Informasi',NULL),(3,'F5212520058','raihan123','f53ce77a8d4ff9f89b4fe2305670f79476c362b706a4037d5c167a3b9a132e79','Raihan Irbah Zaki','Sistem Informasi',NULL),(4,'F5212520061','nabil123','a5c5d85c5d26b70ccc4efe03d889a6f1ffb953d09117c4acd91a7e6e3d37477a','Nabil Afzaal','Sistem Informasi','nabil@gmail.com'),(5,'F5212520069','mulya123','7f5da3ae6b8bc8b3729497d3b0edb6946c9522816211c3d5bd46ee9b2d52ea72','Mulya Syaputra Jufran','Sistem Informasi',NULL),(6,'F5212520073','akbar123','f7a723f542931f05606424a5348ff56118f95ed6ea0312955c5947f9137ec8e3','Muh Akbar Khadapi Dape','Sistem Informasi',NULL);
/*!40000 ALTER TABLE `mahasiswa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pengajuan`
--

DROP TABLE IF EXISTS `pengajuan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pengajuan` (
  `id_pengajuan` bigint NOT NULL AUTO_INCREMENT,
  `id_mahasiswa` bigint NOT NULL,
  `id_jenis_surat` bigint NOT NULL,
  `id_detail_surat` bigint DEFAULT NULL,
  `id_admin` bigint DEFAULT NULL,
  `id_dosen` bigint DEFAULT NULL,
  `tanggal_pengajuan` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(30) NOT NULL DEFAULT 'Diajukan',
  `catatan_admin` text,
  `catatan_dosen` text,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `tanggal_verifikasi_admin` datetime DEFAULT NULL,
  `tanggal_keputusan_dosen` datetime DEFAULT NULL,
  PRIMARY KEY (`id_pengajuan`),
  KEY `fk_pengajuan_mahasiswa` (`id_mahasiswa`),
  KEY `fk_pengajuan_jenis_surat` (`id_jenis_surat`),
  KEY `fk_pengajuan_admin` (`id_admin`),
  KEY `idx_pengajuan_dosen` (`id_dosen`),
  KEY `fk_pengajuan_detail` (`id_detail_surat`),
  CONSTRAINT `fk_pengajuan_admin` FOREIGN KEY (`id_admin`) REFERENCES `admin` (`id_admin`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_pengajuan_detail` FOREIGN KEY (`id_detail_surat`) REFERENCES `detail_surat` (`id_detail_surat`),
  CONSTRAINT `fk_pengajuan_dosen` FOREIGN KEY (`id_dosen`) REFERENCES `dosen` (`id_dosen`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_pengajuan_jenis_surat` FOREIGN KEY (`id_jenis_surat`) REFERENCES `jenis_surat` (`id_jenis_surat`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_pengajuan_mahasiswa` FOREIGN KEY (`id_mahasiswa`) REFERENCES `mahasiswa` (`id_mahasiswa`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pengajuan`
--

LOCK TABLES `pengajuan` WRITE;
/*!40000 ALTER TABLE `pengajuan` DISABLE KEYS */;
INSERT INTO `pengajuan` VALUES (5,1,1,1,1,1,'2026-11-15 00:30:34','Disetujui',NULL,NULL,'2026-11-15 00:30:58','2026-11-15 00:30:58','2026-11-15 00:30:58'),(6,2,2,3,NULL,1,'2026-11-15 00:30:34','Disetujui',NULL,'Disetujui dan ditandatangani oleh dosen pembimbing/wali.','2026-11-16 01:39:26',NULL,'2026-11-16 01:39:26'),(7,3,3,5,1,2,'2026-11-15 00:30:34','Ditolak',NULL,'Proposal belum layak diseminarkan, revisi dari pembimbing belum selesai.','2026-11-15 00:30:58','2026-11-15 00:30:58','2026-11-15 00:30:58'),(8,4,4,7,1,1,'2026-11-15 00:30:34','Selesai','Status diperbarui oleh Admin menjadi Selesai.',NULL,'2026-11-16 01:19:07','2026-11-16 01:19:07','2026-11-15 00:30:58'),(9,5,2,4,1,4,'2026-11-15 00:30:34','Disetujui','Status diperbarui oleh Admin menjadi Disetujui.','Disetujui dan ditandatangani oleh dosen pembimbing/wali.','2026-11-16 02:07:30','2026-11-16 01:45:54','2026-11-16 02:07:30'),(10,6,4,8,1,1,'2026-11-15 00:30:34','Ditolak',NULL,'Pengajuan tidak memenuhi kriteria keringanan UKT yang berlaku.','2026-11-15 00:30:58','2026-11-15 00:30:58','2026-11-15 00:30:58'),(12,4,2,9,1,4,'2026-11-16 02:04:37','Disetujui','Status diperbarui oleh Admin menjadi Disetujui.','Disetujui dan ditandatangani oleh dosen pembimbing/wali.','2026-11-16 02:06:56','2026-11-16 02:05:38','2026-11-16 02:06:56'),(13,6,1,10,1,1,'2026-11-16 03:16:01','Disetujui','Status diperbarui oleh Admin menjadi Diproses.','Disetujui dan ditandatangani oleh dosen kepala jurusan dengan catatan datang Metasys','2026-11-16 03:18:21','2026-11-16 03:16:46','2026-11-16 03:18:22');
/*!40000 ALTER TABLE `pengajuan` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-16  3:36:18
