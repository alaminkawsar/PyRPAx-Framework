import os
from config import SCREENSHOT_DIR


def take_screenshot(page, base_name, screen_name):

    dir_path = f"{SCREENSHOT_DIR}/{base_name}"

    os.makedirs(dir_path, exist_ok=True)

    file_path = f"{dir_path}/{screen_name}.png"

    page.screenshot(
        path=file_path,
        full_page=True
    )

    print("Screenshot ->", file_path)