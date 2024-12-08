from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
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


# def extract_product_id(soup: BeautifulSoup):
#     params = soup.find('table', attrs={'class': 'product-params__table'})
#     id = params.find('span', attrs={'id': 'productNmId'}).text
#     return id


def extract_product_rating(soup: BeautifulSoup):
    rating_info = soup.find('div', attrs={'class': 'product-page__common-info'}).find_all('span')
    return f'Рейтинг {rating_info[0].text}: {rating_info[1].text}'


def collect_product_data(driver: webdriver.Chrome, product_url: str):
    '''парсинг странички товара'''
    # открытие новой вкладки в браузере
    driver.switch_to.new_window('tab')
    driver.get(product_url)
    # Ожидание загрузки страницы
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
    # нужен только тег div с классом "product-page__grid" где вся нужная информация
    product_info_tag_str = driver.find_element(By.CSS_SELECTOR,
                                               "#mainContainer #app .product-page__grid").get_attribute('outerHTML')
    soup = BeautifulSoup(product_info_tag_str, 'lxml')
    title = extract_product_title(soup)
    price = extract_product_price(soup)
    # product_id = extract_product_id(soup)
    rating = extract_product_rating(soup)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return title, price, rating, product_url


def get_product(item_name='laptop lenovo legion'):
    '''поиск товара сразу в url
    item_name: товар, который вводит пользователь в боте'''
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'  # chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    url = f'https://www.wildberries.ru/catalog/0/search.aspx?search={item_name}&sort=priceup'
    driver.get(url)
    # Ожидание загрузки страницы
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'searchInput')))
    # ссылка на карточку товара
    link = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'product-card__wrapper'))
    ).find_element(By.TAG_NAME, 'a').get_attribute('href')
    print('начинается сбор данных')
    product_data = collect_product_data(driver=driver, product_url=link)
    print('сбор данных окончен')
    driver.quit()
    return product_data


if __name__ == '__main__':
    print('Поиск товара...')
    print(get_product())
    print('Поиск завершен.')
