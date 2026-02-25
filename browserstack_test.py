import os
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from local_scraper import run_scraper
# 1. Pull credentials securely from PowerShell environment variables
BROWSERSTACK_USERNAME = os.environ.get("BROWSERSTACK_USERNAME")
BROWSERSTACK_ACCESS_KEY = os.environ.get("BROWSERSTACK_ACCESS_KEY")

if not BROWSERSTACK_USERNAME or not BROWSERSTACK_ACCESS_KEY:
    print("Error: BrowserStack credentials not found in environment variables.")
    exit()

URL = f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"

# 2. Define environments (Desktop + Mobile)
environments = [
    {"bstack:options": {"os": "Windows", "osVersion": "11", "sessionName": "Win_Chrome"}, "browserName": "Chrome"},
    {"bstack:options": {"os": "OS X", "osVersion": "Ventura", "sessionName": "Mac_Safari"}, "browserName": "Safari"},
    {"bstack:options": {"os": "Windows", "osVersion": "10", "sessionName": "Win_Firefox"}, "browserName": "Firefox"},
    {"bstack:options": {"osVersion": "14.0", "deviceName": "iPhone 14", "sessionName": "iOS_Safari", "realMobile": "true"}, "browserName": "safari"},
    {"bstack:options": {"osVersion": "13.0", "deviceName": "Samsung Galaxy S23", "sessionName": "Android_Chrome", "realMobile": "true"}, "browserName": "chrome"}
]

def get_browser_options(env):
    browser_name = env.get("browserName", "").lower()
    if browser_name == "chrome":
        options = ChromeOptions()
    elif browser_name == "safari":
        options = SafariOptions()
    elif browser_name == "firefox":
        options = FirefoxOptions()
    else:
        options = ChromeOptions()
        
    options.set_capability('bstack:options', env.get('bstack:options', {}))
    return options

def run_session(env):
    options = get_browser_options(env)
    session_name = env.get('bstack:options', {}).get('sessionName', 'Unknown')
    print(f"Starting execution on: {session_name}...")
    
    driver = webdriver.Remote(command_executor=URL, options=options)
    
  try:
        # Execute the actual scraping logic on the cloud browsers
        scraped_data = run_scraper(driver)
        
        if scraped_data:
            print(f"[{session_name}] Successfully scraped {len(scraped_data)} articles.")
            driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Scraping completed successfully"}}')
        else:
            driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "No data scraped"}}')
            
    except Exception as e:
        print(f"[{session_name}] Error: {e}")
        driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Exception occurred"}}')
        finally:
        driver.quit()

if __name__ == "__main__":
    print("Sending tests to BrowserStack...")
    # Execute 5 threads in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(run_session, environments)
    print("All parallel tests completed!")
