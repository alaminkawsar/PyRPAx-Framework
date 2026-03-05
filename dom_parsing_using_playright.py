from playwright.sync_api import sync_playwright
import json
import os

def extract_elements(page, screen_name, repo):
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
        except Exception as e:
            print(f"Error processing element: {e}")

def main():
    repo = {}
    OUTPUT_FILE = "object_repository/uipath_object_repository.json"
    os.makedirs("object_repository", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 1. Go to sign-in page and extract elements
        signin_url = "https://my402955.s4hana.cloud.sap/ui#Shell-home"  # <-- Replace with your sign-in URL
        page.goto(signin_url)
        page.wait_for_timeout(3000)
        repo["sign_in"] = []
        extract_elements(page, "sign_in", repo)

        # 2. Perform sign-in (update selectors as needed)
        try:
            page.wait_for_selector("input[type='email']", timeout=30000)
            page.fill("input[type='email']", "your_email@example.com")
            page.wait_for_selector("input[type='password']", timeout=30000)
            page.fill("input[type='password']", "your_password")
            with page.expect_navigation():
                page.click("button[type='submit'], button:has-text('Sign in'), button:has-text('Login'), button:has-text('Continue')")
        except Exception as e:
            page.screenshot(path="login_debug.png")
            print(f"Login failed: {e}. Screenshot saved as login_debug.png")
        # Wait for a unique element on the home page to ensure it's loaded
        # Replace the selector below with one unique to your home page
        try:
            page.wait_for_selector("header, nav, [data-homepage], .dashboard, .home-main", timeout=20000)
        except Exception as e:
            print(f"Home page unique selector not found: {e}")
        # 3. Extract elements from home page
        repo["home_page"] = []
        extract_elements(page, "home_page", repo)

        # Save the repository
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(repo, f, indent=4)
        print(f"Object repository saved to {OUTPUT_FILE}")
        browser.close()

if __name__ == "__main__":
    main()
