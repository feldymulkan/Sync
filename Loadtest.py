import threading
import requests
import time

# List untuk menyimpan waktu respons setiap permintaan
response_times = []

# Fungsi untuk mengirimkan permintaan HTTP dan mencatat response time
def send_request(url, index):
    start_time = time.time()
    response = requests.get(url)
    end_time = time.time()
    response_time = (end_time - start_time) * 1000  # Konversi ke milidetik
    response_times.append(response_time)
    print(f"Request {index}: Response time = {response_time:.2f} milliseconds")

# Fungsi utama untuk melakukan load testing
def load_test(url, num_requests):
    print(f"Sending {num_requests} requests to {url}...")
    threads = []
    for i in range(num_requests):
        thread = threading.Thread(target=send_request, args=(url, i+1))
        threads.append(thread)
        thread.start()
    
    # Tunggu semua utas selesai
    for thread in threads:
        thread.join()
    
    # Menghitung rata-rata response time
    avg_response_time = sum(response_times) / len(response_times)
    print(f"Average Response Time: {avg_response_time:.2f} milliseconds")

if __name__ == "__main__":
    # URL website yang ingin diuji
    website_url = "http://192.168.73.5"
    
    # Jumlah permintaan yang akan dikirim
    num_requests = 1000
    
    # Melakukan load testing
    load_test(website_url, num_requests)
