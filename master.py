#!/usr/bin/env python
import pika
import json
import split

# Path to the JSON file for metadata
metadata_file = 'metadata.json'

# Define global worker routing keys
worker_routing_keys = ['worker1', 'worker2', 'worker3']

def load_metadata():
    """Load existing metadata from file."""
    try:
        with open(metadata_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def update_metadata(file_name, chunk_id, worker_id):
    """Update metadata with chunk information."""
    if file_name not in metadata:
        metadata[file_name] = {}
    if worker_id not in metadata[file_name]:
        metadata[file_name][worker_id] = []
    metadata[file_name][worker_id].append(chunk_id)
    
    # Save updated metadata to file
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)

def get_next_worker():
    """Get the next worker in round-robin fashion."""
    global round_robin_index
    global worker_routing_keys
    worker = worker_routing_keys[round_robin_index]
    round_robin_index = (round_robin_index + 1) % len(worker_routing_keys)
    
    # Save updated round-robin index to file
    with open('round_robin_index.txt', 'w') as f:
        f.write(str(round_robin_index))
    
    return worker

def send_file(file_path):
    """Send file chunks to workers and update metadata."""
    global round_robin_index
    
    # Establish connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
    channel = connection.channel()

    # Declare an exchange of type 'topic'
    channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

    # Initialize round-robin index
    try:
        with open('round_robin_index.txt', 'r') as f:
            round_robin_index = int(f.read())
    except FileNotFoundError:
        round_robin_index = 0

    # Read and split the message
    message = split.my_split(file_path)
    if message is None:
        print(f"Failed to split file: {file_path}")
        return

    print(f"Split message from {file_path}: {message}")

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
        update_metadata(file_path, chunk_id, selected_worker)

    print(" [x] Messages sent and metadata updated")
    connection.close()

def main():
    """Main function to load metadata and process files."""
    global metadata
    metadata = load_metadata()
    
    # Specify the file to send
    file_path = "try3.txt"
    
    # Send the file and update metadata
    send_file(file_path)

if __name__ == "__main__":
    main()
