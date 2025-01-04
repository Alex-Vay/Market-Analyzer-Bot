import re
import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parsers.output_model import ProductOutput


def get_product_price(product_soup):
    price_all = product_soup.find('div', attrs={'class': re.compile('^red-snippet_RedSnippet__price')})
    new_price = price_all.find('div', attrs={'class': re.compile('^red-snippet_RedSnippet__priceNew')}).text
    return new_price


def get_product_rating(product_soup):
    title_and_rating = product_soup.find('div', attrs={'class': re.compile('^red-snippet_RedSnippet__trustAndTitle')})
    rating_and_feedback_span = title_and_rating.find('div', attrs={
        'class': re.compile('^red-snippet_RedSnippet__trust')}).find_all('span')
    if len(rating_and_feedback_span) > 1:
        return f"рейтинг {rating_and_feedback_span[0].text}, {rating_and_feedback_span[1].text}"
    return f"рейтинг отсутствует"


def get_product(item_name=""):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'  # chrome
    options = uc.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument(f'user-agent={user_agent}')
    options.page_load_strategy = 'none'
    driver = uc.Chrome(options=options,
                       # desired_capabilities=caps
                       )
    # driver.set_window_position(-2400, -2400)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
      '''
    })
    search_text = item_name.replace(' ', '+')
    url = f'https://aliexpress.ru/wholesale?SearchText={search_text}&g=y&page=1'  # &sorting=price
    driver.get(url)
    time.sleep(25)
    css_selector = "#__aer_root__ div[class^='SnowSearchWrap_SnowSearchWrap__content'] div[class^='red-snippet_RedSnippet__grid'] div[data-index='0']"
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    driver.execute_script("window.stop();")
    soup = BeautifulSoup(element.get_attribute('outerHTML'), 'lxml')
    product_info = soup.find('div', attrs={'class': re.compile('^red-snippet_RedSnippet__contentWithAside')}).find('a')
    product_url = 'https://' + product_info.get('href')
    product_price = get_product_price(product_info)
    title_and_rating = product_info.find('div', attrs={'class': re.compile('^red-snippet_RedSnippet__trustAndTitle')})
    rating_and_feedback = get_product_rating(product_info)
    product_title = title_and_rating.find('div', attrs={'class': re.compile('^red-snippet_RedSnippet__title')}).text
    price = re.sub(r"\D", "", product_price)
    driver.quit()
    return ProductOutput(shop_name='Алиэкспресс',
                         title=product_title,
                         price=price,
                         rating_info=rating_and_feedback,
                         link=product_url)


if __name__ == '__main__':
    print(get_product('realme 12'))
