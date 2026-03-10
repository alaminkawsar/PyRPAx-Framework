from playwright.sync_api import sync_playwright
from core.navigation_handler import (
    create_nav_handler,
)
from core.saver import save_repo


def run_browser(
    url,
    browser_name,
    repo,
    base_name,
):

    with sync_playwright() as p:

        browser_type = getattr(
            p,
            browser_name,
        )

        browser = browser_type.launch(
            headless=False
        )

        context = browser.new_context()

        page = context.new_page()

        handler = create_nav_handler(
            page,
            repo,
            base_name,
        )

        page.on(
            "framenavigated",
            handler,
        )

        context.on(
            "close",
            lambda _: save_repo(
                repo,
                base_name,
            ),
        )

        page.goto(url)

        page.wait_for_timeout(
            999999999
        )