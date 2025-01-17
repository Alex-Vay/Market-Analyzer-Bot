import difflib
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
from parsers.output_model import ProductOutput
from parsers.title_handler import smart_function


def get_rating(rating_object):
    if rating_object:
        rating_feedback = rating_object.find_all('span', limit=2, recursive=False)
        feedback_count_str = re.sub(r'\W', ' ', rating_feedback[1].text)
        product_rating_str = f"рейтинг {rating_feedback[0].text.strip()}, {feedback_count_str}"
        return product_rating_str
    return "Рейтинг отсутствует"


def get_product(item_name: str):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'  # chrome
    options = uc.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver = uc.Chrome(options=options)
    url = f'https://www.ozon.ru/search/?text={item_name}&from_global=true'  # &sorting=price
    driver.set_window_position(-2400, -2400)
    driver.get(url)
    driver.implicitly_wait(3)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#paginatorContent .tile-root')))
    products = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH,
                                                                                    "//div[@id='paginatorContent']//div[@data-index < 24]")))

    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.container div[data-widget="searchResultsSort"] input')))
    driver.execute_script("return arguments[0].scrollIntoView(true);", element)
    titles_and_urls = {
        int(product.get_attribute('data-index')): product.find_element(
            By.CSS_SELECTOR, '.tile-clickable-element .tsBody500Medium').text.split('"')[0] for product in products}

    best_match_index = smart_function(item_name, titles_and_urls)
    if best_match_index is None:
        return None
    product_card = products[best_match_index]
    soup = BeautifulSoup(product_card.get_attribute('outerHTML'), 'lxml')
    product_url = "https://www.ozon.ru" + soup.find('a', attrs={'class': 'tile-clickable-element'}).get('href')
    product_title = titles_and_urls[best_match_index]
    product_price = soup.find('span', attrs={'class': 'tsHeadline500Medium'}).text
    rating_data = soup.find('div', attrs={'class': 'tsBodyMBold'})
    product_rating_feedback = get_rating(rating_data)
    price = re.sub(r"\D", "", product_price)
    driver.quit()
    return ProductOutput(shop_name='Ozon',
                         title=product_title,
                         price=price,
                         rating_info=product_rating_feedback,
                         link=product_url)


if __name__ == '__main__':
    print('Поиск товара...')
    print(get_product("ryzen7 процессор"))
    print('Поиск завершен.')
