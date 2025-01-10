import re
import bs4
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from parsers.output_model import ProductOutput
from parsers.ozon.ozon_parser import smart_function


def get_rating(rating_tag_object):
    if rating_tag_object:
        rating_and_feedback = rating_tag_object.find_all('span', limit=2)
        rate_str = re.sub(r'\sиз\s\d', '', rating_and_feedback[0].text.lower())
        rating_str = f"{rate_str.replace(':', '')}, {rating_and_feedback[1].text.replace('на основе ', '')}"
    else:
        rating_str = 'рейтинг отсутствует'
    return rating_str


def parse(soup: bs4.BeautifulSoup) -> ProductOutput:
    description = soup.find('div', attrs={'class': '_1ENFO'})
    title = description.find('div', attrs={'data-baobab-name': 'title'}).text
    link = description.find('a').get('href')
    rating = description.find('div', attrs={'data-baobab-name': 'rating'})
    rating_res = get_rating(rating)
    link = f'https://market.yandex.ru/{link}'
    price = soup.find('span', attrs={'data-auto': 'snippet-price-current'}).text
    price = re.sub(r"\D", "", price)
    return ProductOutput(shop_name='Яндекс Маркет',
                         title=title,
                         price=price,
                         rating_info=rating_res,
                         link=link)


def get_product(item_name):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'  # chrome
    options = uc.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver = uc.Chrome(options=options)
    # driver.set_window_position(-2400, -2400)
    url = f'https://market.yandex.ru/search?text={item_name}'  # &how=aprice
    driver.get(url)
    driver.implicitly_wait(5)
    # прокрутка
    selector_cart_button = '//button[@aria-label="В корзину" and @data-auto="cartButton" and @type="button"]'
    cart_button = driver.find_element(By.XPATH, selector_cart_button)
    driver.execute_script("return arguments[0].scrollIntoView(true);", cart_button)

    selector_div_product = '#SerpStatic #ServerLayoutRenderer article[data-auto="searchOrganic"] div._1H-VK'
    products = driver.find_elements(By.CSS_SELECTOR, selector_div_product)[:10]
    selector_title = 'div._1ENFO div[data-baobab-name=title]'
    titles_dict = {i: products[i].find_element(By.CSS_SELECTOR, selector_title).text for i in range(len(products))}
    best_title_index = smart_function(item_name, titles_dict)
    best_product_div = products[best_title_index]

    soup = bs4.BeautifulSoup(best_product_div.get_attribute('outerHTML'), 'lxml')
    product_output_object = parse(soup)
    driver.quit()
    return product_output_object


if __name__ == '__main__':
    print('Поиск товара...')
    print(get_product('intel core i7-13700k'))
    print('Поиск завершен.')
