import os
import json
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By

def read_credentials(filepath):
    creds = {}
    with open(filepath, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                creds[key.strip()] = value.strip()
    return creds

def main():
    # ---------------- ARGUMENT PARSING ----------------
    parser = argparse.ArgumentParser(description="DOM Parsing for SAP UI Elements")
    parser.add_argument('--url', type=str, required=True, help='Target page URL')
    parser.add_argument('--page', type=str, required=True, help='Page name for subfolder (e.g., login_page)')
    args = parser.parse_args()

    URL = args.url
    PAGE_NAME = args.page

    # ---------------- CONFIG ----------------
    OUTPUT_FOLDER = "object_repository"
    PAGE_FOLDER = os.path.join(OUTPUT_FOLDER, PAGE_NAME)
    SCREENSHOT_FOLDER = os.path.join(PAGE_FOLDER, "screenshots")
    os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)
    JSON_FILE = os.path.join(PAGE_FOLDER, "object_repository.json")

    # ---------------- SETUP ----------------
    credentials = read_credentials('credentials.txt')
    email = credentials.get('email')
    password = credentials.get('password')

    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(URL)
    time.sleep(2)

    # ---- LOGIN AUTOMATION ----
    try:
        # Update these selectors as per your login page structure
        email_input = driver.find_element(By.XPATH, "//input[@type='email' or contains(@id, 'email') or contains(@name, 'email')]")
        password_input = driver.find_element(By.XPATH, "//input[@type='password' or contains(@id, 'password') or contains(@name, 'password')]")
        email_input.clear()
        email_input.send_keys(email)
        password_input.clear()
        password_input.send_keys(password)
        # Try to find and click the submit/continue button
        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit' or contains(text(), 'Continue') or contains(text(), 'Login') or contains(text(), 'Sign in')]")
        submit_btn.click()
        print("Login submitted.")
        time.sleep(5)  # Wait for navigation
    except Exception as e:
        print("Login automation failed:", e)

    # ---- PAGE NAME FOR POST-LOGIN ----
    # After login, extract elements for the next page
    PAGE_NAME_AFTER_LOGIN = PAGE_NAME + "_after_login"
    PAGE_FOLDER = os.path.join(OUTPUT_FOLDER, PAGE_NAME_AFTER_LOGIN)
    SCREENSHOT_FOLDER = os.path.join(PAGE_FOLDER, "screenshots")
    os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)
    JSON_FILE = os.path.join(PAGE_FOLDER, "object_repository.json")

    # ---------------- SMART XPATH ----------------
    xpath_query = """
    //input[not(@type='hidden')] |
     //button |
     //a |
     //select |
     //textarea |
     //*[@role='button'] |
     //*[@role='checkbox'] |
     //*[@role='radio']
    """

    elements = driver.find_elements(By.XPATH, xpath_query)

    object_repository = []

    print(f"Total elements found (raw): {len(elements)}")

    # ---------------- PROCESS ELEMENTS ----------------
    for index, el in enumerate(elements):
        try:
            if not el.is_displayed():
                continue

            location = el.location
            size = el.size

            x = location['x']
            y = location['y']
            width = size['width']
            height = size['height']

            # Skip very small elements (icons < 5px etc.)
            if width < 5 or height < 5:
                continue

            element_name = f"{el.tag_name}_{index}"
            screenshot_path = os.path.join(SCREENSHOT_FOLDER, f"{element_name}.png")

            # Save element screenshot directly (better than manual cropping)
            el.screenshot(screenshot_path)

            element_data = {
                "element_name": element_name,
                "tag": el.tag_name,
                "text": el.text.strip(),
                "type": el.get_attribute("type"),
                "role": el.get_attribute("role"),
                "id": el.get_attribute("id"),
                "class": el.get_attribute("class"),
                "aria_label": el.get_attribute("aria-label"),
                "coordinates": {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                },
                "screenshot_path": screenshot_path
            }

            object_repository.append(element_data)

            print(f"Saved: {element_name}")

        except Exception as e:
            print("Error processing element:", e)

    # ---------------- SAVE JSON ----------------
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(object_repository, f, indent=4)

    print(f"Done. Object repository for '{PAGE_NAME_AFTER_LOGIN}' generated successfully in {PAGE_FOLDER}.")
    driver.quit()

if __name__ == "__main__":
    main()