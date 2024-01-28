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
    
def is_same_dirname(path1, path2):
    if os.path.basename(path1) == os.path.basename(path2):
        return True
    else: 
        return False

def get_inode(path):
    return os.stat(path).st_ino

def is_same_inode(dir1, dir2):
    return get_inode(dir1) == get_inode(dir2)
def get_absolute_path(self, directory_path):
    try:
        # Dapatkan absolute path dari suatu direktori
        absolute_path = os.path.abspath(directory_path)
        return absolute_path
    except Exception as e:
        print(f"Error in get_absolute_path: {str(e)}")
        return None
        

