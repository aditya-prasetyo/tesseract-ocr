"""
Code di bawah ini digunakan untuk:
- Menentukan file PDF input yang akan diproses.
- Menentukan jenis pemindahan yang digunakan (Mutasi atau Promosi) untuk menentukan koordinat crop.
- Membaca file PDF menggunakan PyPDF2 dan memeriksa jumlah halamannya.
- Mengonversi halaman PDF menjadi gambar.
- Memotong gambar sesuai dengan koordinat yang telah ditentukan untuk mengambil teks (Nama dan NIP).
- Menggunakan OCR (pytesseract) untuk mengekstrak teks dari gambar yang telah dipotong.
- Menyimpan gambar hasil crop ke dalam direktori yang telah ditentukan.
- Membuat file PDF baru dengan nama file yang disesuaikan berdasarkan teks hasil OCR (NIP dan Nama).
- Menangani proses pembersihan teks dengan menghapus karakter yang tidak diinginkan dan mengganti karakter khusus.
- Menghapus file gambar sementara setelah proses selesai.
- Menangani error jika jumlah halaman PDF kurang dari 2 atau jika terjadi masalah selama pemrosesan.
"""


from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import os
import re
import pytesseract
import pandas as pd


def pdf_processing(file_name, jenis_pemindahan,database_pegawai):
    current_directory = os.getcwd()
    
    # Path ke file input PDF
    file_name = f"{file_name}"
    jenis_pemindahan = jenis_pemindahan


    input_pdf_path = os.path.join(current_directory, "input", f"{file_name}.pdf")
    
    

    # Tentukan koordinat crop berdasarkan jenis pemindahan
    if jenis_pemindahan == "Mutasi":
        x_nip = 135 # semakin besar semakin ke kanan
        y_nip = 745 # semakin besar semakin ke bawah
        w_nip = 220 # semakin besar semakin lebar
        h_nip = 1540 # semakin besar semakin tinggi
        box_nip = (x_nip,y_nip,w_nip,h_nip)
    else:
        x_nip = 130 # semakin besar semakin ke kanan
        y_nip = 700 # semakin besar semakin ke bawah
        w_nip = 210 # semakin besar semakin lebar
        h_nip = 1430 # semakin besar semakin tinggi
        box_nip = (x_nip,y_nip,w_nip,h_nip)

    output_crop_dir = os.path.join(current_directory, "cropped_images")
    os.makedirs(output_crop_dir, exist_ok=True)

    # output_satker = f"output\\{file_name}"
    output_satker = os.path.join(current_directory, "output", file_name)
    os.makedirs(output_satker, exist_ok=True)

    # Baca PDF
    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)

    if total_pages < 2:
        print("File PDF harus memiliki minimal 2 halaman.")
    else:
        # Ambil halaman pertama
        page_1 = reader.pages[0]

        for i in range(1, total_pages):
            writer = PdfWriter()
            writer.add_page(page_1)
            writer.add_page(reader.pages[i])

            # Konversi halaman ke gambar
            images = convert_from_path(
                input_pdf_path, first_page=i+1, last_page=i+1,poppler_path=os.path.join(current_directory, "dependencies", "poppler", "Library", "bin"))
            page_image = images[0]

            # Crop area yang dimaksud
            cropped_image_nip = page_image.crop(box_nip)

            
            # OCR untuk nama dan NIP

            text_nip = pytesseract.image_to_string(
                cropped_image_nip, lang='eng')
            text_nip = re.sub(r'[^0-9]', '', text_nip)
            
            nip_not_found = []
            
            # Jika NIP ada di database, ambil nama dan satker yang sesuai
            if text_nip in database_pegawai.nip.values:
                nama_pegawai = database_pegawai.loc[database_pegawai['nip'] == text_nip, 'nama'].values[0]
                satker_pegawai = database_pegawai.loc[database_pegawai['nip'] == text_nip, 'satker'].values[0]
            else:
                nip_not_found.append(text_nip)
            

            output_image_path_nip = os.path.join(
                output_crop_dir, f"nip_{text_nip}_{i+1}.png")

            # cropped_image_nama.save(output_image_path_nama)
            cropped_image_nip.save(output_image_path_nip)
            

            # Simpan PDF final menggunakan text NIP, Satker dan Nama
            output_filename = os.path.join(
                current_directory, "output", file_name, f"{text_nip}__{satker_pegawai}__{nama_pegawai}.pdf")
            with open(output_filename, "wb") as output_pdf:
                writer.write(output_pdf)

            # Menyelesaikan file sementara dan menghapusnya
            print(
                f"PDF dan gambar berhasil dibuat untuk file: {text_nip}__{satker_pegawai}__{nama_pegawai}.pdf")
            os.remove(output_image_path_nip)
        # write log NIP tidak ditemukan
        if nip_not_found:
            with open(os.path.join(current_directory, "output", file_name, "nip_not_found.txt"), "w") as log_file:
                for nip in nip_not_found:
                    log_file.write(f"NIP tidak ditemukan: {nip}\n")
        os.rmdir(output_crop_dir)
        print("Semua file berhasil dibuat.")


if __name__ == "__main__":
    while True:
        jenis_pemindahan = input(
            "Masukkan jenis pemindahan (Mutasi/Promosi): ").strip().capitalize()
        if jenis_pemindahan in ["Mutasi", "Promosi"]:
            break
        else:
            print("Input tidak valid. Silakan masukkan 'Mutasi' atau 'Promosi'.\n")
    # jenis_pemindahan = "Mutasi"  # Ubah sesuai kebutuhan
    file_list = os.listdir("input")
    # Baca database pegawai
    df_pegawai = pd.read_excel('./database_pegawai/database_pegawai_main.xlsx', dtype={'nip': str})
    # df_pegawai.nip = df_pegawai.nip.astype(int).astype(str)
    for file_path in file_list:
        file_name = os.path.splitext(file_path)[0]
        print(f"Processing file: {file_name}")
        pdf_processing(file_name, jenis_pemindahan,df_pegawai)
