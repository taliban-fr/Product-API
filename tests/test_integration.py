def test_full_crud_flow(client):
    """Integration test: register -> login -> create -> update -> delete."""

    # 1. Register a user
    register_response = client.post(
        "/register",
        json={
            "username": "integrationuser",
            "email": "integration@example.com",
            "password": "integrationpass123",
        },
    )
    assert register_response.status_code == 201

    # 2. Log in with that user
    login_response = client.post(
        "/login", data={"username": "integrationuser", "password": "integrationpass123"}
    )
    assert login_response.status_code == 200

    # 3. Create a product
    create_response = client.post(
        "/products",
        json={
            "name": "Integration Test Product",
            "description": "Created during the full-flow integration test",
            "price": 49.99,
            "stock": 15,
        },
    )
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]

    # 4. Update the product
    update_response = client.patch(f"/products/{product_id}", json={"price": 39.99})
    assert update_response.status_code == 200
    assert update_response.json()["price"] == 39.99

    # 5. Delete the product
    delete_response = client.delete(f"/products/{product_id}")
    assert delete_response.status_code == 204

    # Verify deletion
    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404
