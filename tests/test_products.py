def test_create_category(client):
    response = client.post("/categories", json={"name": "Electronics"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Electronics"


def test_create_duplicate_category(client):
    client.post("/categories", json={"name": "Electronics"})
    response = client.post("/categories", json={"name": "Electronics"})
    assert response.status_code == 400


def test_list_categories(client):
    client.post("/categories", json={"name": "Electronics"})
    response = client.get("/categories")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_product(client):
    product_data = {
        "name": "Wireless Mouse",
        "description": "A basic wireless mouse",
        "price": 19.99,
        "stock": 50,
    }
    response = client.post("/products", json=product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]


def test_get_product(client):
    product_data = {
        "name": "Keyboard",
        "description": "Mechanical",
        "price": 49.99,
        "stock": 20,
    }
    create_response = client.post("/products", json=product_data)
    product_id = create_response.json()["id"]

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Keyboard"


def test_get_product_not_found(client):
    response = client.get("/products/99999")
    assert response.status_code == 404


def test_update_product(client):
    product_data = {
        "name": "Monitor",
        "description": "24 inch full HD display",
        "price": 150.0,
        "stock": 5,
    }
    create_response = client.post("/products", json=product_data)
    product_id = create_response.json()["id"]

    response = client.patch(f"/products/{product_id}", json={"price": 129.99})
    assert response.status_code == 200
    assert response.json()["price"] == 129.99


def test_delete_product(client):
    product_data = {
        "name": "USB Cable",
        "description": "1 meter USB-C cable",
        "price": 5.99,
        "stock": 100,
    }
    create_response = client.post("/products", json=product_data)
    product_id = create_response.json()["id"]

    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 204

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 404
