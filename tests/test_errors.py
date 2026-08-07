def test_404_error(client):
    """Test 404 error handling for a non-existent endpoint."""
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404


def test_get_product_404(client):
    """Test 404 when a product doesn't exist."""
    response = client.get("/products/99999")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_validation_error_empty_name(client):
    """Test validation error when product name is invalid."""
    product_data = {
        "name": "",
        "description": "A valid description here",
        "price": 99.99,
        "stock": 10
    }
    response = client.post("/products", json=product_data)
    assert response.status_code == 422


def test_validation_error_negative_price(client):
    """Test validation error when price is negative."""
    product_data = {
        "name": "Valid Name",
        "description": "A valid description here",
        "price": -10,
        "stock": 10
    }
    response = client.post("/products", json=product_data)
    assert response.status_code in [400, 422]