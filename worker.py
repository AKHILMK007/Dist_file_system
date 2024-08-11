#!/usr/bin/env python
import pika
import json
import sys
import os

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
    channel = connection.channel()

    # Declare an exchange of type 'topic'
    channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

    # Declare a queue for Worker 1
    result = channel.queue_declare(queue='worker1_queue', exclusive=True)
    queue_name = result.method.queue

    # Bind the queue to the exchange with the routing key 'worker1'
    channel.queue_bind(exchange='topic_logs', queue=queue_name, routing_key='worker1')

    def callback(ch, method, properties, body):
        try:
            with open('try1.json', 'r') as file:
                data = json.load(file)
                data.update(json.loads(body))
        except FileNotFoundError:
            data = {}
            data.update(json.loads(body))
        except json.JSONDecodeError:
            print("Error decoding JSON message")
            data = {}
            data.update(json.loads(body))
        with open('try1.json', 'w') as file:
            json.dump(data, file, indent=4)
        print(f" [x] Worker 1 received {body}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [*] Worker 1 waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
