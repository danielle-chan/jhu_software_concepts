import os, json, time, sys, subprocess, pika

EXCHANGE = "tasks"
QUEUE = "tasks_q"
ROUTING_KEY = "tasks"

def _open_channel():
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2F")
    params = pika.URLParameters(url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=ROUTING_KEY)
    ch.basic_qos(prefetch_count=1)
    print("worker connected & consuming...", flush=True)
    return conn, ch

def _load_data():
    # Run your DB loader (mounted at /app/db)
    subprocess.check_call([sys.executable, "/app/db/load_data.py"])

def _handle(ch_, method, props, body):
    try:
        msg = json.loads(body.decode("utf-8")) if body else {}
        kind = msg.get("kind")
        print(f"got: {msg}", flush=True)

        if kind in ("scrape_new_data", "recompute_analytics"):
            _load_data()   # stub: replace with incremental logic later
        else:
            print(f"unknown kind: {kind}", flush=True)

        ch_.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:  # keep message; retry later
        print(f"handler error: {e}", flush=True)
        ch_.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        time.sleep(1)

def main():
    conn, ch = _open_channel()
    ch.basic_consume(queue=QUEUE, on_message_callback=_handle, auto_ack=False)
    try:
        ch.start_consuming()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
