import os

def find_directory_containing_file(start_path, target_file):
    def _search_recursive(path):
        try:
            items = os.listdir(path)
        except OSError:
            return

        for item in items:
            item_path = os.path.join(path, item)

            if os.path.isdir(item_path):
                result = _search_recursive(item_path)
                if result:
                    return result
            elif item == target_file:
                return path

    if os.path.exists(start_path):
        print("Searching for:", target_file)
        result = _search_recursive(start_path)
        if result:
            print(f"File '{target_file}' found in directory:")
            print(result)
        else:
            print(f"File '{target_file}' not found in any subdirectory.")
    else:
        print("Folder not found")

if __name__ == "__main__":
    start_path = "/home"  # Ganti dengan path direktori yang ingin Anda mulai pencarian
    target_file = "tes.txt"    # Ganti dengan nama file yang ingin Anda cari
    find_directory_containing_file(start_path, target_file)
