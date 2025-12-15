if menu == "Pinjaman":
    st.subheader("Simulasi Pinjaman")

    pinjaman_txt = st.text_input("Jumlah Pinjaman (Rp)")
    angsuran_txt = st.text_input("Angsuran / Setoran Bulanan (Rp)")
    bunga_txt = st.text_input("Bunga Tahunan (%)")
    tenor = st.slider("Tenor Pinjaman (bulan)", 1, 120, 12)

    inputs = [pinjaman_txt, angsuran_txt, bunga_txt]

    submit_pinjaman = st.button("💰 Submit Simulasi Pinjaman")

    if all(i == "" for i in inputs):
        st.warning("Silakan isi seluruh data.")
    elif not all(valid_format(i) for i in inputs if i != ""):
        st.error("❌ Format angka salah. Gunakan titik ribuan dan koma desimal.")
    elif submit_pinjaman:
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

            lama_bayar = df["Bulan"].iloc[-1]
            total_bayar = lama_bayar * angsuran

            st.success(
                f"""
                📌 **Ringkasan Simulasi Pinjaman**
                - Jumlah Pinjaman : Rp {format_id(pinjaman)}
                - Angsuran Bulanan : Rp {format_id(angsuran)}
                - Lama Pelunasan : {lama_bayar} bulan
                - Total Pembayaran : Rp {format_id(total_bayar)}
                """
            )
