import os
import time
import requests
import re
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from deep_translator import GoogleTranslator

def download_image(url, folder, filename):
    """Downloads an image from a URL and saves it locally."""
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filepath = os.path.join(folder, filename)
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            return filepath
    except Exception as e:
        print(f"Failed to download image: {e}")
    return None

def run_scraper(driver):
    wait = WebDriverWait(driver, 10)
    
    # 1. Visit El País and ensure it's in Spanish (default base URL is Spanish)
    driver.get("https://elpais.com/")
    
    # Accept cookies if the banner appears (El Pais uses Didomi)
    try:
        cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_btn.click()
        time.sleep(1)
    except:
        print("No cookie banner found or already accepted.")

    # 2. Navigate to the Opinion section
    driver.get("https://elpais.com/opinion/")
    
    # 3. Fetch the first five articles
    # Wait for the article containers to load
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
    
    # Find the links to the first 5 articles
    article_elements = driver.find_elements(By.XPATH, "//article//h2/a")[:5]
    article_urls = [el.get_attribute("href") for el in article_elements]
    
    scraped_data = []

    for idx, url in enumerate(article_urls):
        print(f"\n--- Scraping Article {idx + 1} ---")
        driver.get(url)
        time.sleep(2) # Give the page a moment to load
        
        # Get Title
        try:
            title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text
            print(f"Title: {title}")
        except:
            title = "No title found"
            
        # Get Content (Usually in paragraphs within the article body)
        try:
            paragraphs = driver.find_elements(By.XPATH, "//article//p | //div[@data-dtm-region='articulo_cuerpo']//p")
            content = " ".join([p.text for p in paragraphs if p.text.strip() != ""])
            print(f"Content snippet: {content[:150]}...")
        except:
            content = "No content found"
            
        # Get Image (First relevant image in the article)
        img_url = None
        try:
            image_element = driver.find_element(By.XPATH, "//article//img | //figure//img")
            img_url = image_element.get_attribute("src")
            if img_url:
                download_image(img_url, "article_images", f"cover_{idx+1}.jpg")
                print(f"Image downloaded: cover_{idx+1}.jpg")
        except:
            print("No cover image found.")
            
        scraped_data.append({"title": title, "content": content})
        
    return scraped_data

def process_and_translate(scraped_data):
    translator = GoogleTranslator(source='es', target='en')
    translated_titles = []
    
    print("\n--- Translated Headers ---")
    for data in scraped_data:
        translated_title = translator.translate(data['title'])
        translated_titles.append(translated_title)
        print(translated_title)
        
    # Analyze Translated Headers for repeated words (> 2)
    print("\n--- Word Frequency Analysis ---")
    all_words = []
    for title in translated_titles:
        # Clean punctuation and convert to lowercase
        clean_title = re.sub(r'[^\w\s]', '', title).lower()
        all_words.extend(clean_title.split())
        
    word_counts = Counter(all_words)
    repeated_words = {word: count for word, count in word_counts.items() if count > 2}
    
    if repeated_words:
        for word, count in repeated_words.items():
            print(f"'{word}': {count} times")
    else:
        print("No words were repeated more than twice.")

if __name__ == "__main__":
    # Local Test Execution
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Uncomment to run invisibly
    driver = webdriver.Chrome(options=options)
    
    try:
        data = run_scraper(driver)
        process_and_translate(data)
    finally:
        driver.quit()