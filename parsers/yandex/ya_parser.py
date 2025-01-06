import re
import bs4
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
from parsers.output_model import ProductOutput

def get_rating(rating_tag_object):
    if rating_tag_object:
        rating_and_feedback = rating_tag_object.find_all('span', limit=2)
        rate_str = re.sub(r'\sиз\s\d', '', rating_and_feedback[0].text.lower())
        rating_str = f"{rate_str.replace(':', '')}, {rating_and_feedback[1].text.replace('на основе ', '')}"
    else:
        rating_str = 'рейтинг отсутствует'
    return rating_str


def get_product(item_name):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'  # chrome
    options = uc.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    driver = uc.Chrome(options=options)
    driver.set_window_position(-2400, -2400)
    url = f'https://market.yandex.ru/search?text={item_name}'  # &how=aprice
    driver.get(url)
    driver.implicitly_wait(5)
    selector_wdwait = '#SerpStatic #ServerLayoutRenderer ._1H-VK ._1ENFO .ds-visuallyHidden'
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_wdwait)))
    selector_cart_button = '//button[@aria-label="В корзину" and @data-auto="cartButton" and @type="button"]'
    cart_button = driver.find_element(By.XPATH,
                                      selector_cart_button)
    driver.execute_script("return arguments[0].scrollIntoView(true);", cart_button)
    selector_div_product = '#SerpStatic #ServerLayoutRenderer article[data-auto="searchOrganic"] div._1H-VK'
    div_product = driver.find_element(By.CSS_SELECTOR, selector_div_product).get_attribute('outerHTML')
    soup = bs4.BeautifulSoup(div_product, 'lxml')
    description = soup.find('div', attrs={'class': '_1ENFO'})
    title = description.find('div', attrs={'data-baobab-name': 'title'}).text
    link = description.find('a').get('href')
    rating = description.find('div', attrs={'data-baobab-name': 'rating'})
    rating_res = get_rating(rating)
    link = f'https://market.yandex.ru/{link}'
    price = soup.find('span', attrs={'data-auto': 'snippet-price-current'}).text
    price = re.sub(r"\D", "", price)
    driver.quit()
    return ProductOutput(shop_name='Яндекс Маркет',
                         title=title,
                         price=price,
                         rating_info=rating_res,
                         link=link)


if __name__ == '__main__':
    print('Поиск товара...')
    print(get_product('ryzen9 7900x3d'))
    print('Поиск завершен.')
