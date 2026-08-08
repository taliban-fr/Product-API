import pytest


@pytest.mark.benchmark
def test_create_product_performance(client, benchmark):
    """Benchmark product creation performance."""
    product_data = {
        "name": "Performance Test Product",
        "description": "This is a test product for performance testing",
        "price": 99.99,
        "stock": 10
    }

    def create_product():
        client.post("/products", json=product_data)

    result = benchmark(create_product)