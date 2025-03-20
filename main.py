from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pickle
import requests

# Setup WebDriver (Use Chrome with specified path)
chrome_driver_path = r"C:\Users\BINIT SINGH\Desktop\SCRIIPTS\chromedriver-win64\chromedriver.exe"
service = Service(chrome_driver_path)

driver = webdriver.Chrome(service=service)
driver.get("https://altenens.is")

# Path to save cookies
cookies_file = "altenens_cookies.pkl"

# Telegram Bot Token and Chat IDs
TELEGRAM_BOT_TOKEN = "7266837701:AAEbCLRuSwdPeW62FW-fBRv2LB0xd6-WHIg"
CHAT_IDS = ["5648694628", "7284684032"]  # List of Telegram IDs

# Check if cookies exist (to skip login)
if os.path.exists(cookies_file):
    print("🔵 Using saved login session...")
    with open(cookies_file, "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

    driver.refresh()  # Apply cookies
else:
    print("🔴 Logging in for the first time...")

    # Click on Login button
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="top"]/div[1]/div/div/div/div[1]/a[1]/span'))
    ).click()

    # Wait for input fields to appear
    email_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.NAME, "login"))
    )
    password_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.NAME, "password"))
    )

    # Enter Email & Password
    email_input.send_keys("jessipinkman619@gmail.com")
    password_input.send_keys("@Jessi2020")

    # Press ENTER instead of clicking button
    password_input.send_keys(Keys.RETURN)

    # Wait for login to process
    time.sleep(5)

    # Save Cookies
    with open(cookies_file, "wb") as file:
        pickle.dump(driver.get_cookies(), file)

    print("✅ Login Successful & Cookies Saved!")

def navigate_to_forum():
    driver.get("https://altenens.is/forums/accounts-and-database-dumps.45/")
    time.sleep(5)

navigate_to_forum()

# Extract latest thread title & link, skipping first two sticky threads
def get_latest_thread():
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.structItem-title a'))
    )
    threads = driver.find_elements(By.CSS_SELECTOR, 'div.structItem-title a')
    
    # Skipping first two sticky threads
    if len(threads) > 3:
        latest_thread = threads[3]  # Fourth thread (index 3) is the first non-sticky
        return latest_thread.text, latest_thread.get_attribute('href')
    else:
        return None, None

def get_thread_content(thread_url):
    driver.get(thread_url)
    time.sleep(5)
    try:
        post_content = driver.find_element(By.CSS_SELECTOR, 'div.bbWrapper').text
        return post_content
    except:
        return "⚠️ Unable to extract thread content."
    finally:
        navigate_to_forum()  # Ensure script returns to forum page

def send_telegram_message(message):
    for chat_id in CHAT_IDS:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {"chat_id": chat_id, "text": message}
        requests.post(url, params=params)

latest_title, latest_url = get_latest_thread()
if latest_title and latest_url:
    print(f"🔹 Latest Thread: {latest_title}\n🔗 Link: {latest_url}")
    thread_content = get_thread_content(latest_url)
    print(f"📝 Content:\n{thread_content}")
    send_telegram_message(thread_content)
else:
    print("⚠️ No normal threads found.")

# Continuously check for new threads
previous_title = latest_title
while True:
    time.sleep(10)  # Adjust delay as needed
    driver.refresh()
    new_title, new_url = get_latest_thread()

    if new_title and new_title != previous_title:
        print(f"🆕 New Thread Detected: {new_title}\n🔗 Link: {new_url}")
        thread_content = get_thread_content(new_url)
        print(f"📝 Content:\n{thread_content}")
        send_telegram_message(thread_content)
        previous_title = new_title  # Update last seen thread
