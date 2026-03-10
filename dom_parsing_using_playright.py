from playwright.sync_api import sync_playwright, Error
import json
import os
import sys
import re
from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageFont


# -----------------------------
# Base name
# -----------------------------
def get_base_name(url):

    parsed = urlparse(url)

    name = parsed.netloc.replace(":", "_")

    name = re.sub(r'[\\/*?:"<>|]', "_", name)

    return name


# -----------------------------
# Safe page title
# -----------------------------
def get_screen_name(page):

    try:

        title = page.title()

        if not title:
            title = "untitled"

        title = re.sub(r'[\\/*?:"<>|]', "_", title)

        title = title.strip()

        title = title[:120]

        return title

    except:
        return "unknown_page"


# -----------------------------
# Save JSON
# -----------------------------
def save_repo(repo, base_name):

    os.makedirs("output", exist_ok=True)

    path = f"output/{base_name}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(repo, f, indent=4)

    print("Saved ->", path)


# -----------------------------
# Screenshot
# -----------------------------
def take_screenshot(page, base_name, screen_name):

    dir_path = f"output/screenshots/{base_name}"

    os.makedirs(dir_path, exist_ok=True)

    path = f"{dir_path}/{screen_name}.png"

    page.screenshot(path=path, full_page=True)

    print("Screenshot ->", path)


# -----------------------------
# FULL control detection
# -----------------------------
def detect_control(tag, el_type, role, el):

    tag = (tag or "").lower()
    el_type = (el_type or "").lower()
    role = (role or "").lower()

    try:
        aria_checked = el.get_attribute("aria-checked")
        aria_selected = el.get_attribute("aria-selected")
        aria_expanded = el.get_attribute("aria-expanded")
        href = el.get_attribute("href")
        onclick = el.get_attribute("onclick")
        tabindex = el.get_attribute("tabindex")
    except:
        aria_checked = None
        aria_selected = None
        aria_expanded = None
        href = None
        onclick = None
        tabindex = None

    if tag == "input":

        if el_type in ["text", ""]:
            return "textbox"

        if el_type == "password":
            return "password"

        if el_type == "checkbox":
            return "checkbox"

        if el_type == "radio":
            return "radio"

        if el_type == "file":
            return "file"

        if el_type == "date":
            return "date"

        if el_type == "number":
            return "number"

        if el_type == "email":
            return "email"

        if el_type == "search":
            return "search"

        if el_type == "submit":
            return "submit"

        if el_type == "button":
            return "button"

        return "input"

    if tag == "textarea":
        return "textarea"

    if tag == "select":
        return "dropdown"

    if tag == "button":
        return "button"

    if tag == "a":
        return "link"

    if role == "button":
        return "button"

    if role == "checkbox":
        return "checkbox"

    if role == "radio":
        return "radio"

    if role == "textbox":
        return "textbox"

    if role == "combobox":
        return "combobox"

    if role == "switch":
        return "switch"

    if role == "tab":
        return "tab"

    if role == "menuitem":
        return "menu"

    if aria_checked is not None:
        return "checkbox"

    if aria_selected is not None:
        return "selectable"

    if aria_expanded is not None:
        return "expand"

    if onclick:
        return "button"

    if tabindex is not None:
        return "focusable"

    return "element"


# -----------------------------
# Label text
# -----------------------------
def get_label_text(el):

    try:

        label = el.evaluate(
            """e => {
                if (e.labels && e.labels.length > 0)
                    return e.labels[0].innerText
                return null
            }"""
        )

        return label

    except:
        return None


