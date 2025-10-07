# module_6/web/publisher.py
import os
import pika

def get_conn_params():
    return pika.ConnectionParameters(
        host=os.environ.get("RABBITMQ_HOST", "localhost"),
        port=int(os.environ.get("RABBITMQ_PORT", "5672")),
        credentials=pika.PlainCredentials(
            os.environ.get("RABBITMQ_USER", "guest"),
            os.environ.get("RABBITMQ_PASSWORD", "guest"),
        ),
        heartbeat=30
    )

def publish_message(payload: bytes):
    exchange = os.environ.get("RABBITMQ_EXCHANGE", "gradcafe_events")
    queue = os.environ.get("RABBITMQ_QUEUE", "gradcafe_jobs")
    routing_key = os.environ.get("RABBITMQ_ROUTING_KEY", "etl.job")

    connection = pika.BlockingConnection(get_conn_params())
    channel = connection.channel()

    # Durable exchange & queue
    channel.exchange_declare(exchange=exchange, exchange_type="direct", durable=True)
    channel.queue_declare(queue=queue, durable=True)
    channel.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)

    # delivery_mode=2 makes the message persistent
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=payload,
        properties=pika.BasicProperties(delivery_mode=2),
        mandatory=True
    )
    connection.close()
