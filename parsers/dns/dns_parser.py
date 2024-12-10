import re

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def get_product_price(soup):
    product_price = soup.find('div', attrs={'class': 'product-buy'}).find('div', attrs={
        'class': 'product-buy__price-wrap'}).find('div', attrs={'class': 'product-buy__price'}).text
    return product_price


def get_product_rating_and_feedback(soup):
    product_rating_feedback = soup.find('div', attrs={'class': 'catalog-product__stat'}).find('a', attrs={
        'class': 'catalog-product__rating'})
    product_rating = product_rating_feedback.get('data-rating')
    product_feedback = product_rating_feedback.text
    product_rating_feedback_str = f"Рейтинг: {product_rating}, отзывы: {product_feedback}"
    return product_rating_feedback_str


def get_product_title_and_url(soup):
    product_title_and_url = soup.find('a', attrs={'class': 'catalog-product__name'})
    product_url = 'https://www.dns-shop.ru' + product_title_and_url.get('href')
    product_title = product_title_and_url.find('span').text
    return product_title, product_url


def extract_data(soup: BeautifulSoup):
    product_title, product_url = get_product_title_and_url(soup)
    product_price = get_product_price(soup)
    product_rating_feedback_str = get_product_rating_and_feedback(soup)
    return product_title, re.sub("[^0-9]", "", product_price), product_rating_feedback_str, product_url


def get_product(item_name=""):
    options = uc.ChromeOptions()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'  # chrome

    options.add_argument(f'user-agent={user_agent}')
    driver = uc.Chrome(options=options)
    driver.get(f'https://www.dns-shop.ru/search/?q={item_name}')

    css_selector = "#search-results .products-list__content .catalog-product"
    # прокрутка до элемента, т.к. он может быть ниже
    # element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    driver.execute_script("window.scrollTo(0, 1500)")
    # подождем пока дозагрузится цена
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector + ' .product-buy .product-buy__price')))
    product_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    product_div_source = product_div.get_attribute('outerHTML')
    driver.quit()
    soup = BeautifulSoup(product_div_source, 'lxml')
    extracted_data = extract_data(soup)
    return extracted_data


if __name__ == '__main__':
    print(get_product('honor magicbook 15'))
