from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re

chromedriver_path = r"C:\Users\fairp\Downloads\chromedriver-win64\chromedriver.exe"
brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

options = Options()
options.binary_location = brave_path
options.add_argument("--headless")  
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)


def google_search(query, max_results=50):
    """Search Google and return URLs"""
    urls = []
    for start in range(0, max_results, 10):
        driver.get(f"https://www.google.com/search?q={query}&num=10&start={start}")
        time.sleep(2)
        results = driver.find_elements(By.XPATH, '//a[@href]')
        for r in results:
            href = r.get_attribute('href')
            if href and "http" in href:
                urls.append(href)
    return list(set(urls))

def extract_email_from_text(text):
    """Regex extract emails"""
    return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}', text)

def get_employee_data_from_page(url):
    """Scrape a page for employee data"""
    print(f"\n[*] Scraping website: {url}")
    driver.get(url)
    time.sleep(2)
    data = {"Website": url, "Name": "Not found", "Role": "Not found", "Email": "Not found"}

    emails = extract_email_from_text(driver.page_source)
    if emails:
        data["Email"] = emails[0]

    try:
        title = driver.title
        data["Name"] = title
    except:
        pass

    print(f"--> Extracted Data: Name/Title: {data['Name']}, Email: {data['Email']}")
    return data


if __name__ == "__main__":
    company_name = input("Enter company name: ").strip()
    print(f"[*] Starting search for employees of {company_name}...\n")

    urls = google_search(f"{company_name} employees email OR contact OR team OR staff", max_results=100)
    print(f"[*] Found {len(urls)} URLs to process.\n")

    employees = []

    for idx, url in enumerate(urls, start=1):
        print(f"[{idx}/{len(urls)}] Visiting: {url}")
        try:
            data = get_employee_data_from_page(url)
            employees.append(data)
        except Exception as e:
            print(f"[!] Error processing {url}: {e}")
        time.sleep(1)  

    if employees:
        df = pd.DataFrame(employees)
        file_name = f"{company_name}_employees.xlsx"
        df.to_excel(file_name, index=False)
        print(f"\n[✓] Saved {len(employees)} records to {file_name}")
    else:
        print("\n[!] No employee data found. Excel file not created.")

    driver.quit()
