import requests
from parsers.mvideo.config import headers, cookies
from parsers.output_model import ProductOutput

def get_data_mvideo(query):
    params = {
        'offset': '0',
        'doTranslit': 'true',
        'limit': '24',
        'query': query,
    }
    session = requests.Session()
    try:
        resp = session.get('https://www.mvideo.ru/bff/products/v2/search', params=params, cookies=cookies, headers=headers).json()
        page_products_ids = resp['body']['products']
        data = {'productIds': page_products_ids[:5]}
        resp = session.post('https://www.mvideo.ru/bff/product-details/list', cookies=cookies, headers=headers, json=data)
        data = {'productIds': ','.join(page_products_ids[:5])}
        prices = session.get('https://www.mvideo.ru/bff/products/prices', params=data, cookies=cookies, headers=headers).json()
        material_prices = prices['body']['materialPrices']

        if resp.status_code == 200:
            products = resp.json()['body']['products']
            query_lower = query.lower()
            for i, product in enumerate(products):
                product_name_lower = product['name'].lower()
                if query_lower in product_name_lower:
                    product_id = product["productId"]
                    link = f'https://www.mvideo.ru/products/{product["nameTranslit"]}-{product_id}'
                    for price in material_prices:
                        if price['productId'] == product_id:
                            truePriceObject = price
                            break
                    item_current_price = str(truePriceObject.get('price', {}).get('salePrice', "Цена не указана"))
                    rating = product['rating']
                    rating_count_sales_str = rating.get('count') if rating.get('count') is not None else 'нет'
                    rating_star_str = round(rating.get('star'), 2) if rating.get('star') is not None else 'отсутствует'
                    rating_and_feedback = f"Отзывов - {rating_count_sales_str}, рейтинг {rating_star_str}"
                    return ProductOutput(shop_name='М.Видео',
                                  title=product['name'],
                                  price=item_current_price,
                                  rating_info=rating_and_feedback,
                                  link=link)
        else:
            print(f'[!] Skipped')
            return None

    except Exception as e:
        print(f'[!] Skipped, {e.__class.name}')
        return None


if __name__ == '__main__':
    product = get_data_mvideo('legion 7 pro')
    print(product.price, product.link)