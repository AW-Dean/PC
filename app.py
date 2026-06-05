import streamlit as st
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

def run_app():
    st.set_page_config(page_title="AWE Product Management", layout="wide")
    st.title("📦 AWE Product Management")

    try:
        # Koneksi ke MotherDuck
        con = duckdb.connect('md:AWE_DB')
        con.execute("""
            CREATE TABLE IF NOT EXISTS product_catalog (
                product_id VARCHAR PRIMARY KEY,
                product_name VARCHAR,
                category VARCHAR,
                created_at TIMESTAMPTZ
            )
        """)

        # Membuat Tab UI
        tab1, tab2, tab3, tab4 = st.tabs(["➕ Tambah Produk", "📋 Lihat Katalog", "✏️ Edit Produk", "🗑️ Hapus Produk"])

        with tab1:
            st.subheader("Tambah Produk Baru")
            with st.form("add_form", clear_on_submit=True):
                p_name = st.text_input("Nama Product")
                p_cat = st.text_input("Kategori")
                submitted = st.form_submit_button("Simpan Data")

                if submitted:
                    if p_name and p_cat:
                        # Cek Duplikasi
                        existing = con.execute(
                            "SELECT product_id FROM product_catalog WHERE product_name = ? AND category = ?", 
                            [p_name, p_cat]
                        ).fetchone()

                        if existing:
                            st.warning(f"Produk dengan nama dan kategori yang sama sudah ada (ID: {existing[0]})")
                        
                        # Tetap proses insert
                        p_id = generate_product_id()
                        wib_tz = ZoneInfo("Asia/Jakarta")
                        created_at = datetime.now(wib_tz)
                        
                        con.execute("""
                            INSERT INTO product_catalog (product_id, product_name, category, created_at)
                            VALUES (?, ?, ?, ?)
                        """, [p_id, p_name, p_cat, created_at])
                        st.success(f"Berhasil! Data ditambahkan dengan ID: {p_id}")
                    else:
                        st.error("Nama dan Kategori wajib diisi!")

        with tab2:
            st.subheader("Katalog Produk")
            df = con.execute("SELECT * FROM product_catalog ORDER BY product_name ASC").df()
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Katalog masih kosong.")

        with tab3:
            st.subheader("Edit Produk")
            # Mengambil nama dan ID untuk selection yang lebih informatif
            items = con.execute("SELECT product_id, product_name FROM product_catalog ORDER BY product_name ASC").fetchall()
            product_options = {f"{r[1]} ({r[0]})": r[0] for r in items}
            
            selected_label = st.selectbox("Pilih Produk yang akan diedit", ["-- Pilih Produk --"] + list(product_options.keys()))
            
            if selected_label != "-- Pilih Produk --":
                selected_id = product_options[selected_label]
                target = con.execute("SELECT * FROM product_catalog WHERE product_id = ?", [selected_id]).fetchone()
                
                with st.form("edit_form"):
                    new_name = st.text_input("Nama Baru", value=target[1])
                    new_cat = st.text_input("Kategori Baru", value=target[2])
                    update_btn = st.form_submit_button("Update Data")
                    
                    if update_btn:
                        con.execute("""
                            UPDATE product_catalog 
                            SET product_name = ?, category = ? 
                            WHERE product_id = ?
                        """, [new_name, new_cat, selected_id])
                        st.success(f"Produk {selected_id} berhasil diperbarui!")
                        st.rerun()

        with tab4:
            st.subheader("Hapus Produk")
            # Menggunakan logika selection yang sama dengan Tab Edit
            items_del = con.execute("SELECT product_id, product_name FROM product_catalog ORDER BY product_name ASC").fetchall()
            del_options = {f"{r[1]} ({r[0]})": r[0] for r in items_del}
            
            selected_del_label = st.selectbox("Pilih Produk yang akan dihapus", ["-- Pilih Produk --"] + list(del_options.keys()))
            
            if selected_del_label != "-- Pilih Produk --":
                selected_del_id = del_options[selected_del_label]
                
                st.warning(f"⚠️ **Peringatan:** Anda akan menghapus produk **{selected_del_label}**. Tindakan ini tidak dapat dibatalkan.")
                
                # Checkbox konfirmasi sesuai permintaan
                confirm_delete = st.checkbox("Saya benar-benar yakin ingin menghapus data ini secara permanen.")
                
                if st.button("Hapus Produk Sekarang", type="primary", disabled=not confirm_delete):
                    try:
                        con.execute("DELETE FROM product_catalog WHERE product_id = ?", [selected_del_id])
                        st.success(f"Produk {selected_del_id} telah berhasil dihapus.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menghapus data: {e}")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    run_app()