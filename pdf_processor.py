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


def pdf_processing(file_name, jenis_pemindahan):
    current_directory = os.getcwd()
    
    # Path ke file input PDF
    file_name = f"{file_name}"
    jenis_pemindahan = jenis_pemindahan


    input_pdf_path = os.path.join(current_directory, "input", f"{file_name}.pdf")
    
    

    # Tentukan koordinat crop berdasarkan jenis pemindahan
    if jenis_pemindahan == "Mutasi":
        x_nip = 135 # semakin besar semakin ke kanan
        y_nip = 765 # semakin besar semakin ke bawah
        w_nip = 250 # semakin besar semakin lebar
        h_nip = 1540 # semakin besar semakin tinggi
        box_nip = (x_nip,y_nip,w_nip,h_nip)
        
        x_nama = 240 # semakin besar semakin ke kanan
        y_nama = 750 # semakin besar semakin ke bawah
        w_nama = 480 # semakin besar semakin lebar
        h_nama = 930 # semakin besar semakin tinggi
        box_nama = (x_nama,y_nama,w_nama,h_nama)
        
    else:
        
        x_nip = 180 # semakin besar semakin ke kanan
        y_nip = 580 # semakin besar semakin ke bawah
        w_nip = 95 # semakin besar semakin lebar
        h_nip = 145 # semakin besar semakin tinggi
        box_nip = (x_nip,y_nip,x_nip + w_nip,y_nip + h_nip)
        print(box_nip)
        
        x_nama = 310 # semakin besar semakin ke kanan
        y_nama = 580 # semakin besar semakin ke bawah
        w_nama = 460 # semakin besar semakin lebar
        h_nama = 145 # semakin besar semakin tinggi
        box_nama = (x_nama,y_nama,x_nama + w_nama,y_nama + h_nama)
        print(box_nama)
        
        x_satker = 980   # semakin besar semakin ke kanan
        y_satker = 550   # semakin besar semakin ke bawah
        w_satker = 260   # semakin besar semakin lebar
        h_satker = 145   # semakin besar semakin tinggi
        box_satker = (x_satker,y_satker,x_satker + w_satker,y_satker + h_satker)
        print(box_satker)
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
                input_pdf_path, first_page=i+1, last_page=i+1,
                # poppler_path=os.path.join(current_directory, "dependencies", "poppler", "Library", "bin")
                )
            page_image = images[0]

            # Crop area yang dimaksud
            cropped_image_nip = page_image.crop(box_nip)
            cropped_image_nama = page_image.crop(box_nama)
            # cropped_image_satker = page_image.crop(box_satker)

            
            # OCR untuk nama dan NIP

            text_nip = pytesseract.image_to_string(
                cropped_image_nip, lang='eng')
            text_nip = re.sub(r'[^0-9]', '', text_nip)
        
            text_nama = pytesseract.image_to_string(
                cropped_image_nama, lang='eng')
            # Bersihkan teks nama dari karakter yang tidak diinginkan
            text_nama = re.sub(r'[^a-zA-Z\s]', '', text_nama).strip()
            text_nama = text_nama.replace("\n", " ").strip()

            print(f"Extracted Name: {text_nama}")
            

            output_image_path_nip = os.path.join(
                output_crop_dir, f"nip_{text_nip}_{i+1}.png")
            
            output_image_path_nama = os.path.join(
                output_crop_dir, f"nama_{text_nama}_{i+1}.png")
            
            cropped_image_nip.save(output_image_path_nip)
            cropped_image_nama.save(output_image_path_nama)
            
            if jenis_pemindahan == "Promosi":
                cropped_image_satker = page_image.crop(box_satker)
                text_satker = pytesseract.image_to_string(
                    cropped_image_satker, lang='eng')
                text_satker = re.sub(r'[^a-zA-Z0-9\-\s]', '', text_satker).strip()
                text_satker = re.sub(r"\s+", " ", text_satker).strip()

                
                output_image_path_satker = os.path.join(
                output_crop_dir, f"satker_{text_satker}_{i+1}.png")
                cropped_image_satker.save(output_image_path_satker)
            else:
                text_satker = file_name
            
            
            

            # Simpan PDF final menggunakan text NIP, Satker dan Nama
            output_filename = os.path.join(
                current_directory, "output", file_name, f"{text_nip}__{text_satker}__{text_nama}__.pdf")
            with open(output_filename, "wb") as output_pdf:
                writer.write(output_pdf)

            # Menyelesaikan file sementara dan menghapusnya
            
            # print(
            #     f"PDF dan gambar berhasil dibuat untuk file: {text_nip}__{satker_pegawai}__{nama_pegawai}.pdf")
            # if text_nip:  # Pastikan text_nip tidak kosong
            #     os.remove(output_image_path_nip)
            
        # menghapus semua file gambar di folder cropped_images
        for temp_file in os.listdir(output_crop_dir):
            temp_file_path = os.path.join(output_crop_dir, temp_file)
            os.remove(temp_file_path)
        print("Semua file berhasil dibuat.")


if __name__ == "__main__":
    while True:
        jenis_pemindahan = input(
            "Masukkan jenis pemindahan (Mutasi/Promosi): ").strip().capitalize()
        if jenis_pemindahan in ["Mutasi", "Promosi"]:
            break
        else:
            print("Input tidak valid. Silakan masukkan 'Mutasi' atau 'Promosi'.\n")
    # jenis_pemindahan = "Promosi"  # Ubah sesuai kebutuhan
    file_list = os.listdir("input")
    # Baca database pegawai
    # df_pegawai.nip = df_pegawai.nip.astype(int).astype(str)
    for file_path in file_list:
        file_name = os.path.splitext(file_path)[0]
        print(f"Processing file: {file_name}")
        pdf_processing(file_name, jenis_pemindahan)
