import aiohttp
import asyncio
from config import cookies, headers, json_data
import time


async def fetch(session, url):
    async with session.post(url, json=json_data) as response:
        return await response.json()


async def parse(url):
    async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
        data = await fetch(session, url)
        # soup = BeautifulSoup(html, 'lxml')
        # извлечения данных из soup
        first_product = data['data']['productsFeed']['productsV2'][0]['product']
        url = first_product['productUrl']
        title = first_product['productTitle']
        price, currency = first_product['rawFinalPrice']['amount'], first_product['rawFinalPrice']['currency']
        rating = first_product.get('rating', '')
        sales = first_product.get('sales', '')
        return url, title, price, currency, rating, sales


async def main(urls):
    tasks = [parse(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results


st = time.perf_counter()
urls = [
    'https://aliexpress.ru/aer-webapi/v1/search',
]
results = asyncio.run(main(urls))
print(results)
fn = time.perf_counter()
print(fn - st)
