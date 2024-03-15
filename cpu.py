import psutil
import tkinter as tk

# Fungsi untuk memperbarui label dengan persentase CPU dan RAM yang baru
def update_labels():
    cpu_percent = psutil.cpu_percent(interval=1)
    ram_percent = psutil.virtual_memory().percent
    cpu_label.config(text=f"CPU Usage: {cpu_percent:.2f}%")
    ram_label.config(text=f"RAM Usage: {ram_percent:.2f}%")
    root.after(1000, update_labels)  # Memperbarui setiap 1 detik

# Membuat jendela utama
root = tk.Tk()
root.title("System Monitor")

# Membuat label untuk menampilkan persentase CPU dan RAM
cpu_label = tk.Label(root, text="")
cpu_label.pack()
ram_label = tk.Label(root, text="")
ram_label.pack()

# Memulai pembaruan label
update_labels()

# Menjalankan loop utama
root.mainloop()
