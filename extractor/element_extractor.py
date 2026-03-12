from extractor.control_detector import detect_control
from extractor.label_utils import get_label_text


class ElementExtractor:

    def __init__(self, repo):
        self.repo = repo

    def extract(self, page, screen_name):

        selectors = [
            "input:not([type='hidden'])",
            "textarea",
            "select",
            "button",
            "a",
            "[role='button']",
            "[aria-label]",
            "[tabindex]",
        ]

        if screen_name not in self.repo["pages"]:
            self.repo["pages"][screen_name] = []

        elements = []

        for s in selectors:
            for el in page.query_selector_all(s):
                elements.append((el, s))

        for idx, (el, sel) in enumerate(elements):

            try:

                box = el.bounding_box()

                if not box:
                    continue

                tag = el.evaluate(
                    "e => e.tagName.toLowerCase()"
                )

                el_type = el.get_attribute("type")
                role = el.get_attribute("role")

                control_type = detect_control(
                    tag,
                    el_type,
                    role,
                    el
                )

                info = {

                    "name": f"{tag}_{idx}",
                    "control_type": control_type,
                    "selector": sel,
                    "box": box,
                }

                self.repo["pages"][screen_name].append(
                    info
                )

            except:
                pass