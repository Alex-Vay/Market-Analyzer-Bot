import re
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def get_product_price(product_soup):
    price_all = product_soup.find('div', attrs={'class': re.compile('^red-snippet_RedSnippet__price')})
    new_price = price_all.find('div', attrs={'class': re.compile('^red-snippet_RedSnippet__priceNew')}).text
    return new_price


def get_product_rating(product_soup):
    title_and_rating = product_soup.find('div', attrs={'class': re.compile('^red-snippet_RedSnippet__trustAndTitle')})
    rating_and_feedback_span = title_and_rating.find('div', attrs={
        'class': re.compile('^red-snippet_RedSnippet__trust')}).find_all('span')
    return f"Рейтинг: {rating_and_feedback_span[0].text}, {rating_and_feedback_span[1].text}"


def get_product(item_name=""):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'  # chrome
    options = uc.ChromeOptions()
    # options.add_argument("--headless")
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f'user-agent={user_agent}')
    # чтобы не ждать полностью загрузку страницы
    # caps = DesiredCapabilities().CHROME
    # caps["pageLoadStrategy"] = "none"  # interactive
    driver = uc.Chrome(options=options,
                       # desired_capabilities=caps
                       )

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

    css_selector = "#__aer_root__ div[class^='SnowSearchWrap_SnowSearchWrap__content'] div[class^='red-snippet_RedSnippet__grid'] div[data-index='0']"
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    soup = BeautifulSoup(element.get_attribute('outerHTML'), 'lxml')
    product_info = soup.find('div', attrs={'class': re.compile('^red-snippet_RedSnippet__contentWithAside')}).find('a')
    product_url = 'https://' + product_info.get('href')
    product_price = get_product_price(product_info)
    title_and_rating = product_info.find('div', attrs={'class': re.compile('^red-snippet_RedSnippet__trustAndTitle')})
    rating_and_feedback = get_product_rating(product_info)
    product_title = title_and_rating.find('div', attrs={'class': re.compile('^red-snippet_RedSnippet__title')}).text
    driver.quit()
    return product_title, product_price, rating_and_feedback, product_url


if __name__ == '__main__':
    print(get_product('honor magicbook 16'))
