import re
import requests
from parsers.mvideo.config import headers, cookies
from parsers.title_handler import smart_function
from parsers.output_model import ProductOutput


def parse(best_match_product: dict, material_prices):
    product_id = best_match_product["productId"]
    link = f'https://www.mvideo.ru/products/{best_match_product["nameTranslit"]}-{product_id}'
    true_price_object = ''
    for price in material_prices:
        if price['productId'] == product_id:
            true_price_object = price
    item_current_price = str(true_price_object['price']['salePrice'])
    price = re.sub(r"\D", "", item_current_price)
    rating = best_match_product['rating']
    rating_count_sales_str = rating.get('count') if rating.get('count') is not None else 'нет'
    rating_star_str = round(rating.get('star'), 2) if rating.get('star') is not None else 'отсутствует'
    rating_and_feedback = f"рейтинг {rating_star_str}, отзывов {rating_count_sales_str}, "
    return ProductOutput(shop_name='М.Видео',
                         title=best_match_product['name'],
                         price=price,
                         rating_info=rating_and_feedback,
                         link=link)


def get_data_mvideo(ids):
    params = {
        'offset': '0',
        'doTranslit': 'true',
        'limit': '24',
        'query': ids,
    }
    session = requests.Session()
    try:
        resp = session.get('https://www.mvideo.ru/bff/products/v2/search', params=params, cookies=cookies,
                           headers=headers).json()
        page_products_ids = resp['body']['products']
        data = {
            'productIds': page_products_ids[:24],
        }
        resp = session.post('https://www.mvideo.ru/bff/product-details/list', cookies=cookies, headers=headers,
                            json=data)
        data = {
            'productIds': ','.join(page_products_ids[:24]),
        }
        prices = session.get('https://www.mvideo.ru/bff/products/prices', params=data, cookies=cookies,
                             headers=headers).json()
        material_prices = prices['body']['materialPrices']
        if resp.status_code == 200:
            products = resp.json()['body']['products']
            titles_dict = {i: products[i]['name'] for i in range(len(products))}
            best_match_title_index = smart_function(ids, titles_dict)
            if best_match_title_index is None:
                return None
            best_match_product = products[best_match_title_index]
            product_output_object = parse(best_match_product, material_prices)
            return product_output_object

        else:
            print(f'[!] Skipped')
            return None
    except Exception as e:
        print(f'[!] Skipped, {e.__class.name}')
        return None


if __name__ == '__main__':
    product = get_data_mvideo('ноутбук lenovo legion')
    print(product.price, product.link)