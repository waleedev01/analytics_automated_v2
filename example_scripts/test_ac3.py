import os
import requests
import time

def test_cwl_files(directory, api_url, response_file):
    all_times = []
    valid_count = 0
    total_files = 0
    
    for filename in os.listdir(directory):
        if filename.endswith('.cwl'):
            total_files += 1
            file_path = os.path.join(directory, filename)
            
            with open(file_path, 'rb') as f:
                start_time = time.time()
                response = requests.post(api_url, files={'file': f})
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  
                all_times.append(response_time)
                
                with open(response_file, 'a') as rf:
                    rf.write(f"{filename}: {response_time} ms\n")
                
                if response.ok and response_time <= 500:
                    valid_count += 1
    
    if total_files > 0:
        success_rate = (valid_count / total_files) * 100
        print(f"Total files tested: {total_files}")
        print(f"Files processed in ≤ 500 ms: {valid_count}")
        print(f"Success rate: {success_rate:.2f}%")
    else:
        print("No CWL files found in the directory.")

if __name__ == '__main__':
    #test_directory = '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen-cwl/'
    test_directory = '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/example_cwl_files/'
    api_url = 'http://localhost:8000/upload'
    response_file = 'response.txt'
    
    if os.path.exists(response_file):
        os.remove(response_file)
    
    test_cwl_files(test_directory, api_url, response_file)

