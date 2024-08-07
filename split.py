import os
import json
import math

def my_split(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        
        total_length = len(file_content)
        chunk_size = math.ceil(total_length / 3)
        
        chunks = [file_content[i:i + chunk_size] for i in range(0, total_length, chunk_size)]
        
        json_data = {}
        base_name = os.path.basename(file_path).split('.')[0]
        
        for i, chunk in enumerate(chunks):
            json_data[f"{base_name}_{i+1}"] = chunk
        
        return json_data
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

