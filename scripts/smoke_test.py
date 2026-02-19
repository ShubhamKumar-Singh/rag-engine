"""Smoke test: upload a short text and run a query against the running app.

This uses FastAPI TestClient so it can run against the app without network.
Usage:
    python -m scripts.smoke_test
"""
from fastapi.testclient import TestClient
import app.main as app_main


def run_smoke_test():
    client = TestClient(app_main.app)

    # Upload a short text
    text_payload = {
        "text": "Python is a programming language. It is widely used for scripting and data science.",
        "filename": "smoke_test.txt"
    }
    r = client.post("/upload/text", json=text_payload)
    print("/upload/text ->", r.status_code, r.json())

    # Query the system
    query_payload = {"question": "What is Python used for?"}
    r2 = client.post("/ask", json=query_payload)
    print("/ask ->", r2.status_code, r2.json())


if __name__ == "__main__":
    run_smoke_test()
