-- Script untuk inisialisasi database PostgreSQL
-- File ini akan dijalankan otomatis saat container PostgreSQL pertama kali dibuat

-- Buat extension jika diperlukan
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Insert sample employees (akan diabaikan jika sudah ada karena aplikasi sudah handle ini)
-- Ini hanya backup jika aplikasi tidak berjalan dengan benar

-- Catatan: Tabel akan dibuat otomatis oleh aplikasi Flask
-- Script ini hanya untuk setup tambahan jika diperlukan