# PyRPAx-Framework

PyRPAx-Framework is a lightweight Python toolkit for capturing UI structure and visual state of web pages to support Robotic Process Automation (RPA) workflows, UI analysis, and automated element extraction. It uses Playwright for browser control, extracts structural and accessibility information about interactive elements, records screenshots, annotates them, and writes structured JSON output describing pages and controls.

This README documents the repository layout, explains the purpose of each script and module, and shows how to run the main capture flow and example scripts.

Status
------
Prototype / early-stage — functional scripts for DOM inspection and screenshot/annotation. Contributions, bug reports and improvements are welcome.

Quick summary
-------------
- Main capture flow: `main.py` — run a Playwright browser, observe DOM changes and network events, extract interactive elements, save JSON describing pages and controls, take screenshots and annotate them.
- Core browser control: `core/browser_manager.py` — starts Playwright and returns a page/context.
- Extraction: `extractor/` — element detection, control-type heuristics and label helpers.
- Storage: `repository/json_storage.py` — writes output JSON after de-duplication.
- Screenshot/annotation: `screenshot/` — take screenshots and draw element annotations.
- Example (Selenium): `simple_design/main.py` — simple page object usage for reference.
- Helpers and utilities: `utils/`, `common/` and additional scripts such as `dom_parsing.py`.

Repository structure
--------------------
PyRPAx-Framework/
- .github/                — CI / issue templates (if present)
- common/                 — common utilities (logger, etc.)
- core/
  - browser_manager.py    — Playwright start-up wrapper (provides page & context)
- extractor/
  - element_extractor.py  — enumerates interactive elements and captures attributes
  - control_detector.py   — heuristics to map tags/attributes to control types
  - label_utils.py        — helper to find label text for elements
- repository/
  - json_filter.py        — (de-)duplication helpers for repository data
  - json_storage.py       — persists repository JSON into output/
- screenshot/
  - screenshot_service.py — take screenshots of pages
  - draw_annotator.py     — draw boxes/annotations for discovered elements
- simple_design/
  - main.py               — short Selenium-based example using a Page Object
- dom_parsing.py          — utility script related to DOM parsing (extra helpers)
- main.py                 — main capture workflow (Playwright-based)
- requirements.txt        — runtime dependencies
- env.txt                 — sample environment variables / notes
- ProjectPlan.md          — notes / project plan
- README.md               — (this file)

Files and purpose (detailed)
----------------------------

main.py
- Entry point for the Playwright capture workflow.
- Usage: `python main.py <url>`
- What it does:
  - Starts a Playwright browser via `core.browser_manager.BrowserManager`.
  - Creates extractor, storage, screenshot and annotation service instances:
    - `ElementExtractor(repo)` — scans for elements and saves attributes to `repo`.
    - `JsonStorage()` — writes the filtered JSON to `output/<base_name>.json`.
    - `ScreenshotService()` — captures screenshots for each observed page state.
    - `DrawAnnotator(base_name, repo)` — creates annotated screenshots for discovered elements.
  - Installs a DOM MutationObserver inside the page (via `page.evaluate`) that calls a Python-exposed function `notify_dom_change` with debounce logic.
  - Registers listeners:
    - `framenavigated` — triggers extraction on main-frame navigation.
    - `response` — triggers extraction for XHR/fetch responses.
    - `domcontentloaded` — lightweight trigger for DOM updates.
  - Extraction includes scanning main page and iframes, storing element metadata and taking screenshots. Screenshots and JSON files are produced per captured screen state.

core/browser_manager.py
- Minimal Playwright wrapper:
  - `start()` -> starts Playwright, launches chromium (headless set to False by default), creates a context and a page, and returns `(page, context)`.
- Adjust if you want headless operation or extra launch options.

extractor/element_extractor.py
- Collects interactive elements using a set of CSS selectors (inputs, textarea, select, button, anchor, ARIA roles, data attributes, tabindex, etc.).
- For each element it captures:
  - bounding box (position & size)
  - tag, type, id, name attribute, placeholder, autocomplete, title, aria-label, class, data attributes, label (found via label_utils)
  - computed control type via `control_detector.detect_control(tag, type, role, element)`
  - a normalized selector string via `normalize_selector`, currently transforming `input:not([type='hidden'])` into a consistent format like `input([type='hidden'])`.
- Extracted element records are stored in a `repo["pages"][screen_name]` list and later saved to JSON.

extractor/control_detector.py
- Contains heuristics to infer a control type (e.g., text input, button, link, checkbox, radio, select, etc.) based on element tag, type attribute, role and other characteristics.
- Used by ElementExtractor to add a human-friendly `control_type` to each element's metadata.

extractor/label_utils.py
- Helpers to locate a label for a given element (searches for `<label for="...">`, parent label, aria-label, etc.) and return best-guess label text.

repository/json_filter.py
- Functions to detect and remove duplicate or redundant element entries before saving final JSON. This keeps output compact and consistent across repeated captures.

repository/json_storage.py
- `JsonStorage.save(repo, base_name)`:
  - Calls `filter_duplicate_elements` to clean the repo structure.
  - Ensures `output/` directory exists.
  - Writes `output/<base_name>.json` containing the full `repo` object (pages, elements, base_url).
  - Prints the saved path.

screenshot/screenshot_service.py
- Responsible for taking screenshots of the page for each captured screen version.
- Called from `main.py` as `screenshot.take(page, base_name, versioned_name)`.

screenshot/draw_annotator.py
- Uses the stored `repo` information to draw annotations (bounding boxes, labels, IDs) on screenshots so you can visually inspect discovered elements.
- `annotator.draw_all()` is called at the end of `main.py` to annotate the final capture set.

simple_design/main.py
- A minimal Selenium example demonstrating a Page Object pattern:
  - Creates a Chrome webdriver, navigates to a login URL, and uses a `LoginPage` helper to interact with UI fields.
- Useful as a reference for how tests or automations might be structured. Not directly part of the Playwright capture flow but helpful for comparisons and design examples.

dom_parsing.py
- Contains DOM parsing utilities and helpers (auxiliary processing of DOM/HTML when needed).

Requirements & setup
--------------------
- Python 3.8+
- Playwright (sync API) is used in the main capture flow. Install and set up Playwright browsers if you use `main.py`.
  - Typical install:
    ```bash
    pip install -r requirements.txt
    ```
    (If `requirements.txt` lists Playwright, run `playwright install` afterward to install browser binaries.)
- For the Selenium example in `simple_design/`, you will need Selenium and an appropriate WebDriver (e.g., chromedriver) on PATH.

Running the main capture flow
-----------------------------
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate     # macOS / Linux
   .\.venv\Scripts\activate      # Windows
   pip install -r requirements.txt
