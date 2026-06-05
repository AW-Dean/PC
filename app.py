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
        tab1, tab2, tab3 = st.tabs(["➕ Tambah Produk", "📋 Lihat Katalog", "✏️ Edit Produk"])

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
            catalog_ids = con.execute("SELECT product_id FROM product_catalog").fetchall()
            id_list = [r[0] for r in catalog_ids]
            
            selected_id = st.selectbox("Pilih Product ID yang akan diedit", ["-- Pilih ID --"] + id_list)
            
            if selected_id != "-- Pilih ID --":
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

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    run_app()