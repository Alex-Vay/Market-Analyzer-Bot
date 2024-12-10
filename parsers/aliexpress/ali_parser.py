import aiohttp
import asyncio
import config
from config import cookies, headers
import time

json_data = {
    'catId': '',
    'searchText': 'ноутбук lenovo legion',
    'storeIds': [],
    'pgChildren': [],
    'aeBrainIds': [],
    'searchInfo': '',
    'searchTrigger': '',
    'source': 'direct',
}


async def fetch(session, url):
    async with session.post(url, json=json_data) as response:
        return await response.json()


async def parse():
    async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
        url = 'https://aliexpress.ru/aer-webapi/v1/search'
        data = await fetch(session, url)
        first_product = data['data']['productsFeed']['productsV2'][0]['product']
        url = first_product['productUrl']
        title = first_product['productTitle']
        price, currency = first_product['rawFinalPrice']['amount'], first_product['rawFinalPrice']['currency']
        rating = first_product.get('rating', '')
        sales = first_product.get('sales', '')
        rating_and_sales = f'Рейтинг {rating}, {sales} продано'
        formatted_price = "{:,}".format(price).replace(",", " ")
        print_and_currency = price + currency
        return title, formatted_price, print_and_currency, rating_and_sales, url


async def get_product(item_name):
    json_data['searchText'] = item_name
    task = parse()
    results = await asyncio.gather(task)
    return results[0]


if __name__ == '__main__':
    st = time.perf_counter()
    urls = [
        'https://aliexpress.ru/aer-webapi/v1/search',
    ]
    results = asyncio.run(get_product('honor magicbook 15'))
    print(results)
    fn = time.perf_counter()
    print(fn - st)

