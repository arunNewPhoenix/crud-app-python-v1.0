def test_health_reports_dependencies(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_orders_initially_empty(client):
    response = client.get("/orders")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_list_order(client):
    payload = {"customer_name": "Asha", "item": "Keyboard", "quantity": 2, "unit_price": 1499.0}
    created = client.post("/orders", json=payload)
    assert created.status_code == 201
    assert created.json()["customer_name"] == "Asha"
    assert created.json()["status"] == "created"

    listed = client.get("/orders")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["item"] == "Keyboard"


def test_create_order_rejects_invalid_quantity(client):
    payload = {"customer_name": "Asha", "item": "Keyboard", "quantity": 0, "unit_price": 1499.0}
    response = client.post("/orders", json=payload)
    assert response.status_code == 422


def test_metrics_endpoint_exposes_prometheus_format(client):
    client.get("/orders")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
