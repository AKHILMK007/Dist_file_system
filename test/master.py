import pika
import json
import os
import threading

# Load metadata from a JSON file
def load_metadata():
    with open('metadata.json', 'r') as file:
        return json.load(file)

# Ensure the received files directory exists
def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to handle responses from workers
received_chunks = {}  # Dictionary to hold received chunks
stop_signal = threading.Event()  # Thread-safe event to signal stopping

def on_response(ch, method, properties, body, filename, metadata, channel):
    chunk_data = json.loads(body)
    for chunk_id, chunk_content in chunk_data.items():
        print(f"Received {chunk_id} from worker")
        received_chunks[chunk_id] = chunk_content
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # Check if all chunks have been received
    total_chunks = sum(len(chunks) for chunks in metadata[filename].values())
    if len(received_chunks) == total_chunks:
        print("All chunks received. Writing to file...")
        # Sort the chunks by chunk order and write them in the correct order
        sorted_chunks = sorted(received_chunks.items(), key=lambda x: int(x[0].split('_')[-1]))  # Sort by chunk order
        with open(os.path.join('received_files', f'{filename}_retrieved.txt'), 'w') as output_file:
            for _, chunk_content in sorted_chunks:
                output_file.write(chunk_content)
        stop_signal.set()  # Signal to stop consuming

def request_file_chunks(filename, metadata):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
    channel = connection.channel()

    if filename not in metadata:
        print(f"File {filename} not found in metadata.")
        return

    # Ensure the directory for received files exists
    ensure_directory('received_files')

    # Declare queues for each worker
    for worker in metadata[filename]:
        queue_name = f'file_response_{worker}'
        channel.queue_declare(queue=queue_name)

    # Register consumers for each worker queue
    for worker in metadata[filename]:
        queue_name = f'file_response_{worker}'
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=lambda ch, method, properties, body: on_response(ch, method, properties, body, filename, metadata, channel)
        )

    try:
        for worker, chunks in metadata[filename].items():
            for chunk_id in chunks:
                request = json.dumps({'chunk_id': chunk_id, 'worker_id': worker})
                routing_key = f'file_request_{worker}'
                channel.basic_publish(exchange='', routing_key=routing_key, body=request)
                print(f"Requested {chunk_id} from {worker}")

        print("Waiting for file chunks...")

        while not stop_signal.is_set():  # Run the consuming loop until all chunks are received
            channel.connection.process_data_events(time_limit=1)  # Process events with a time limit

        print("Terminating consumption.")
        channel.stop_consuming()

    except KeyboardInterrupt:
        print("Terminating master...")
        stop_signal.set()
        channel.stop_consuming()

    connection.close()

def main():
    metadata = load_metadata()
    
    # Retrieving first file
    file_to_retrieve = 'try2.txt'  
    p1 = threading.Thread(target=request_file_chunks, args=(file_to_retrieve, metadata))
    p1.start()
    p1.join()

    # Clear previous state
    received_chunks.clear()
    stop_signal.clear()
    
    # Retrieving second file
    file_to_retrieve = 'try3.txt'  
    p2 = threading.Thread(target=request_file_chunks, args=(file_to_retrieve, metadata))
    p2.start()
    p2.join()

if __name__ == "__main__":
    main()
