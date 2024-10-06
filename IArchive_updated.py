import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  
import time

def download_website_and_screenshot(url, output_dir):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the website: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string.strip().replace(' ', '_').replace('/', '_') if soup.title else "website"
    page_folder = os.path.join(output_dir, title)

    if not os.path.exists(page_folder):
        os.makedirs(page_folder)
    html_filename = os.path.join(page_folder, f"{title}.html")
    with open(html_filename, 'w', encoding='utf-8') as file:
        file.write(response.text)
    def download_resource(resource_url, folder_name):
        try:
            resource_url = urljoin(url, resource_url)
            resource_response = requests.get(resource_url, stream=True)
            resource_response.raise_for_status()

            resource_path = os.path.join(page_folder, folder_name, os.path.basename(resource_url))
            os.makedirs(os.path.dirname(resource_path), exist_ok=True)

            with open(resource_path, 'wb') as resource_file:
                shutil.copyfileobj(resource_response.raw, resource_file)

            print(f"Downloaded: {resource_url}")
            return os.path.join(folder_name, os.path.basename(resource_url))
        except Exception as e:
            print(f"Failed to download {resource_url}: {e}")
            return None
    for img in soup.find_all('img'):
        img_url = img.get('src')
        if img_url:
            local_img_path = download_resource(img_url, 'images')
            if local_img_path:
                img['src'] = local_img_path
    for script in soup.find_all('script'):
        script_url = script.get('src')
        if script_url:
            download_resource(script_url, 'scripts')
    with open(html_filename, 'w', encoding='utf-8') as file:
        file.write(str(soup))
    print(f"Website downloaded to {page_folder}")
    take_screenshot(url, page_folder)
def take_screenshot(url, save_folder):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get(url)
        time.sleep(5)  
        screenshot_path = os.path.join(save_folder, "screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
    except Exception as e:
        print(f"Error capturing the screenshot: {e}")
    finally:
        driver.quit()
def main():
    url = input("Enter the website URL: ").strip()
    output_dir = input("Enter the output directory path: ").strip()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("\nProcessing your request please wait.....")
    download_website_and_screenshot(url, output_dir)
if __name__ == "__main__":
    main()