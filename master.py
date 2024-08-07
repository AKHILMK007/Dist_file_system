#!/usr/bin/env python
import pika
import json
import split
# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = connection.channel()
# channel.queue_declare(queue='hello')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

routing_key = 'app.info'  # Example routing key
message=split.my_split("try.txt")
print(message)

# message = json.dumps({'string': 'Hello World!'})
for keys in message:
    print(message[keys])
    channel.basic_publish(exchange='topic_logs',
                      routing_key=routing_key,
                      body=json.dumps({keys:message[keys]}))
print(" [x] Sent 'Hello World!'")
connection.close()

#channel.basic_publish(exchange='topic_logs', routing_key=routing_key, body=message)