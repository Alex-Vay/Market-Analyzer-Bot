import difflib
import re

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import undetected_chromedriver as uc


def get_product(item_name='телефон realme 10 черный'):
    '''поиск товара на главной страничке
    item_name: товар, который вводит пользователь в боте'''

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'  # chrome
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    url = f'https://www.ozon.ru/search/?text={item_name}&from_global=true' #&sorting=price
    driver.get(url)
    # pass captcha
    button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'reload-button')))
    button.click()
    driver.implicitly_wait(3)
    # Ожидание загрузки страницы
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#paginatorContent .tile-root .tile-hover-target')))
    # получаем карточки
    products = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH,
                                                                                    "//div[@id='paginatorContent']//div[@data-index < 1]")))
    #  значение атрибута data-index (порядковый номер карточки) как id
    titles_and_urls = {
        int(product.get_attribute('data-index')): product.find_element(
            By.CSS_SELECTOR, '.tile-hover-target .tsBody500Medium').text for product in products}

    best_match_index = None
    best_ratio = 0

    for index, product_title in titles_and_urls.items():
        try:

            sm = difflib.SequenceMatcher(None, item_name.lower(), product_title.lower())
            similarity_ratio = sm.ratio()

            if similarity_ratio > best_ratio:  # Нашли лучшее совпадение?
                best_ratio = similarity_ratio
                best_match_index = index
        except Exception as e:
            print(f"Ошибка при обработке товара: {e}")
            continue
    product_card = products[best_match_index]
    soup = BeautifulSoup(product_card.get_attribute('outerHTML'), 'lxml')
    product_url = "https://www.ozon.ru" + soup.find('a', attrs={'class': 'tile-hover-target'}).get('href')
    product_title = titles_and_urls[best_match_index]
    product_price = soup.find('span', attrs={'class': 'tsHeadline500Medium'}).text
    try:
        rating_feedback = soup.find('div', attrs={'class': 'tsBodyMBold'}).find_all('span', attrs={'q1'})
        product_rating_feedback = f"Рейтинг: {rating_feedback[0].text}, {rating_feedback[1].text}"
    except:
        product_rating_feedback = f"Рейтинг: отсутствует"
    driver.quit()
    return product_title, re.sub("[^0-9]", "", product_price), product_rating_feedback, product_url


if __name__ == '__main__':
    print('Поиск товара...')
    print(get_product("ноутбук Lenovo"))
    print('Поиск завершен.')
