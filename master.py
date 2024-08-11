#!/usr/bin/env python
import pika
import json
import split
import random

# Establish connection to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
channel = connection.channel()

# Declare an exchange of type 'topic'
channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

# Define worker routing keys
worker_routing_keys = ['worker1', 'worker2']

# Read and split the message
message = split.my_split("try2.txt")
print(message)

# Publish each chunk to a randomly chosen worker
for keys in message:
    selected_worker = random.choice(worker_routing_keys)  # Randomly select a worker
    print(f"Publishing to {selected_worker}: {message[keys]}")
    channel.basic_publish(
        exchange='topic_logs',
        routing_key=selected_worker,
        body=json.dumps({keys: message[keys]})
    )

print(" [x] Messages sent")
connection.close()
