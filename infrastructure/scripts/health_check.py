#!/usr/bin/env python3
"""
Infrastructure Health Check Script
Verifies all services are running correctly
"""

import sys
import time
from typing import Dict, Tuple

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def check_postgres() -> Tuple[bool, str]:
    """Check PostgreSQL connection"""
    try:
        import psycopg2

        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="multi_agent_db",
            connect_timeout=5,
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
        return True, f"Connected (PostgreSQL {version.split(',')[0]})"
    except Exception as e:
        return False, str(e)


def check_redis() -> Tuple[bool, str]:
    """Check Redis connection"""
    try:
        import redis

        client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        client.ping()
        info = client.info("server")
        client.close()
        return True, f"Connected (Redis {info['redis_version']})"
    except Exception as e:
        return False, str(e)


def check_rabbitmq() -> Tuple[bool, str]:
    """Check RabbitMQ connection"""
    try:
        import pika

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="localhost",
                port=5672,
                credentials=pika.PlainCredentials("guest", "guest"),
            )
        )
        connection.close()
        return True, "Connected (RabbitMQ Ready)"
    except Exception as e:
        return False, str(e)


def check_minio() -> Tuple[bool, str]:
    """Check MinIO connection"""
    try:
        from minio import Minio

        client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False,
        )
        buckets = client.list_buckets()
        return True, f"Connected ({len(buckets)} buckets)"
    except Exception as e:
        return False, str(e)


def check_fastapi() -> Tuple[bool, str]:
    """Check FastAPI health endpoint"""
    try:
        import httpx

        response = httpx.get("http://localhost:8000/api/v1/health/live", timeout=5)
        if response.status_code == 200:
            return True, "Connected (FastAPI Running)"
        return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, str(e)


def check_prometheus() -> Tuple[bool, str]:
    """Check Prometheus"""
    try:
        import httpx

        response = httpx.get("http://localhost:9090/-/healthy", timeout=5)
        if response.status_code == 200:
            return True, "Connected (Prometheus Healthy)"
        return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, str(e)


def check_grafana() -> Tuple[bool, str]:
    """Check Grafana"""
    try:
        import httpx

        response = httpx.get("http://localhost:3000/api/health", timeout=5)
        if response.status_code == 200:
            return True, "Connected (Grafana Healthy)"
        return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, str(e)


def main():
    """Run all health checks"""
    print(f"\n{'='*60}")
    print("  Multi-Agent Data Analysis Assistant - Health Check")
    print(f"{'='*60}\n")

    checks: Dict[str, Tuple[bool, str]] = {
        "PostgreSQL": check_postgres(),
        "Redis": check_redis(),
        "RabbitMQ": check_rabbitmq(),
        "MinIO": check_minio(),
        "FastAPI": check_fastapi(),
        "Prometheus": check_prometheus(),
        "Grafana": check_grafana(),
    }

    all_passed = True

    for service, (status, message) in checks.items():
        if status:
            print(f"  {GREEN}✓{RESET} {service:<15} {message}")
        else:
            print(f"  {RED}✗{RESET} {service:<15} {YELLOW}{message}{RESET}")
            all_passed = False

    print(f"\n{'='*60}")

    if all_passed:
        print(f"  {GREEN}All services are healthy!{RESET}")
        print(f"{'='*60}\n")
        return 0
    else:
        print(f"  {RED}Some services are unhealthy!{RESET}")
        print(f"{'='*60}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())