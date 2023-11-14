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


def compare_md5(file1_path, file2_path):
    md5_file1 = calculate_md5(file1_path)
    md5_file2 = calculate_md5(file2_path)
    return md5_file1 == md5_file2
    
def is_same_filename(path1, path2):
    if os.path.basename(path1) == os.path.basename(path2):
        return True
    else: 
        return False
        
        
