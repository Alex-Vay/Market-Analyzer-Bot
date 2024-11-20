import aiohttp
import asyncio
from bs4 import BeautifulSoup
from test_config import cookies, headers
import time


async def fetch(session, url, params):
    async with session.get(url, params=params) as response:
        print(response.status)
        return await response.text()


async def parse(url, params):
    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
        html = await fetch(session, url, params)
        soup = BeautifulSoup(html, 'lxml')
        # извлечения данных из soup
        product_div_tag = soup.find('div', attrs={'data-id': 'product'})

        href = product_div_tag.find('a', recursive=False).get('href')
        link = 'https://www.dns-shop.ru' + href
        product_title = product_div_tag.find('a', recursive=False).find('span').text

        feedback = product_div_tag.find('div',
                                        attrs={'class': 'catalog-product__stat'},
                                        recursive=False).find('a', recursive=False)
        feedback_score = feedback.get('data-rating')
        feedback_count = feedback.text
        return link, product_title, feedback_score, feedback_count


async def main(urls):
    tasks = [parse(url_and_params[0], url_and_params[1]) for url_and_params in urls]
    results = await asyncio.gather(*tasks)
    return results


st = time.perf_counter()

urls = [
    ('https://www.dns-shop.ru/search/', {'q': 'realme 8'}),
    ('https://www.dns-shop.ru/search/', {'q': 'realme 9'})
]
results = asyncio.run(main(urls))
print(results)
fn = time.perf_counter()
print(fn - st)
