#!/usr/bin/env python
import pika
import json
import split

# Path to the JSON file for metadata
metadata_file = 'metadata.json'

# Load existing metadata if available
try:
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
except FileNotFoundError:
    metadata = {}

def update_metadata(file_name, chunk_id, worker_id):
    if file_name not in metadata:
        metadata[file_name] = {}
    if worker_id not in metadata[file_name]:
        metadata[file_name][worker_id] = []
    metadata[file_name][worker_id].append(chunk_id)
    
    # Save updated metadata to file
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)

# Establish connection to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
channel = connection.channel()

# Declare an exchange of type 'topic'
channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

# Define worker routing keys
worker_routing_keys = ['worker1', 'worker2', 'worker3']

# Initialize round-robin index
try:
    with open('round_robin_index.txt', 'r') as f:
        round_robin_index = int(f.read())
except FileNotFoundError:
    round_robin_index = 0

def get_next_worker():
    global round_robin_index
    worker = worker_routing_keys[round_robin_index]
    round_robin_index = (round_robin_index + 1) % len(worker_routing_keys)
    
    # Save updated round-robin index to file
    with open('round_robin_index.txt', 'w') as f:
        f.write(str(round_robin_index))
    
    return worker

# Read and split the message
message = split.my_split("try2.txt")
print(message)

# Publish each chunk to the next worker in round-robin fashion and update metadata
for chunk_id, chunk_data in message.items():
    selected_worker = get_next_worker()  # Get the next worker in round-robin
    print(f"Publishing to {selected_worker}: {chunk_data}")
    
    # Publish chunk to RabbitMQ
    channel.basic_publish(
        exchange='topic_logs',
        routing_key=selected_worker,
        body=json.dumps({chunk_id: chunk_data})
    )
    
    # Update metadata
    update_metadata("try2.txt", chunk_id, selected_worker)

print(" [x] Messages sent and metadata updated")
connection.close()
