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


def pdf_processing(file_name, jenis_pemindahan):
    current_directory = os.getcwd()
    
    # Path ke file input PDF
    file_name = f"{file_name}"
    jenis_pemindahan = jenis_pemindahan

    # input_pdf_path = f"input\\{file_name}.pdf"
    # input_pdf_path = f"input/{file_name}.pdf"
    input_pdf_path = os.path.join(current_directory, "input", f"{file_name}.pdf")

    if jenis_pemindahan == "Mutasi":
        x_nip = 135 # semakin besar semakin ke kanan
        y_nip = 745 # semakin besar semakin ke bawah
        w_nip = x_nip - 50 # semakin besar semakin lebar
        h_nip = 100 # semakin besar semakin tinggi
        box_nip = (x_nip, y_nip, x_nip + w_nip, y_nip + h_nip)
    else:
        # x1_name, y1_name, x2_name, y2_name = 310, 580, 770, 725
        x1_nip, y1_nip, x2_nip, y2_nip = 180, 580, 300, 725

    # nip_xy = (x1_nip, y1_nip, x2_nip, y2_nip)
    # nama_xy = (x1_name, y1_name, x2_name, y2_name)

    # Direktori output untuk gambar hasil crop
    # output_crop_dir = "cropped_images"
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
            # cropped_image_nama = page_image.crop(nama_xy)
            cropped_image_nip = page_image.crop(box_nip)

            
            # OCR untuk nama dan NIP
            # text_nama = pytesseract.image_to_string(
            #     cropped_image_nama, lang='eng')
            # text_nama = re.sub(r'[\\/*?:"<>|]', "", text_nama).strip().replace(
            #     "\n", " ").replace("\r", "").replace(".", "")

            text_nip = pytesseract.image_to_string(
                cropped_image_nip, lang='eng')
            # text_nip = re.sub(r'[\\/*?:"<>|]', "", text_nip).strip().replace(
            #     "\n", " ").replace("\r", "").replace(".", "")
            # ambil hanya angka dari text_nip
            text_nip = re.sub(r'[^0-9]', '', text_nip)
            
            # Simpan hasil crop
            # output_image_path_nama = os.path.join(
            #     output_crop_dir, f"nama_{text_nama}_{i+1}.png")
            output_image_path_nip = os.path.join(
                output_crop_dir, f"nip_{text_nip}_{i+1}.png")

            # cropped_image_nama.save(output_image_path_nama)
            cropped_image_nip.save(output_image_path_nip)
            

            # Simpan PDF final menggunakan text NIP dan Nama
            # output_filename = f"output\\{file_name}\\{text_nip}_{text_nama}.pdf"
            output_filename = os.path.join(
                current_directory, "output", file_name, f"{text_nip}_.pdf")
            with open(output_filename, "wb") as output_pdf:
                writer.write(output_pdf)

            # Menyelesaikan file sementara dan menghapusnya
            print(
                f"PDF dan gambar berhasil dibuat untuk NIP: {text_nip}")
            # os.remove(output_image_path_nama)
            # os.remove(output_image_path_nip)
        # os.rmdir(output_crop_dir)
        print("Semua file berhasil dibuat.")


if __name__ == "__main__":
    # while True:
        # jenis_pemindahan = input(
        #     "Masukkan jenis pemindahan (Mutasi/Promosi): ").strip().capitalize()
        # if jenis_pemindahan in ["Mutasi", "Promosi"]:
        #     break
        # else:
        #     print("Input tidak valid. Silakan masukkan 'Mutasi' atau 'Promosi'.\n")
    jenis_pemindahan = "Mutasi"  # Ubah sesuai kebutuhan
    file_list = os.listdir("input")
    for file_path in file_list:
        file_name = os.path.splitext(file_path)[0]
        pdf_processing(file_name, jenis_pemindahan)
