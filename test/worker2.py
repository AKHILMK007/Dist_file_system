import pika
import json
import os

def load_worker_data(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return {}

def on_request(ch, method, properties, body, worker_data, worker_id):
    request = json.loads(body)
    chunk_id = request['chunk_id']
    requested_worker_id = request['worker_id']

    if requested_worker_id == worker_id:
        if chunk_id in worker_data:
            response = json.dumps({chunk_id: worker_data[chunk_id]})
            ch.basic_publish(exchange='', routing_key=f'file_response_{worker_id}', body=response)
            print(f"Sent {chunk_id} to master")
        else:
            print(f"Chunk {chunk_id} not found in worker data.")
    else:
        print(f"Request for {chunk_id} ignored by {worker_id}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    worker_id = 'worker2'  # Replace 'worker1' with 'worker2' or 'worker3' for other workers
    worker_data = load_worker_data('try2.json')  # Replace 'try1.json' with the correct file for each worker

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
    channel = connection.channel()

    channel.queue_declare(queue=f'file_request_{worker_id}')
    channel.queue_declare(queue=f'file_response_{worker_id}')

    on_request_callback = lambda ch, method, properties, body: on_request(ch, method, properties, body, worker_data, worker_id)
    channel.basic_consume(queue=f'file_request_{worker_id}', on_message_callback=on_request_callback)

    print(f"{worker_id} is waiting for file requests...")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"Terminating {worker_id}...")
        channel.stop_consuming()
        connection.close()

if __name__ == "__main__":
    main()
