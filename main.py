from core.browser_manager import BrowserManager
from extractor.element_extractor import ElementExtractor
from repository.json_storage import JsonStorage
from screenshot.screenshot_service import ScreenshotService
from utils.name_utils import get_base_name, get_screen_name, get_page_key
from screenshot.draw_annotator import DrawAnnotator
from playwright.sync_api import Error

from common.logger import Logger
logger = Logger.get_logger("main")

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
    logger.info("Browser instant created.")


    extractor = ElementExtractor(repo)
    storage = JsonStorage()
    screenshot = ScreenshotService()
    annotator = DrawAnnotator(base_name, repo)
    logger.info("All Instant created Successfully.")

    last_screen = {"name": None}


    # -----------------------------
    # COMMON UI CHANGE HANDLER
    # -----------------------------
    def handle_ui_change():

        try:
            logger.info("handle_ui_change(): Waiting for network idle...")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(700)
        except:
            pass

        name = get_page_key(page)

        # prevent duplicate extraction
        if name == last_screen["name"]:
            return

        last_screen["name"] = name

        logger.info(f"Loaded -> {name}")

        # -------- MAIN PAGE EXTRACTION (unchanged behavior)
        try:
            logger.info(f"Extracting from page: {page.url}")
            extractor.extract(page, name)
        except:
            pass

        # -------- IFRAME EXTRACTION (new)
        for frame in page.frames:
            if frame == page.main_frame:
                continue

            try:
                logger.info(f"Extracting from frame: {frame.url}")
                extractor.extract(frame, name)
            except:
                pass

        screenshot.take(page, base_name, name)

        storage.save(repo, base_name)
        logger.info("Data saved to repository.")


    # -----------------------------
    # NAVIGATION (URL change)
    # -----------------------------
    def on_nav(frame):

        if frame != page.main_frame:
            return

        try:
            logger.info(f"on_nav(): Navigated to: {frame.url}")
            logger.info("on_nav(): Waiting for load state...")
            page.wait_for_load_state("load")
        except:
            pass

        handle_ui_change()


    # -----------------------------
    # AJAX / FETCH / API change
    # -----------------------------
    def on_response(response):
        logger.debug(f"on_response(): Response received: {response.url}")
        logger.debug(f"on_response(): Resource type: {response.request.resource_type}")
        try:
            if response.request.resource_type in ["xhr", "fetch"]:
                handle_ui_change()
        except:
            pass


    # -----------------------------
    # DOM change (textfield submit case)
    # -----------------------------
    def on_dom_loaded(_):

        try:
            page.wait_for_timeout(500)
            handle_ui_change()
        except:
            pass


    # -----------------------------
    # EVENT LISTENERS
    # -----------------------------
    page.on("framenavigated", on_nav)
    page.on("response", on_response)
    page.on("domcontentloaded", on_dom_loaded)


    # -----------------------------
    # START
    # -----------------------------
    page.goto(url)

    try:
        page.wait_for_timeout(999999999)

    except Error:
        logger.info("Stopped safely")

    # annotate the elements
    annotator.draw_all()


if __name__ == "__main__":
    main()