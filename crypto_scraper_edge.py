import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === CONFIGURATION ===
URL = "https://coinmarketcap.com/"
CSV_FILE = "crypto_prices.csv"
TOP_N = 10  # Top N coins to scrape
HEADLESS_MODE = True  
PRICE_FILTER = None  # Example: 20000 (only coins above this price)
CHANGE_FILTER = None  # Example: 5 (only coins with > 5% 24h change)

# === SETUP SELENIUM EDGE DRIVER ===
service = Service(r"C:\msedgedriver.exe")
options = Options()

if HEADLESS_MODE:
    options.add_argument("--headless=new")  # New headless mode (faster & stable)
    options.add_argument("--disable-gpu")

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Edge(service=service, options=options)

try:
    driver.get(URL)
    print("Loading CoinMarketCap...")
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.XPATH, '//table//tbody/tr'))
    )
    time.sleep(2)  
    rows = driver.find_elements(By.XPATH, '//table//tbody/tr')[:TOP_N]
    scraped_data = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for row in rows:
        try:
            name = row.find_element(By.XPATH, './/td[3]//p').text
            price = float(row.find_element(By.XPATH, './/td[4]//span').text.replace("$", "").replace(",", ""))
            change_24h = row.find_element(By.XPATH, './/td[5]//span').text
            change_24h_value = float(change_24h.replace("%", "").replace(",", ""))
            market_cap = row.find_element(By.XPATH, './/td[7]//span').text
            if PRICE_FILTER is not None and price < PRICE_FILTER:
                continue
            if CHANGE_FILTER is not None and change_24h_value < CHANGE_FILTER:
                continue

            scraped_data.append([timestamp, name, price, change_24h, market_cap])
        except Exception as e:
            print("Error parsing row:", e)
    file_exists = False
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            file_exists = True
    except FileNotFoundError:
        pass

    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Name", "Price (USD)", "24h Change (%)", "Market Cap"])
        writer.writerows(scraped_data)

    print(f"✅ {len(scraped_data)} records appended to {CSV_FILE}")

finally:
    driver.quit()
