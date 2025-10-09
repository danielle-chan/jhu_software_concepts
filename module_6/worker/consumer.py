import os
import json
import time
from typing import Any, Dict, Iterable, Tuple, Optional

import pika
import psycopg

EXCHANGE = "tasks"
QUEUE = "tasks_q"
ROUTING_KEY = "tasks"

# Environment helpers
def _amqp_url() -> str:
    # e.g. amqp://guest:guest@rabbitmq:5672/%2F
    return os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2F")

def _db_dsn() -> str:
    # Prefer DATABASE_URL; otherwise build from POSTGRES_* envs
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    db = os.getenv("POSTGRES_DB", "applicants")
    user = os.getenv("POSTGRES_USER", "postgres")
    pwd = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

# DB helpers
def _open_db():
    # psycopg 3 connection (autocommit False by default); we manage tx manually
    return psycopg.connect(_db_dsn())

def _ensure_watermark_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ingestion_watermarks (
            source TEXT PRIMARY KEY,
            last_seen TEXT,
            updated_at TIMESTAMPTZ DEFAULT now()
        );
    """)

def _get_last_seen(cur, source: str) -> Optional[str]:
    cur.execute("SELECT last_seen FROM ingestion_watermarks WHERE source = %s", (source,))
    row = cur.fetchone()
    return row[0] if row and row[0] is not None else None

def _set_last_seen(cur, source: str, last_seen: Optional[str]) -> None:
    cur.execute(
        """
        INSERT INTO ingestion_watermarks (source, last_seen)
        VALUES (%s, %s)
        ON CONFLICT (source)
        DO UPDATE SET last_seen = EXCLUDED.last_seen, updated_at = now()
        """,
        (source, last_seen),
    )

def _insert_applicants_batch(cur, rows: Iterable[Dict[str, Any]]) -> int:
    """
    Insert normalized rows into applicants with idempotence on (url).
    rows: iterable of dicts with keys matching your applicants schema fields.
    Returns number of attempted inserts (not counting duplicates).
    """
    inserted = 0
    for e in rows:
        cur.execute(
            """
            INSERT INTO applicants (
                program, degree, comments, date_added, status, url,
                gpa, gre, gre_v, gre_aw, term, us_or_international,
                llm_generated_program, llm_generated_university, university
            ) VALUES (
                %(program)s, %(degree)s, %(comments)s, %(date_added)s, %(status)s, %(url)s,
                %(gpa)s, %(gre)s, %(gre_v)s, %(gre_aw)s, %(term)s, %(us_or_international)s,
                %(llm_generated_program)s, %(llm_generated_university)s, %(university)s
            )
            ON CONFLICT (url) DO NOTHING
            """,
            e,
        )
        inserted += 1
    return inserted

# Task helpers
def handle_scrape_new_data(conn, payload: Dict[str, Any]) -> None:
    """
    Runs incremental scrape:
      1) read watermark (or use payload['since'] if provided)
      2) run scraper since watermark → (rows, max_seen)
      3) insert rows idempotently
      4) advance watermark to max_seen AFTER successful insert
    """
    source = payload.get("source", "gradcafe")
    with conn.cursor() as cur:
        _ensure_watermark_table(cur)
        since = payload.get("since") or _get_last_seen(cur, source)

        # Import your incremental scraper. It must accept since (str|None)
        # and return (rows, max_seen) where:
        #   rows: iterable[dict] normalized to applicants schema
        #   max_seen: str|None sortable watermark (e.g., latest date_added or max url id)
        from etl.incremental_scraper import run_scraper  # type: ignore

        rows, max_seen = run_scraper(since=since)

        # rows must already be normalized to your applicants schema keys
        _insert_applicants_batch(cur, rows)

        # advance watermark (only after successful inserts)
        if max_seen is not None:
            _set_last_seen(cur, source, max_seen)

def handle_recompute_analytics(conn, payload: Dict[str, Any]) -> None:
    """
    Recompute summaries used by the UI.
    This refreshes the single-row materialized view 'applicant_summary'.
    """
    with conn.cursor() as cur:
        # If you created a UNIQUE index on applicant_summary(id), you may use CONCURRENTLY.
        # cur.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY applicant_summary;")
        cur.execute("REFRESH MATERIALIZED VIEW applicant_summary;")


# Consumer
def _open_channel():
    params = pika.URLParameters(_amqp_url())
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=ROUTING_KEY)
    ch.basic_qos(prefetch_count=1)  # backpressure: 1 message at a time
    print("worker connected & waiting for tasks...", flush=True)
    return conn, ch

def _task_map():
    return {
        "scrape_new_data": handle_scrape_new_data,
        "recompute_analytics": handle_recompute_analytics,
    }

def _on_message(ch, method, props, body):
    try:
        msg = json.loads(body.decode("utf-8")) if body else {}
        kind = msg.get("kind")
        payload = msg.get("payload") or {}
        print(f"received: {kind} payload={payload}", flush=True)

        handler = _task_map().get(kind)
        if handler is None:
            print(f"unknown kind: {kind}; dropping", flush=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        # Per-message DB transaction
        with _open_db() as conn:
            try:
                handler(conn, payload)
                conn.commit()   # commit on success
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                conn.rollback()
                print(f"handler error: {e}", flush=True)
                # No infinite retry loops:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    except Exception as e:
        print(f"fatal decode/dispatch error: {e}", flush=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    conn, ch = _open_channel()
    ch.basic_consume(queue=QUEUE, on_message_callback=_on_message, auto_ack=False)
    try:
        ch.start_consuming()
    finally:
        try:
            conn.close()
        except Exception:
            pass
        # brief backoff if docker keeps restarting us
        time.sleep(0.5)

if __name__ == "__main__":
    main()
