from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
import time
import re
from selenium import webdriver


def extract_product_title(soup: BeautifulSoup) -> str:
    h1_tag = soup.find('h1')
    if h1_tag:
        return h1_tag.text.strip() if len(h1_tag.text) < 50 else h1_tag.text[:50].strip() + '...'
    return 'Название не найдено'


def extract_product_price(soup: BeautifulSoup):
    price_block = soup.find('span', attrs={'class': 'price-block__price'})
    price = price_block.find('ins').text
    return price


def extract_product_id(soup: BeautifulSoup):
    params = soup.find('table', attrs={'class': 'product-params__table'})
    id = params.find('span', attrs={'id': 'productNmId'}).text
    return id


def extract_product_rating(soup: BeautifulSoup):
    rating_info = soup.find('div', attrs={'class': 'product-page__common-info'}).find_all('span')
    return f'Рейтинг {rating_info[0].text}: {rating_info[1].text}'


def collect_product_data(driver: uc.Chrome, product_url: str):
    '''парсинг странички товара'''
    # открытие новой вкладки в браузере
    driver.switch_to.new_window('tab')
    driver.get(product_url)
    # Ожидание загрузки страницы
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
    # html код страницы
    page_source = driver.page_source
    # нужен только тег div с классом "product-page__grid" где вся нужная информация
    product_info_tag_str = re.search(
        r'(<div\s+class="product-page__grid"[^>]*>.*</div>)<button class="btn.*К началу страницы</button>',
        page_source,
        re.DOTALL).group()
    soup = BeautifulSoup(product_info_tag_str, 'lxml')
    title = extract_product_title(soup)
    price = extract_product_price(soup)
    # product_id = extract_product_id(soup)
    rating = extract_product_rating(soup)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return title, price, rating, product_url


def get_product(item_name='lenovo legion', price=''):
    '''поиск товара сразу в url
    item_name: товар, который вводит пользователь в боте'''
    driver = uc.Chrome()
    driver.implicitly_wait(5)
    url = f'https://www.wildberries.ru/catalog/0/search.aspx?search={item_name}&sort=rate'
    driver.get(url)
    # Ожидание загрузки страницы
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'searchInput')))
    # ссылка на карточку товара
    link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'product-card__wrapper'))
    ).find_element(By.TAG_NAME, 'a').get_attribute('href')
    print(link)
    print('начинается сбор данных')
    product_data = collect_product_data(driver=driver, product_url=link)
    print(product_data)
    print('сбор данных окончен')
    driver.close()
    driver.quit()
    return product_data


if __name__ == '__main__':
    print('Поиск товара...')
    print(get_product())
    print('Поиск завершен.')
