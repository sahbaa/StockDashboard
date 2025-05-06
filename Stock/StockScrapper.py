from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import undetected_chromedriver as uc

def scrapping (serchQuery):
    # options = uc.ChromeOptions()
    # # options.headless = True  # ← همچنان headless ولی هوشمند
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')

    options = Options()
    # options.add_argument('--head-less')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')#Avoid detection as automation

    # driver = uc.Chrome(options=options)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    df = pd.DataFrame(columns=['news', 'links'])  # ← تعریف اولیه df خارج از try

    try:
        driver.get(f'https://finance.yahoo.com/quote/{serchQuery}/news')
        time.sleep(3)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id = "scroll-down-btn"]')))
        driver.find_element(By.CSS_SELECTOR, 'button[id = "scroll-down-btn"]').click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[name = "reject"]')))
        driver.find_element(By.CSS_SELECTOR, 'button[name = "reject"]').click()
        
        last_height = driver.execute_script("return document.body.scrollHeight")

        all_ads = []
        all_links = []

        while True:
            
            ads_serach = driver.find_elements(By.CSS_SELECTOR, 'a.subtle-link.fin-size-small.thumb.yf-bwm9iy')
            ads = [ad.get_attribute('title') for ad in ads_serach]
            links = [ad.get_attribute('href') for ad in ads_serach]

            all_ads.extend(ads)
            all_links.extend(links)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if len(all_ads)>=4 : 
                break
            if last_height == new_height:
                break
            last_height = new_height

        df = pd.DataFrame(zip(all_ads, all_links), columns=['news', 'links'])  # ← مقداردهی اصلی
        print(df)
    except Exception as e:
        print(f"Error extracting ad: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
            del driver  # مهم برای جلوگیری از __del__ دوباره

    return df

