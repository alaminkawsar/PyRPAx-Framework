from playwright.sync_api import sync_playwright, Error
import json
import os
import sys
from urllib.parse import urlparse


OUTPUT_FILE = "object_repository/uipath_object_repository.json"


# -----------------------------
# Utility: Save JSON safely
# -----------------------------
def save_repo(repo):
    os.makedirs("object_repository", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(repo, f, indent=4)
    print(f"Saved -> {OUTPUT_FILE}")


# -----------------------------
# Utility: screen name from URL
# -----------------------------
def get_screen_name(url):
    parsed = urlparse(url)
    name = parsed.path.strip("/")

    if not name:
        name = parsed.netloc

    if not name:
        name = "start_page"

    return name.replace("/", "_")


# -----------------------------
# Extract elements
# -----------------------------
def extract_elements(page, screen_name, repo):

    selectors = [
        "input:not([type='hidden'])",
        "button",
        "a",
        "select",
        "textarea",
        "[role='button']",
        "[role='checkbox']",
        "[role='radio']",
    ]

    if screen_name not in repo["pages"]:
        repo["pages"][screen_name] = []

    elements = []

    for s in selectors:
        elements.extend(page.query_selector_all(s))

    print(f"[{screen_name}] Found {len(elements)} elements")

    for idx, el in enumerate(elements):

        try:
            box = el.bounding_box()

            if not box:
                continue

            if box["width"] < 5 or box["height"] < 5:
                continue

            tag = el.evaluate("e => e.tagName.toLowerCase()")

            el_info = {
                "name": f"{tag}_{idx}",
                "tag": tag,
                "text": el.inner_text() if tag != "input" else "",
                "type": el.get_attribute("type"),
                "id": el.get_attribute("id"),
                "class": el.get_attribute("class"),
                "role": el.get_attribute("role"),
                "aria_label": el.get_attribute("aria-label"),
                "selector": s,
                "box": box,
            }

            repo["pages"][screen_name].append(el_info)

        except Exception:
            pass


# -----------------------------
# Main
# -----------------------------
def main():

    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "python script.py <url> [browser]\n"
            "browser = chromium | firefox | webkit"
        )
        sys.exit(1)

    url = sys.argv[1]
    browser_name = sys.argv[2] if len(sys.argv) > 2 else "chromium"

    repo = {
        "pages": {}
    }

    try:

        with sync_playwright() as p:

            browser_type = getattr(p, browser_name)

            browser = browser_type.launch(headless=False)

            context = browser.new_context()

            page = context.new_page()

            # -------------------------
            # On navigation → extract
            # -------------------------
            def on_nav(frame):

                if frame != page.main_frame:
                    return

                try:
                    page.wait_for_load_state("load")

                    name = get_screen_name(page.url)

                    print("Navigated ->", name)

                    extract_elements(page, name, repo)

                    save_repo(repo)

                except Error:
                    pass


            page.on("framenavigated", on_nav)


            # -------------------------
            # On close → save
            # -------------------------
            def on_close():

                print("Browser closed by user")

                save_repo(repo)


            context.on("close", lambda _: on_close())


            # -------------------------
            # Start
            # -------------------------
            page.goto(url)

            print("Running... close browser to stop")

            page.wait_for_timeout(999999999)


    except Error:

        save_repo(repo)

        print("Stopped safely")


if __name__ == "__main__":
    main()