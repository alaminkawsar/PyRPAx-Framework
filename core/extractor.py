from config import SELECTORS


def extract_elements(page, screen_name, repo):

    if screen_name not in repo["pages"]:
        repo["pages"][screen_name] = []

    elements = []

    for s in SELECTORS:
        elements.extend(
            page.query_selector_all(s)
        )

    print(
        f"[{screen_name}] Found {len(elements)}"
    )

    for idx, el in enumerate(elements):

        try:

            box = el.bounding_box()

            if not box:
                continue

            if box["width"] < 5:
                continue

            tag = el.evaluate(
                "e => e.tagName.toLowerCase()"
            )

            el_info = {
                "name": f"{tag}_{idx}",
                "tag": tag,
                "text": el.inner_text()
                if tag != "input"
                else "",
                "type": el.get_attribute("type"),
                "id": el.get_attribute("id"),
                "class": el.get_attribute("class"),
                "role": el.get_attribute("role"),
                "aria_label": el.get_attribute(
                    "aria-label"
                ),
                "box": box,
            }

            repo["pages"][screen_name].append(
                el_info
            )

        except Exception:
            pass