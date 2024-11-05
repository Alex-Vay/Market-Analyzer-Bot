import bs4
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
import time
import re
from selenium import webdriver


def collect_product_data(driver: uc.Chrome, product_url=''):
    '''парсинг странички товара'''
    # открытие новой вкладки в браузере
    driver.switch_to.new_window('tab')
    time.sleep(3)
    # открытие ссылки товара в новой вкладке
    driver.get(product_url)
    time.sleep(3)
    # артикул товара

    page_source = driver.page_source
    soup = bs4.BeautifulSoup(page_source, 'lxml')
    time.sleep(2)
    # получение названия товара
    h1_tag = soup.find('h1').text
    title_full = re.search(r'\b.+\b', h1_tag).group()
    title_short = title_full[:50].strip(', ') + '...'
    # получение цены, цена может быть с озон картой или без
    price_element = soup.find('span', string='без Ozon Карты')
    time.sleep(2)
    if price_element:
        product_price_ozon_card = price_element.parent.parent.find('div').find_all('span')
        price = product_price_ozon_card[0].text
    else:
        product_price_div = soup.find('div', attrs={'data-widget': 'webPrice'}).find('span')
        price = product_price_div.text
    product_id = soup.find('button', attrs={'data-widget': 'webDetailSKU'}).find('div').text
    product_score = soup.find('div', attrs={'data-widget': 'webSingleProductScore'}).find('div').text
    rating, feedback_count = product_score.split(' • ')
    rating_and_feedback = f'Рейтинг {rating}, {feedback_count}'
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return f"{title_short}\n{product_id}\n{price}\n{rating_and_feedback}"


def get_product(item_name='ноутбук lenovo'):
    '''поиск товара на главной страничке
    item_name: товар, который вводит пользователь в боте'''
    driver = uc.Chrome()
    # driver.implicitly_wait(5)
    url = 'https://www.ozon.ru'
    driver.get(url)
    time.sleep(5)
    # находим строку поиска
    input_field = driver.find_element(By.NAME, 'text')
    input_field.clear()
    # вставляем товар для поиска
    input_field.send_keys(item_name)
    time.sleep(2)
    # нажатие enter
    input_field.send_keys(Keys.ENTER)
    time.sleep(2)
    # сортировка по рейтингу (можно убрать)
    current_url = driver.current_url
    driver.get(f'{current_url}&sorting=rating')
    time.sleep(2)
    # ссылка на товар
    link = driver.find_element(By.CLASS_NAME, 'tile-hover-target').get_attribute('href')
    print('начинается сбор данных')
    product_data = collect_product_data(driver=driver, product_url=link)
    print(product_data)
    print('сбор данных окончен')
    driver.close()
    driver.quit()


if __name__ == '__main__':
    print('Поиск товара...')
    print(get_product())
    print('Поиск завершен.')
