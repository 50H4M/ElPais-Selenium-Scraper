# El País Web Scraper & Cross-Browser Automation

## Overview
This project is a technical demonstration of web scraping, API integration, text processing, and parallel cloud execution. It uses Python and Selenium to scrape the Opinion section of the Spanish news outlet, El País, translates the article headers to English, analyzes word frequencies, and validates cross-browser compatibility using BrowserStack.

## Features
* **Web Scraping:** Navigates to El País, accepts cookies, and extracts the title, content, and cover image of the first five Opinion articles.
* **API Integration:** Uses `deep-translator` (Google Translate API wrapper) to translate Spanish headers into English.
* **Text Processing:** Analyzes the translated headers to identify and count words repeated more than twice.
* **Cross-Browser Testing:** Executes parallel automated sessions across 5 distinct environments (Windows/Chrome, Mac/Safari, Windows/Firefox, iOS/Safari, Android/Chrome) using BrowserStack.

## Prerequisites
* Python 3.x
* A BrowserStack account (for cloud execution)

## Installation
1. Clone the repository:
   ```bash
  git clone https://github.com/50H4M/ElPais-Selenium-Scraper.git
   cd ElPais-Selenium-Scraper
