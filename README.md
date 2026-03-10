# Playwright Object Repository Generator

This project is a modular Playwright-based automation tool that
automatically extracts UI elements from web pages and builds an Object
Repository in JSON format. It also captures screenshots of each visited
page.

## Features

-   Works with Chromium, Firefox, WebKit
-   Auto navigation detection
-   Screenshot for each page
-   JSON repository per site
-   Stops when browser closed
-   Modular architecture

## Structure

project/ main.py config.py core/ output/ screenshots/

## Usage

python main.py https://example.com