# -----------------------------
# Extract elements
# -----------------------------
def extract_elements(page, screen_name, repo):

    selectors = [

        "input:not([type='hidden'])",
        "textarea",
        "select",
        "button",
        "a",
        "label",

        "[role='button']",
        "[role='checkbox']",
        "[role='radio']",
        "[role='textbox']",
        "[role='combobox']",
        "[role='switch']",

        "[aria-label]",
        "[aria-checked]",
        "[aria-selected]",

        "[tabindex]",

        "[data-testid]",
        "[data-id]",
    ]

    if screen_name not in repo["pages"]:
        repo["pages"][screen_name] = []

    elements = []

    for s in selectors:

        for el in page.query_selector_all(s):
            elements.append((el, s))

    print(f"[{screen_name}] Found {len(elements)}")

    for idx, (el, sel) in enumerate(elements):

        try:

            box = el.bounding_box()

            if not box:
                continue

            if box["width"] < 5 or box["height"] < 5:
                continue

            tag = el.evaluate(
                "e => e.tagName.toLowerCase()"
            )

            el_type = el.get_attribute("type")
            role = el.get_attribute("role")

            text = None

            if tag != "input":
                text = el.inner_text()
            else:
                text = el.get_attribute("value")

            el_id = el.get_attribute("id")

            name_attr = el.get_attribute("name")

            placeholder = el.get_attribute("placeholder")

            autocomplete = el.get_attribute("autocomplete")

            title = el.get_attribute("title")

            aria_label = el.get_attribute("aria-label")

            el_class = el.get_attribute("class")

            data_testid = el.get_attribute("data-testid")

            data_id = el.get_attribute("data-id")

            label = get_label_text(el)

            control_type = detect_control(
                tag,
                el_type,
                role,
                el
            )

            info = {

                "name": f"{tag}_{idx}",

                "control_type": control_type,

                "tag": tag,

                "text": text,

                "type": el_type,

                "id": el_id,

                "name_attr": name_attr,

                "placeholder": placeholder,

                "autocomplete": autocomplete,

                "title": title,

                "label": label,

                "class": el_class,

                "role": role,

                "aria_label": aria_label,

                "data_testid": data_testid,

                "data_id": data_id,

                "selector": sel,

                "box": box,
            }

            if info not in repo["pages"][screen_name]:
                repo["pages"][screen_name].append(info)

        except:
            pass


# -----------------------------
# DRAW ALL PAGES
# -----------------------------
def draw_all_pages(repo, base_name):

    img_dir = f"output/screenshots/{base_name}"

    out_dir = f"{img_dir}/annotated"

    os.makedirs(out_dir, exist_ok=True)

    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()

    for page_name, elements in repo["pages"].items():

        img_path = f"{img_dir}/{page_name}.png"

        if not os.path.exists(img_path):
            continue

        out_path = f"{out_dir}/{page_name}_anchor.png"

        img = Image.open(img_path)

        draw = ImageDraw.Draw(img)

        for el in elements:

            box = el["box"]

            x = box["x"]
            y = box["y"]
            w = box["width"]
            h = box["height"]

            x2 = x + w
            y2 = y + h

            t = el.get("control_type")

            color = "red"

            if t == "textbox":
                color = "blue"

            elif t == "password":
                color = "purple"

            elif t == "button":
                color = "green"

            elif t == "checkbox":
                color = "orange"

            elif t == "radio":
                color = "yellow"

            draw.rectangle(
                [x, y, x2, y2],
                outline=color,
                width=2
            )

            label = el["name"]

            if el.get("id"):
                label += f" | {el['id']}"

            if t:
                label += f" | {t}"

            draw.rectangle(
                [x, y - 15, x + 220, y],
                fill=color
            )

            draw.text(
                (x + 2, y - 14),
                label,
                fill="white",
                font=font
            )

        img.save(out_path)

        print("Annotated ->", out_path)


# -----------------------------
# MAIN
# -----------------------------
def main():

    if len(sys.argv) < 2:
        print("Usage: python script.py <url>")
        sys.exit(1)

    url = sys.argv[1]

    base_name = get_base_name(url)

    repo = {
        "base_url": url,
        "pages": {}
    }

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=False
            )

            context = browser.new_context()

            page = context.new_page()

            def on_nav(frame):

                if frame != page.main_frame:
                    return

                page.wait_for_load_state("load")

                name = get_screen_name(page)

                print("Navigated ->", name)

                extract_elements(
                    page,
                    name,
                    repo
                )

                take_screenshot(
                    page,
                    base_name,
                    name
                )

                save_repo(
                    repo,
                    base_name
                )

            page.on(
                "framenavigated",
                on_nav
            )

            def on_close():

                save_repo(
                    repo,
                    base_name
                )

                draw_all_pages(
                    repo,
                    base_name
                )

            context.on(
                "close",
                lambda _: on_close()
            )

            page.goto(url)

            print("Running...")

            page.wait_for_timeout(
                999999999
            )

    except Error:

        save_repo(
            repo,
            base_name
        )

        draw_all_pages(
            repo,
            base_name
        )

        print("Stopped safely")


if __name__ == "__main__":
    main()