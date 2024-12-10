import re

import bs4
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver


def get_product(item_name='realme 10'):
    '''поиск товара на главной страничке
    item_name: товар, который вводит пользователь в боте'''
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'  # chrome
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    url = f'https://market.yandex.ru/search?text={item_name}' #&how=aprice
    driver.get(url)
    driver.implicitly_wait(5)
    # Ожидание загрузки страницы
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'aside')))
    # прогрутим браузер до первой кнопки 'В корзину', т.к. div тег с товаром не видно
    cart_button = driver.find_element(By.XPATH,
                                      '//button[@aria-label="В корзину" and @data-auto="cartButton" and @type="button"]')
    driver.execute_script("return arguments[0].scrollIntoView(true);", cart_button)
    # div тег где находится информация о товаре
    div_product = driver.find_element(By.CSS_SELECTOR,
                                      'div[data-auto-themename="listDetailed"] div._1H-VK').get_attribute('outerHTML')
    soup = bs4.BeautifulSoup(div_product, 'lxml')
    description = soup.find('div', attrs={'class': '_1ENFO'})
    title = description.find('div', attrs={'data-baobab-name': 'title'}).text
    link = description.find('a').get('href')
    rating = description.find('div', attrs={'data-baobab-name': 'rating'}).find_all('span', limit=2)
    rating = f"{rating[0].text}, {rating[1].text}"
    link = f'https://market.yandex.ru/{link}'
    price = soup.find('span', attrs={'data-auto': 'snippet-price-current'}).text

    driver.quit()
    return title, re.sub("[^0-9]", "", price), rating, link


if __name__ == '__main__':
    print('Поиск товара...')
    print(get_product())
    print('Поиск завершен.')
