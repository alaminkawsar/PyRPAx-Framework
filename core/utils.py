from urllib.parse import urlparse


def get_base_name(url):
    parsed = urlparse(url)
    return parsed.netloc.replace(":", "_")


def get_screen_name(url):

    parsed = urlparse(url)

    name = parsed.path.strip("/")

    if not name:
        name = "start_page"

    return name.replace("/", "_")