from playwright.sync_api import sync_playwright, Error
import json
import os
import sys
from urllib.parse import urlparse

def extract_elements(page, screen_name, repo, output_file=None):
    # Define smart selectors for common UI elements
    selectors = [
        "input:not([type='hidden'])",
        "button",
        "a",
        "select",
        "textarea",
        "[role='button']",
        "[role='checkbox']",
        "[role='radio']"
    ]
    elements = []
    for selector in selectors:
        elements.extend(page.query_selector_all(selector))
    print(f"[{screen_name}] Found {len(elements)} elements.")
    for idx, el in enumerate(elements):
        try:
            box = el.bounding_box()
            if not box or box['width'] < 5 or box['height'] < 5:
                continue
            tag = el.evaluate('e => e.tagName.toLowerCase()')
            element_name = f"{tag}_{idx}"
            el_info = {
                "element_name": element_name,
                "tag": tag,
                "text": el.inner_text() if tag != 'input' else '',
                "type": el.get_attribute("type"),
                "role": el.get_attribute("role"),
                "id": el.get_attribute("id"),
                "class": el.get_attribute("class"),
                "aria_label": el.get_attribute("aria-label"),
                "coordinates": {
                    "x": box['x'],
                    "y": box['y'],
                    "width": box['width'],
                    "height": box['height']
                },
                "selector": selector
            }
            repo[screen_name].append(el_info)
        except Error as e:
            if "Target page, context or browser has been closed" in str(e):
                print("Browser was closed by user during element extraction. Stopping extraction.")
                # Save repository before breaking
                if output_file:
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(repo, f, indent=4)
                    print(f"Object repository saved to {output_file} before exit.")
                break
            print(f"Error processing element: {e}")
        except Exception as e:
            print(f"Error processing element: {e}")

def main():
    repo = {}
    OUTPUT_FILE = "object_repository/uipath_object_repository.json"
    os.makedirs("object_repository", exist_ok=True)
    if len(sys.argv) < 2:
        print("Usage: python dom_parsing_using_playright.py <url>")
        sys.exit(1)
    start_url = sys.argv[1]
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            # 1. Go to start page and extract elements
            page.goto(start_url)
            page.wait_for_load_state("load")
            parsed = urlparse(page.url)
            screen_name = parsed.path.strip("/") or parsed.netloc
            if not screen_name:
                screen_name = "start_page"
            repo[screen_name] = []
            extract_elements(page, screen_name, repo, OUTPUT_FILE)

            # 2. Optionally perform sign-in (update selectors as needed)
            try:
                page.wait_for_selector("input[type='email']")
                page.fill("input[type='email']", "your_email@example.com")
                page.wait_for_selector("input[type='password']")
                page.fill("input[type='password']", "your_password")
                with page.expect_navigation():
                    page.click("button[type='submit'], button:has-text('Sign in'), button:has-text('Login'), button:has-text('Continue')")
            except Exception as e:
                page.screenshot(path="login_debug.png")
                print(f"Login failed: {e}. Screenshot saved as login_debug.png")

            # 3. After navigation, extract elements from new page with dynamic name
            page.wait_for_load_state("load")
            parsed = urlparse(page.url)
            screen_name = parsed.path.strip("/") or parsed.netloc
            if not screen_name:
                screen_name = "page_after_login"
            if screen_name not in repo:
                repo[screen_name] = []
            extract_elements(page, screen_name, repo, OUTPUT_FILE)

            # Save the repository
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(repo, f, indent=4)
            print(f"Object repository saved to {OUTPUT_FILE}")
            browser.close()
    except Error as e:
        if "Target page, context or browser has been closed" in str(e):
            # Save repository even if browser was closed by user
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(repo, f, indent=4)
            print(f"Browser was closed by user. Object repository saved to {OUTPUT_FILE}.")
        else:
            print(f"Playwright error: {e}")

if __name__ == "__main__":
    main()
