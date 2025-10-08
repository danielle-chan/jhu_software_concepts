import os, json, time, sys, subprocess
import pika

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
RABBIT_PORT = int(os.getenv("RABBIT_PORT", "5672"))
RABBIT_USER = os.getenv("RABBIT_USER", "guest")
RABBIT_PASS = os.getenv("RABBIT_PASS", "guest")
ETL_EXCHANGE = os.getenv("ETL_EXCHANGE", "etl")
ETL_QUEUE = os.getenv("ETL_QUEUE", "ingest")
ETL_ROUTING_KEY = os.getenv("ETL_ROUTING_KEY", "ingest")

def load_data():
    """
    Run your DB loader. This assumes docker-compose mounts ./db -> /app/db:ro.
    If load_data.py has a main guard, this will execute it.
    """
    # If your loader is a module with a callable, you could import and call it.
    # Using a subprocess keeps it simple and decoupled.
    subprocess.check_call([sys.executable, "/app/db/load_data.py"])

def main():
    creds = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    params = pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT, credentials=creds)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    ch.exchange_declare(exchange=ETL_EXCHANGE, exchange_type="direct", durable=True)
    ch.queue_declare(queue=ETL_QUEUE, durable=True)
    ch.queue_bind(queue=ETL_QUEUE, exchange=ETL_EXCHANGE, routing_key=ETL_ROUTING_KEY)
    ch.basic_qos(prefetch_count=1)

    def handle(ch_, method, props, body):
        try:
            # optional: inspect payload
            _ = json.loads(body.decode("utf-8")) if body else {}
            load_data()
            ch_.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            # nack + requeue
            ch_.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            time.sleep(1)

    ch.basic_consume(queue=ETL_QUEUE, on_message_callback=handle, auto_ack=False)
    ch.start_consuming()

if __name__ == "__main__":
    main()
