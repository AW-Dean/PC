import duckdb
import random
import string
from datetime import datetime
from zoneinfo import ZoneInfo

def generate_product_id():
    """Menghasilkan ID dengan format PROD-XXXXXX (6 karakter alfanumerik)"""
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choice(chars) for _ in range(6))
    return f"PROD-{random_str}"

def add_product(con):
    print("\n--- Form Tambah Produk ---")
    product_name = input("Masukkan Nama Product: ")
    category = input("Masukkan Kategori: ")
    
    if not product_name or not category:
        print("[Error] Nama produk dan kategori tidak boleh kosong.")
        return

    # Cek Duplikasi
    existing = con.execute(
        "SELECT product_id FROM product_catalog WHERE product_name = ? AND category = ?", 
        [product_name, category]
    ).fetchone()

    if existing:
        print(f"\n[WARNING] Produk dengan nama dan kategori yang sama sudah ada (ID: {existing[0]})")
        confirm = input("Tetap simpan sebagai data baru? (y/n): ")
        if confirm.lower() != 'y':
            print("Penyimpanan dibatalkan.")
            return

    # Generate data otomatis
    product_id = generate_product_id()
    wib_tz = ZoneInfo("Asia/Jakarta")
    created_at = datetime.now(wib_tz)
    
    con.execute("""
        INSERT INTO product_catalog (product_id, product_name, category, created_at)
        VALUES (?, ?, ?, ?)
    """, [product_id, product_name, category, created_at])
    
    print(f"\n[Berhasil] Data ditambahkan! ID: {product_id}")

def view_catalog(con):
    print("\n--- Katalog Produk ---")
    results = con.execute("SELECT * FROM product_catalog ORDER BY created_at DESC").fetchall()
    if not results:
        print("Katalog kosong.")
        return
    
    print(f"{'ID':<15} | {'Nama Produk':<25} | {'Kategori':<15} | {'Dibuat Pada'}")
    print("-" * 80)
    for row in results:
        print(f"{row[0]:<15} | {row[1]:<25} | {row[2]:<15} | {row[3]}")

def edit_product(con):
    print("\n--- Edit Produk ---")
    p_id = input("Masukkan Product ID yang akan diedit: ").strip()
    
    # Cek apakah ID ada
    target = con.execute("SELECT * FROM product_catalog WHERE product_id = ?", [p_id]).fetchone()
    if not target:
        print(f"[Error] Product ID {p_id} tidak ditemukan.")
        return

    print(f"Data saat ini: {target[1]} ({target[2]})")
    new_name = input(f"Nama baru (kosongkan jika tetap '{target[1]}'): ") or target[1]
    new_cat = input(f"Kategori baru (kosongkan jika tetap '{target[2]}'): ") or target[2]

    con.execute("""
        UPDATE product_catalog 
        SET product_name = ?, category = ? 
        WHERE product_id = ?
    """, [new_name, new_cat, p_id])
    
    print(f"✅ Product {p_id} berhasil diperbarui.")

def run_app():
    try:
        con = duckdb.connect('md:AWE_DB')
        
        con.execute("""
            CREATE TABLE IF NOT EXISTS product_catalog (
                product_id VARCHAR PRIMARY KEY,
                product_name VARCHAR,
                category VARCHAR,
                created_at TIMESTAMP
            )
        """)
        
        while True:
            print("\n=== AWE Product Management ===")
            print("1. Tambah Produk Baru")
            print("2. Lihat Katalog")
            print("3. Edit Produk")
            print("4. Keluar")
            
            pilihan = input("Pilih menu (1-4): ")
            
            if pilihan == '1':
                add_product(con)
            elif pilihan == '2':
                view_catalog(con)
            elif pilihan == '3':
                edit_product(con)
            elif pilihan == '4':
                print("Keluar dari aplikasi...")
                break
            else:
                print("Pilihan tidak valid.")

        con.close()
    except Exception as e:
        print(f"\n[Error] Terjadi kesalahan: {e}")

if __name__ == "__main__":
    run_app()