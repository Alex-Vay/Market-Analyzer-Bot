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
    return h1_tag.text.strip() if h1_tag else 'Название не найдено'


def extract_product_price(soup: BeautifulSoup) -> str:
    price_element = soup.find('span', string='без Ozon Карты')
    if price_element:
        product_price_ozon_card = price_element.parent.parent.find('div').find_all('span')
        return product_price_ozon_card[0].text if product_price_ozon_card else 'Цена не найдена'
    else:
        product_price_div = soup.find('div', attrs={'data-widget': 'webPrice'})
        if product_price_div:
            return product_price_div.find('span').text if product_price_div.find('span') else 'Цена не найдена'
    return 'Цена не найдена'


def extract_product_id(soup: BeautifulSoup) -> str:
    product_id_element = soup.find('button', attrs={'data-widget': 'webDetailSKU'})
    return product_id_element.find('div').text if product_id_element else 'Артикул не найден'


def extract_product_rating(soup: BeautifulSoup):
    product_score = soup.find('div', attrs={'data-widget': 'webSingleProductScore'})
    if product_score:
        rating, feedback_count = product_score.find('div').text.split(' • ')
        return f'Рейтинг {rating}, {feedback_count}'
    return 'Рейтинг не найден'


def collect_product_data(driver: uc.Chrome, product_url: str):
    '''парсинг странички товара'''
    # открытие новой вкладки в браузере
    driver.switch_to.new_window('tab')
    driver.get(product_url)
    # Ожидание загрузки страницы
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
    # html код страницы
    page_source = driver.page_source
    # нужен только тег div с атрибутом data-widget="container" где вся нужная информация
    product_info_tag_str = re.search(r'(<div\s+data-widget="container"[^>]*>.*</div>)<div data-widget="webStickyProducts"[^>]*>',
                            page_source,
                            re.DOTALL).group()

    soup = BeautifulSoup(product_info_tag_str, 'lxml')
    # получение названия товара
    title_full = extract_product_title(soup)
    title_short = title_full[:50].strip(', ') + '...'
    # Получение цены товара
    price = extract_product_price(soup)
    # Получение артикул и рейтинга
    # product_id = extract_product_id(soup)
    rating_and_feedback = extract_product_rating(soup)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return title_short, price, rating_and_feedback, product_url


def get_product(item_name=''):
    '''поиск товара на главной страничке
    item_name: товар, который вводит пользователь в боте'''
    # options = uc.ChromeOptions()
    driver = uc.Chrome()
    driver.implicitly_wait(5)
    url = f'https://www.ozon.ru/search/?text={item_name}&from_global=true&sorting=rating'
    driver.get(url)
    # Ожидание загрузки страницы
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'form')))
    # ссылка на товар
    link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'tile-hover-target'))
    ).get_attribute('href')
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
