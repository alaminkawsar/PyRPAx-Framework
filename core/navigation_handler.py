from core.extractor import extract_elements
from core.saver import save_repo
from core.screenshot import take_screenshot
from core.utils import get_screen_name


def create_nav_handler(
    page,
    repo,
    base_name
):

    def on_nav(frame):

        if frame != page.main_frame:
            return

        try:

            page.wait_for_load_state(
                "load"
            )

            screen_name = get_screen_name(
                page.url
            )

            print(
                "Navigated ->",
                screen_name
            )

            extract_elements(
                page,
                screen_name,
                repo,
            )

            take_screenshot(
                page,
                base_name,
                screen_name,
            )

            save_repo(
                repo,
                base_name,
            )

        except Exception:
            pass

    return on_nav