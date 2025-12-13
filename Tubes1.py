import streamlit as st
import numpy as np
import pandas as pd
import re

st.set_page_config(page_title="Kalkulator Finansial", layout="centered")
st.title("Kalkulator Finansial Sederhana")

st.info(
    "📌 **Petunjuk Pengisian Angka**\n\n"
    "- Gunakan **titik (.)** untuk ribuan → contoh: 1.500.000\n"
    "- Gunakan **koma (,)** untuk desimal → contoh: 10,5\n"
    "- ❌ Jangan gunakan format lain (misal: 1,500,000)"
)

menu = st.sidebar.selectbox("Pilih Simulasi", ["Tabungan", "Pinjaman"])

def valid_format(teks):
    pola = r'^(\d{1,3}(\.\d{3})*|\d+)(,\d+)?$'
    return re.match(pola, teks) is not None

def rupiah_to_float(teks):
    return float(teks.replace(".", "").replace(",", "."))

def format_id(angka):
    s = f"{angka:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s

if menu == "Tabungan":
    st.subheader("Simulasi Tabungan")

    saldo_txt = st.text_input("Saldo Awal (Rp)")
    setoran_txt = st.text_input("Setoran Bulanan (Rp)")
    bunga_txt = st.text_input("Bunga Tahunan (%)")
    bulan = st.slider("Lama Menabung (bulan)", 1, 120, 12)

    inputs = [saldo_txt, setoran_txt, bunga_txt]

    if all(i == "" for i in inputs):
        st.warning("Silakan isi seluruh data.")
    elif not all(valid_format(i) for i in inputs if i != ""):
        st.error("❌ Format angka salah. Gunakan titik ribuan dan koma desimal.")
    else:
        saldo_awal = rupiah_to_float(saldo_txt)
        setoran = rupiah_to_float(setoran_txt)
        bunga = rupiah_to_float(bunga_txt) / 100 / 12

        waktu = np.arange(0, bulan + 1)
        saldo = np.zeros(len(waktu))
        saldo[0] = saldo_awal

        for i in range(1, len(waktu)):
            saldo[i] = saldo[i - 1] * (1 + bunga) + setoran

        df = pd.DataFrame({
            "Bulan": waktu,
            "Saldo (Rp)": saldo
        })

        df_tampil = df.copy()
        df_tampil["Saldo (Rp)"] = df_tampil["Saldo (Rp)"].apply(format_id)

        st.write("### Tabel Perkembangan Saldo")
        st.dataframe(df_tampil)

        st.write("### Grafik Saldo Tabungan")
        st.line_chart(df.set_index("Bulan"))

        st.success(f"Saldo akhir: Rp {format_id(saldo[-1])}")

if menu == "Pinjaman":
    st.subheader("Simulasi Pinjaman")

    pinjaman_txt = st.text_input("Jumlah Pinjaman (Rp)")
    angsuran_txt = st.text_input("Angsuran / Setoran Bulanan (Rp)")
    bunga_txt = st.text_input("Bunga Tahunan (%)")
    tenor = st.slider("Tenor Pinjaman (bulan)", 1, 120, 12)

    inputs = [pinjaman_txt, angsuran_txt, bunga_txt]

    if all(i == "" for i in inputs):
        st.warning("Silakan isi seluruh data.")
    elif not all(valid_format(i) for i in inputs if i != ""):
        st.error("❌ Format angka salah. Gunakan titik ribuan dan koma desimal.")
    else:
        pinjaman = rupiah_to_float(pinjaman_txt)
        angsuran = rupiah_to_float(angsuran_txt)
        bunga = rupiah_to_float(bunga_txt) / 100 / 12

        sisa = pinjaman
        data = []

        for b in range(1, tenor + 1):
            bunga_bln = sisa * bunga
            pokok = angsuran - bunga_bln

            if pokok <= 0:
                st.error("❌ Angsuran terlalu kecil, utang tidak akan berkurang.")
                break

            sisa -= pokok
            if sisa < 0:
                sisa = 0

            data.append([b, sisa])

            if sisa == 0:
                break

        if len(data) > 0:
            df = pd.DataFrame(data, columns=["Bulan", "Sisa Utang (Rp)"])

            df_tampil = df.copy()
            df_tampil["Sisa Utang (Rp)"] = df_tampil["Sisa Utang (Rp)"].apply(format_id)

            st.write("### Tabel Sisa Utang")
            st.dataframe(df_tampil)

            st.write("### Grafik Sisa Utang")
            st.line_chart(df.set_index("Bulan"))

            st.success(f"Angsuran bulanan: Rp {format_id(angsuran)}")
