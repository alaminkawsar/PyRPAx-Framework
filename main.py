from core.browser_manager import BrowserManager
from extractor.element_extractor import ElementExtractor
from repository.json_storage import JsonStorage
from screenshot.screenshot_service import ScreenshotService
from utils.name_utils import get_base_name, get_screen_name

import sys


def main():

    url = sys.argv[1]

    base_name = get_base_name(url)

    repo = {
        "base_url": url,
        "pages": {}
    }

    browser = BrowserManager()

    page, context = browser.start()

    extractor = ElementExtractor(repo)

    storage = JsonStorage()

    screenshot = ScreenshotService()

    def on_nav(frame):

        if frame != page.main_frame:
            return

        page.wait_for_load_state("load")

        name = get_screen_name(page)

        extractor.extract(page, name)

        screenshot.take(page, base_name, name)

        storage.save(repo, base_name)

    page.on("framenavigated", on_nav)

    page.goto(url)

    page.wait_for_timeout(999999999)


if __name__ == "__main__":
    main()