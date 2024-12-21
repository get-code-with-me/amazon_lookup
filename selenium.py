from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import json
import time
import random
import re

def login(driver):
    """
    Logs in to Amazon using provided credentials.

    Args:
        driver: Selenium WebDriver instance.

    Raises:
        Exception: If login fails.
    """
    driver.get("https://www.amazon.com/ap/signin")

    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ap_email"))
    )
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ap_password"))
    )

    # Enter your credentials here
    username_field.send_keys("your_username")
    password_field.send_keys("your_password")

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "signInSubmit"))
    )
    login_button.click()

    # Wait for login to complete
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "nav-cart-count"))
    )  # Example: Check for cart icon after login

    print("Login successful!")

def scrape_category(driver, category):
    """
    Scrapes product data from a given Amazon Best Sellers category.

    Args:
        driver: Selenium WebDriver instance.
        category: Name of the category to scrape.

    Returns:
        list: List of dictionaries, each containing product data.
    """
    driver.get(f"https://www.amazon.com/bestsellers/{category}")

    products = []
    page_number = 1

    while True:
        product_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-component-type='s-search-result']"))
        )

        for product in product_elements:
            try:
                product_data = {}

                # Extract product details
                product_data["Name"] = product.find_element(By.XPATH, ".//h2/a").text
                product_data["Price"] = product.find_element(By.XPATH, ".//span[contains(@class, 'a-offscreen')]").text
                product_data["Sale_Discount"] = product.find_element(By.XPATH, ".//span[contains(@class, 'a-color-price')]").text
                # ... Extract other details (Best Seller Rating, Ship From, Sold By, etc.)

                # Check if discount is greater than 50%
                discount_percentage_str = product_data["Sale_Discount"].strip("%")
                if discount_percentage_str:
                    discount_percentage = float(re.findall(r'\d+\.\d+|\d+', discount_percentage_str)[0])
                    if discount_percentage > 50:
                        products.append(product_data)

            except Exception as e:
                print(f"Error processing product: {e}")

        # Check if there's a "Next Page" button
        next_page_button = driver.find_element(By.XPATH, "//a[contains(@class, 's-pagination-next')]")
        if not next_page_button.is_enabled():
            break

        next_page_button.click()
        page_number += 1

        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-component-type='s-search-result']"))
        )

        # Limit to top 1500 products
        if len(products) >= 1500:
            break

    return products

def store_data(data, filename):
    """
    Stores scraped data in CSV and JSON formats.

    Args:
        data: List of dictionaries containing product data.
        filename: Base filename for output files.
    """
    df = pd.DataFrame(data)
    df.to_csv(f"{filename}.csv", index=False)

    with open(f"{filename}.json", "w") as f:
        json.dump(data, f, indent=4)

if _name_ == "_main_":
    categories = ["electronics", "books", "clothing", "home", ...]  # List of categories

    driver = webdriver.Chrome()  # Replace with your preferred browser

    try:
        login(driver)

        all_products = []
        for category in categories:
            print(f"Scraping {category}...")
            category_products = scrape_category(driver, category)
            all_products.extend(category_products)
            time.sleep(random.uniform(2, 5))  # Add random delay to avoid being blocked

        store_data(all_products, "amazon_products")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()