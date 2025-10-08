import os, json, pika

EXCHANGE = os.getenv("ETL_EXCHANGE", "etl")
QUEUE = os.getenv("ETL_QUEUE", "ingest")
ROUTING_KEY = os.getenv("ETL_ROUTING_KEY", "ingest")

def publish(payload: dict) -> None:
    creds = pika.PlainCredentials(os.getenv("RABBIT_USER","guest"), os.getenv("RABBIT_PASS","guest"))
    params = pika.ConnectionParameters(
        host=os.getenv("RABBIT_HOST","rabbitmq"),
        port=int(os.getenv("RABBIT_PORT","5672")),
        credentials=creds,
    )
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.queue_bind(queue=QUEUE, exchange=EXCHANGE, routing_key=ROUTING_KEY)
    ch.basic_publish(
        exchange=EXCHANGE,
        routing_key=ROUTING_KEY,
        body=json.dumps(payload).encode("utf-8"),
        properties=pika.BasicProperties(delivery_mode=2),  # persistent
    )
    conn.close()
