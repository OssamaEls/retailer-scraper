import pandas as pd
import pytest

from retailer_scraper.analysis import get_min_prices


@pytest.fixture
def items_details():
    return [
        {
            'id': '1',
            'name': 'cheap_product_per_each',
            'category': 'category_1',
            'price': 10,
            'price_per_quantity': 0.5,
            'base_quantity': 'each',
            'image_link': 'www.example.com/1',
        },
        {
            'id': '2',
            'name': 'cheap_product_per_100g',
            'category': 'category_1',
            'price': 7,
            'price_per_quantity': 0.7,
            'base_quantity': '100g',
            'image_link': 'www.example.com/2',
        },
        {
            'id': '3',
            'name': 'cheap_product',
            'category': 'category_1',
            'price': 2,
            'price_per_quantity': 0.8,
            'base_quantity': 'each',
            'image_link': 'www.example.com/3',
        },
        {
            'id': '4',
            'name': 'expensive_product_per_100g',
            'category': 'category_1',
            'price': 6,
            'price_per_quantity': 0.9,
            'base_quantity': '100g',
            'image_link': 'www.example.com/4',
        },
        {
            'id': '5',
            'name': 'expensive_product_per_100mL',
            'category': 'category_2',
            'price': 3,
            'price_per_quantity': 0.4,
            'base_quantity': '100mL',
            'image_link': 'www.example.com/5',
        },
        {
            'id': '6',
            'name': 'cheap_product_per_100mL',
            'category': 'category_2',
            'price': 6,
            'price_per_quantity': 0.3,
            'base_quantity': '100mL',
            'image_link': 'www.example.com/6',
        },
    ]


@pytest.fixture
def actual_min_price():
    return {
            'name': 'cheap_product',
            'price': 2,
            'price_per_quantity': 0.8,
            'base_quantity': 'each',
            'url': 'https://www.tesco.com/groceries/en-GB/products/3'
        }


@pytest.fixture
def actual_min_prices_per_quantity():
    return [
        {
            'name': 'cheap_product_per_each',
            'price': 10,
            'price_per_quantity': 0.5,
            'base_quantity': 'each',
            'url': 'https://www.tesco.com/groceries/en-GB/products/1'
        },
        {
            'name': 'cheap_product_per_100g',
            'price': 7,
            'price_per_quantity': 0.7,
            'base_quantity': '100g',
            'url': 'https://www.tesco.com/groceries/en-GB/products/2'
        },
        {
            'name': 'cheap_product_per_100mL',
            'price': 6,
            'price_per_quantity': 0.3,
            'base_quantity': '100mL',
            'url': 'https://www.tesco.com/groceries/en-GB/products/6'
        },
    ]


def test_min_prices(items_details, actual_min_price, actual_min_prices_per_quantity):
    min_price, min_prices_per_quantity = get_min_prices(items_details)

    assert min_price == actual_min_price

    assert len(min_prices_per_quantity) == len(actual_min_prices_per_quantity)
    for item in min_prices_per_quantity:
        assert item in actual_min_prices_per_quantity
