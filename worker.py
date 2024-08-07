# #!/usr/bin/env python
# import pika, sys, os
# import json
# def main():
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
#     channel = connection.channel()

#     channel.queue_declare(queue='hello')

#     def callback(ch, method, properties, body):
#         try:
#             with open('try1.json', 'r') as file:
#                 data = json.load(file)
#                 data.update(json.loads(body))
#         except:
#             data={}
#             data.update(json.loads(body))
#         with open('try1.json', 'w') as file:
#             json.dump(data, file, indent=4)
#         print(f" [x] Received {body}")

#     channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

#     print(' [*] Waiting for messages. To exit press CTRL+C')
#     channel.start_consuming()

# if __name__ == '__main__':
#     try:
#         main()
#     except KeyboardInterrupt:
#         print('Interrupted')
#         try:
#             sys.exit(0)
#         except SystemExit:
#             os._exit(0)




#!/usr/bin/env python
import pika, sys, os
import json
def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    #channel.queue_declare(queue='hello')
    channel.exchange_declare(exchange='topic_logs', exchange_type='topic')
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    # Bind the queue to the exchange with a specific routing key pattern
    binding_key = "*.info"  # Example pattern, you can customize this
    channel.queue_bind(exchange='topic_logs', queue=queue_name, routing_key=binding_key)

    def callback(ch, method, properties, body):
        try:
            with open('try1.json', 'r') as file:
                data = json.load(file)
                data.update(json.loads(body))
        except:
            data={}
            data.update(json.loads(body))
        with open('try1.json', 'w') as file:
            json.dump(data, file, indent=4)
        print(f" [x] Received {body}")

    # channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

    # print(' [*] Waiting for messages. To exit press CTRL+C')
    # channel.start_consuming()
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
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