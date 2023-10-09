import hashlib
import os

def calculate_md5(file_path):
    """
    Menghitung nilai MD5 hash dari sebuah file.
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        while True:
            data = file.read(8192)  # Membaca file dalam potongan-potongan 8192 byte
            if not data:
                break
            md5_hash.update(data)
    return md5_hash.hexdigest()


def compare_files(file1_path, file2_path):
    """
    Membandingkan dua file berdasarkan nilai MD5 hash-nya.
    """
    md5_file1 = calculate_md5(file1_path)
    md5_file2 = calculate_md5(file2_path)

    if md5_file1 == md5_file2:
        return True
    else:
        return False
