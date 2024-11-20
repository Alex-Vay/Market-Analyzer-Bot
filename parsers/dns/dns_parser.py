import re

from config import headers, cookies
from bs4 import BeautifulSoup
import requests


def get_product(product='', price=''):
    # url = 'https://www.dns-shop.ru/search/'
    params = {'q': 'realme 8',
    }

    url = 'https://www.dns-shop.ru/search/'
    response = requests.get(url=url, params=params, cookies=cookies, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

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


print(get_product())
