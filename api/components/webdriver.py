# Import necessary Selenium modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_channel(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    # Initialize Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Wait for video title elements to be present
    channels = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.ID, 'video-title'))
    )
    
    # Extract video titles
    titles = []
    for i in range(min(10, len(channels))):
        if channels[i].text != '':
            titles.append(channels[i].text)
    return titles

""" if __name__ == "__main__":
    s = scrape_channel("https://www.youtube.com/@Unbounce/videos")
    print(s) """



