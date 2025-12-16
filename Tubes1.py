import streamlit as st
import numpy as np
import pandas as pd
import re
from io import BytesIO
import openpyxl
from openpyxl import load_workbook
from openpyxl.chart import LineChart, Reference

st.set_page_config(page_title="Kalkulator Finansial", layout="centered")
st.title("Kalkulator Finansial Sederhana")

st.info(
    "📌 Petunjuk:\n"
    "- Titik (.) untuk ribuan → 1.500.000\n"
    "- Koma (,) untuk desimal → 10,5"
)

menu = st.sidebar.selectbox("Pilih Simulasi", ["Tabungan", "Pinjaman"])

def valid_format(teks):
    return re.match(r'^(\d{1,3}(\.\d{3})*|\d+)(,\d+)?$', teks)

def rupiah_to_float(teks):
    return float(teks.replace(".", "").replace(",", "."))

def format_id(x):
    s = f"{x:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

# ================= TABUNGAN =================
if menu == "Tabungan":
    st.subheader("Simulasi Tabungan")

    saldo_txt = st.text_input("Saldo Awal (Rp)")
    setoran_txt = st.text_input("Setoran Bulanan (Rp)")
    bunga_txt = st.text_input("Bunga Tahunan (%)")
    bulan = st.slider("Lama Menabung (bulan)", 1, 120, 12)

    if st.button("Submit Tabungan"):
        if "" in [saldo_txt, setoran_txt, bunga_txt]:
            st.warning("Lengkapi data.")
        elif not all(valid_format(i) for i in [saldo_txt, setoran_txt, bunga_txt]):
            st.error("Format angka salah.")
        else:
            saldo_awal = rupiah_to_float(saldo_txt)
            setoran = rupiah_to_float(setoran_txt)
            bunga = rupiah_to_float(bunga_txt) / 100 / 12

            bulan_arr = np.arange(0, bulan + 1)
            saldo = np.zeros(len(bulan_arr))
            saldo[0] = saldo_awal

            for i in range(1, len(bulan_arr)):
                saldo[i] = saldo[i-1] * (1 + bunga) + setoran

            df = pd.DataFrame({"Bulan": bulan_arr, "Saldo (Rp)": saldo})

            st.dataframe(df.assign(
                **{"Saldo (Rp)": df["Saldo (Rp)"].apply(format_id)}
            ))
            st.line_chart(df.set_index("Bulan"))

            # ===== RINGKASAN TABUNGAN =====
            st.success(f"Total saldo akhir tabungan: Rp {format_id(saldo[-1])}")

            # ===== EXCEL TABUNGAN + GRAFIK =====
            buf = BytesIO()
            df.to_excel(buf, index=False, sheet_name="Tabungan", engine="openpyxl")
            buf.seek(0)

            wb = load_workbook(buf)
            ws = wb["Tabungan"]

            chart = LineChart()
            chart.title = "Grafik Saldo Tabungan"
            chart.x_axis.title = "Bulan"
            chart.y_axis.title = "Saldo (Rp)"

            y = Reference(ws, min_col=2, min_row=1, max_row=ws.max_row)
            x = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)

            chart.add_data(y, titles_from_data=True)
            chart.set_categories(x)
            ws.add_chart(chart, "E2")

            out = BytesIO()
            wb.save(out)
            out.seek(0)

            st.download_button(
                "📥 Download Excel Tabungan + Grafik",
                out,
                "hasil_tabungan.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ================= PINJAMAN =================
if menu == "Pinjaman":
    st.subheader("Simulasi Pinjaman")

    pinjaman_txt = st.text_input("Jumlah Pinjaman (Rp)")
    angsuran_txt = st.text_input("Angsuran Bulanan (Rp)")
    bunga_txt = st.text_input("Bunga Tahunan (%)")
    tenor = st.slider("Tenor (bulan)", 1, 120, 12)

    if st.button("Submit Pinjaman"):
        if "" in [pinjaman_txt, angsuran_txt, bunga_txt]:
            st.warning("Lengkapi data.")
        elif not all(valid_format(i) for i in [pinjaman_txt, angsuran_txt, bunga_txt]):
            st.error("Format angka salah.")
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
                    st.error("❌ Angsuran terlalu kecil.")
                    break
                sisa = max(sisa - pokok, 0)
                data.append([b, sisa])
                if sisa == 0:
                    break

            if data:
                df = pd.DataFrame(data, columns=["Bulan", "Sisa Utang (Rp)"])
                st.dataframe(df.assign(
                    **{"Sisa Utang (Rp)": df["Sisa Utang (Rp)"].apply(format_id)}
                ))
                st.line_chart(df.set_index("Bulan"))

                # ===== RINGKASAN PINJAMAN =====
                total_bayar = angsuran * len(data)
                total_bunga = total_bayar - pinjaman

                st.success(f"Angsuran bulanan: Rp {format_id(angsuran)}")
                st.info(f"Total pembayaran: Rp {format_id(total_bayar)}")
                st.info(f"Total bunga dibayar: Rp {format_id(total_bunga)}")
                st.success(f"Lunas dalam {len(data)} bulan")
                st.info(f"Jumlah pinjaman awal: Rp {format_id(pinjaman)}")

                lama_bulan = len(data)
                lama_hari = lama_bulan * 30
                lama_tahun = lama_bulan // 12
                sisa_bulan = lama_bulan % 12

                st.info(
                    f"Lama pembayaran: "
                    f"{lama_hari} hari / "
                    f"{lama_bulan} bulan / "
                    f"{lama_tahun} tahun {sisa_bulan} bulan"
                )

                # ===== EXCEL PINJAMAN + GRAFIK =====
                buf = BytesIO()
                df.to_excel(buf, index=False, sheet_name="Pinjaman", engine="openpyxl")
                buf.seek(0)

                wb = load_workbook(buf)
                ws = wb["Pinjaman"]

                chart = LineChart()
                chart.title = "Grafik Sisa Utang"
                chart.x_axis.title = "Bulan"
                chart.y_axis.title = "Sisa Utang (Rp)"

                y = Reference(ws, min_col=2, min_row=1, max_row=ws.max_row)
                x = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)

                chart.add_data(y, titles_from_data=True)
                chart.set_categories(x)
                ws.add_chart(chart, "E2")

                out = BytesIO()
                wb.save(out)
                out.seek(0)

                st.download_button(
                    "📥 Download Excel Pinjaman + Grafik",
                    out,
                    "hasil_pinjaman.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
