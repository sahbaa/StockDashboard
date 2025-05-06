from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd


def scrape(search_query, output_file):
    options = Options()
    options.add_argument('--head-less')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')#Avoid detection as automation

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
   
    try:
        # در اینجا آدرس سایت هدف رو میزاریم
        driver.get("https://digikala.com")
        time.sleep(5)
        print("✅ Step 1: Page loaded")
        # این کد کارش اینه که بیاد و جایی که سرچ در سایت ها اتفاق میوفته رو پیدا کنه و اون متن ما رو داخلش وارد کنه
        # اگر در این مرحله به مشکل خوردید این تیکه کد و سایتی که قرار اسکرپش کنید رو به chatgpt بدید و بهش بگید که براتون درستش کنه
        driver.find_element(By.CSS_SELECTOR,"div[data-cro-id='searchbox-click']").click()
        search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='search-input']"))
        )
        
        time.sleep(3)
        #<input class="px-2 TextField_TextField__input__hFMFl text-subtitle w-full TextField_TextField__bwN9_ TextField_TextField--primary__IZ6Ku text-neutral-500 text-body-2 lg:text-body-2 text-button-1 h-full text-neutral-500"
        #  type="text" name="search-input" autocomplete="off" value="">
        print("✅ Step 2: search box found ")
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)
        last_height = driver.execute_script("return document.body.scrollHeight")
        ads = []

        while True:
            time.sleep(5)
            # در اینچا اون باکسی که اطلاعات گوشی داخلش هست رو پیدا میکنیم و اینجا میزاریمش
            ad_elements = driver.find_elements(By.CSS_SELECTOR, 'div.product-list_ProductList__item__LiiNI')
            for ad in ad_elements:
                try:
                    txt = ad.text
                    title = txt.split('\n')[0]
                    price = txt.split('\n')[-1]
                    ads.append({'title':title , 'price':price})
                except Exception as e:
                    print(f"Error extracting ad: {e}")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break

            last_height = new_height
        if ads:
            df = pd.DataFrame(ads)
            df.to_csv(output_file, index=False)
            print(f"Data successfully saved to {output_file}")
        else:
            print("No data found to save.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()


search_query = "گوشی"
#در اینجا ادرس فایل اکسلی که میخواید اطاعات رو در آن ذخیره کنید قرار بدید
output_file = "digi.csv"
scrape(search_query, output_file)