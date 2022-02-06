from typing import List, Dict, Tuple

import pandas as pd


def get_min_prices(items_details: List[Dict]) -> Tuple[List, List]:
    """
    Get min prices (per unit and per quantity)
    Parameters
    ----------
    items_details
    Returns
    -------
        Tuple of items with min prices. The first result is the minimum price per unit.
        Rest of the results are minimum prices per quantity.
    Example
    -------
        If in the input there are prices per 100g, prices per 100mL, and prices per each, the output tuple will contain
        4 elements:
            - min price per unit
            - min price / 100g
            - min price / 100mL
            - min price / each
    """
    df = pd.DataFrame(items_details)
    base_url = 'https://www.tesco.com/groceries/en-GB/products/'
    df['url'] = base_url + df['id']
    columns = ['name', 'price', 'price_per_quantity', 'base_quantity', 'url']
    min_price = df.loc[df['price'] == df['price'].min(), columns].iloc[[0]]
    min_prices_per_quantity = df.loc[df.groupby('base_quantity')['price_per_quantity'].idxmin(), columns]

    return min_price.to_dict('records')[0], min_prices_per_quantity.to_dict('records')


def print_in_cyan(string: str):
    cyan = "\033[36m"
    print(cyan + string)


def print_results(items_details: List[Dict]):
    min_price, min_prices_per_quantity = get_min_prices(items_details)

    print_in_cyan(
        f"\n************************\n"
        "Min price found for:"
    )
    print_item_details(min_price)

    print_in_cyan("\nMin price per quantity found for:\n")
    for item in min_prices_per_quantity:
        print_in_cyan(f"Base quantity: {item['base_quantity']}")
        print_item_details(item)


def print_item_details(item: Dict):
    print_in_cyan(f"\t- {item['name']}\n"
                  f"\t  Price: £{item['price']}\n"
                  f"\t  Price per quantity: £{item['price_per_quantity']}/{item['base_quantity']}\n"
                  f"\t  Link: {item['url']}\n"
                  )
