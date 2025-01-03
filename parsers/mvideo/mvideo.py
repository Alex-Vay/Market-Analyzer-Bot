import re

import requests
from parsers.mvideo.config import headers, cookies
import os


def get_data_mvideo(ids):
    params = {
        'offset': '0',
        'doTranslit': 'true',
        'limit': '24',
        'query': f'{ids}',
        # 'sort' : 'price_asc',
    }
    session = requests.Session()
    try:
        resp = session.get('https://www.mvideo.ru/bff/products/v2/search', params=params, cookies=cookies,
                           headers=headers).json()
        page_products_ids = resp['body']['products']
        data = {
            'productIds': page_products_ids[:5],
        }
        resp = session.post('https://www.mvideo.ru/bff/product-details/list', cookies=cookies, headers=headers,
                            json=data)
        data = {
            'productIds': ','.join(page_products_ids[:5]),
        }
        prices = session.get('https://www.mvideo.ru/bff/products/prices', params=data, cookies=cookies,
                             headers=headers).json()
        material_prices = prices['body']['materialPrices']
        if resp.status_code == 200:
            products = resp.json()['body']['products']
            for i, product in enumerate(products):
                product_id = product["productId"]
                link = f'https://www.mvideo.ru/products/{product["nameTranslit"]}-{product_id}'
                truePriceObject = ''
                for price in material_prices:
                    if price['productId'] == product_id:
                        truePriceObject = price
                item_current_price = str(truePriceObject['price']['salePrice'])
                rating = product['rating']
                rating_count_sales_str = rating.get('count') if rating.get('count') is not None else 'нет'
                rating_star_str = round(rating.get('star'), 2) if rating.get('star') is not None else 'отсутствует'
                rating_and_feedback = f"Отзывов - {rating_count_sales_str}, рейтинг {rating_star_str}"
                return product['name'], re.sub("\D", "", item_current_price), rating_and_feedback, link

        else:
            print(f'[!] Skipped')
    except Exception as e:
        print(f'[!] Skipped, {e.__class__.__name__}')


if __name__ == '__main__':
    print(get_data_mvideo('Ноутбук Lenovo'))
