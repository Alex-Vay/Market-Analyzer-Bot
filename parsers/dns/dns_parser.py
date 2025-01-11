import re
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.common import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from parsers.output_model import ProductOutput
from parsers.title_handler import smart_function

def get_product_price(soup):
    try:
        product_price = soup.find('div', attrs={'class': 'product-buy'}).find('div', attrs={
            'class': 'product-buy__price-wrap'}).find('div', attrs={'class': 'product-buy__price'}).contents[0].strip()
        return product_price
    except:
        return None


def get_product_rating_and_feedback(soup):
    product_rating_feedback = soup.find('div', attrs={'class': 'catalog-product__stat'}).find('a', attrs={
        'class': 'catalog-product__rating'})
    product_rating_feedback_text = product_rating_feedback.text
    if 'нет' in product_rating_feedback_text or product_rating_feedback_text is None:
        product_rating, product_feedback = 'рейтинг отсутствует', 'отзывов нет'
    else:
        product_rating, product_feedback = product_rating_feedback_text.split('|')
    product_rating_feedback_str = f"рейтинг {product_rating.strip()}, {product_feedback}"
    return product_rating_feedback_str


def get_product_title_and_url(soup):
    product_title_and_url = soup.find('a', attrs={'class': 'catalog-product__name'})
    product_url = 'https://www.dns-shop.ru' + product_title_and_url.get('href')
    product_title = product_title_and_url.find('span').text[:75] + '...'
    return product_title, product_url


def extract_data(soup: BeautifulSoup):
    product_title, product_url = get_product_title_and_url(soup)
    product_price = get_product_price(soup)
    product_rating_feedback_str = get_product_rating_and_feedback(soup)
    price = re.sub(r"\D", "", product_price)
    return ProductOutput(shop_name='DNS',
                         title=product_title,
                         price=price,
                         rating_info=product_rating_feedback_str,
                         link=product_url)


def get_product(item_name=""):
    options = uc.ChromeOptions()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'  # chrome
    options.add_argument(f'user-agent={user_agent}')
    options.page_load_strategy = 'none'
    driver = uc.Chrome(options=options)
    driver.set_window_position(-2400, -2400)
    driver.get(f'https://www.dns-shop.ru/search/?q={item_name}')
    try:
        css_selector = ".products-list__content .catalog-product"
        time.sleep(32)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector + ' .product-buy')))
        driver.execute_script("window.stop();")
        element = driver.find_element(By.CSS_SELECTOR, css_selector)
        driver.execute_script("arguments[0].scrollIntoView();", element)

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
        products_div = driver.find_elements(By.CSS_SELECTOR, css_selector)[:10]
        titles_dict = {}
        for i, product_div in enumerate(products_div):
            product_title = product_div.find_element(By.CSS_SELECTOR, "a.catalog-product__name span").text
            product_title_short = re.search(r'^(.*?)\s*\[', product_title).group().replace('"', '')
            titles_dict[i] = product_title_short
        best_match_title_index = smart_function(item_name, titles_dict)
        if best_match_title_index is None:
            return None
        best_match_product = products_div[best_match_title_index]
        driver.execute_script("window.stop();")
        product_div_source = best_match_product.get_attribute('outerHTML')
        soup = BeautifulSoup(product_div_source, 'lxml')
        extracted_data = extract_data(soup)
        driver.quit()
        return extracted_data
    except TimeoutException:
        return None
    finally:
        driver.quit()


if __name__ == '__main__':
    product = get_product('ноутбук lenovo legion')
    print(product)
