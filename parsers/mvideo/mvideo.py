import os
import requests
from config import headers, cookies


def get_data_mvideo(ids):
    if not os.path.exists('data'):
        os.mkdir('data')
    params = {
        'offset': '0',
        # 'filterParams': 'WyJ0b2xrby12LW5hbGljaGlpIiwiLTEyIiwiZGEiXQ==',
        'doTranslit': 'true',
        'limit': '24',
        'query': f'{ids}',
        # 'context': 'v2dzaG9wX2lkZFMwMDJhcXXQvdC+0YPRgtCx0YPQuiBsZW5vdm9sY2F0ZWdvcnlfaWRzn///',
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
                item_base_price = truePriceObject['price']['basePrice']
                item_current_price = truePriceObject['price']['salePrice']
                rating = product['rating']
                # item ={
                #     'name' : product['name'],
                #     'link' : link,
                #     'rating': rating,
                #     'item_basePrice': item_base_price,
                #     'item_currentPrice': item_current_price,
                # }
                # yield item

                return f"{product['name']}\n{link}\n{item_current_price}\n{rating['star']}-{rating['count']}"

        else:
            print(f'[!] Skipped')
    except Exception as e:
        print(f'[!] Skipped, {e.__class__.__name__}')


print(get_data_mvideo('Ноутбук Lenovo'))
