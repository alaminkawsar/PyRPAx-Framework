import sys

from core.browser_manager import (
    run_browser,
)
from core.utils import (
    get_base_name,
)


def main():

    if len(sys.argv) < 2:
        print(
            "Usage: python main.py <url> [browser]"
        )
        return

    url = sys.argv[1]

    browser = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "chromium"
    )

    base_name = get_base_name(url)

    repo = {
        "base_url": url,
        "pages": {},
    }

    run_browser(
        url,
        browser,
        repo,
        base_name,
    )


if __name__ == "__main__":
    main()