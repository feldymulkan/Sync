import threading
import requests
import time
import csv

response_times = []
errors = []
successful_requests = 0  # Track successful requests
total_time = 0  # Track total time for testing

def send_request(url, index):
    global successful_requests, errors  # Global variables
    try:
        start_time = time.time()
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Request {index} failed with status code {response.status_code}")
        successful_requests += 1  # Increment successful requests
    except Exception as e:
        errors.append((index, str(e)))
    finally:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        response_times.append(response_time)
        print(f"Request {index}: Response time = {response_time:.2f} milliseconds")

def load_test(url, num_requests, ramp_up_time):
    global successful_requests, total_time, errors  # Global variables
    print(f"Sending {num_requests} requests to {url}...")
    threads = []
    start_time = time.time()
    for i in range(num_requests):
        thread = threading.Thread(target=send_request, args=(url, i+1))
        threads.append(thread)
        thread.start()
        time.sleep(ramp_up_time / num_requests)  # Adding ramp-up time

    for thread in threads:
        thread.join()

    total_time = time.time() - start_time
    print(f"Total Testing Time: {total_time:.2f} seconds")  # Print total testing time
    print(f"Successful Requests: {successful_requests}")
    print(f"Failed Requests: {len(errors)}")

    avg_response_time = sum(response_times) / len(response_times)
    throughput = successful_requests / total_time  # Calculate throughput (RPS)
    print(f"Average Response Time: {avg_response_time:.2f} milliseconds")
    print(f"Throughput: {throughput:.2f} requests/second")

    # Save results to CSV
    with open('load_test_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Request Index", "Response Time (ms)"])
        for idx, resp_time in enumerate(response_times):
            writer.writerow([idx + 1, resp_time])
    
    # Save errors to CSV
    with open('load_test_errors.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Request Index", "Error Message"])
        writer.writerows(errors)

if __name__ == "__main__":
    website_url = "http://172.16.28.251"
    num_requests = 1000
    ramp_up_time = 1  
    load_test(website_url, num_requests, ramp_up_time)
