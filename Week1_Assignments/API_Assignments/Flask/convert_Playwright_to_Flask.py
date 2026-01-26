from flask import Flask, jsonify
from playwright.sync_api import sync_playwright
import logging
from datetime import datetime

app = Flask(__name__)

# -------------------------------
# LOGGING CONFIGURATION
# -------------------------------
logging.basicConfig(
    filename="project_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("\n" + "="*50)
logging.info(f"NEW EXECUTION STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logging.info("="*50 + "\n")
logging.info("Flask Program started")


def extract_metadata():
    with sync_playwright() as p:
        logging.info("Launching browser")

        browser = p.chromium.launch(
            headless=True,
            args=["--start-maximized"]
        )

        context = browser.new_context(viewport=None)
        page = context.new_page()
        page.set_default_timeout(60000)

        url = "https://www.bbc.com/news/technology"
        logging.info(f"Opening website: {url}")
        page.goto(url)

        logging.info("Page loaded successfully")

        # -------------------------------
        # METADATA EXTRACTION
        # -------------------------------
        title = page.title()

        try:
            description = page.locator("meta[name='description']").get_attribute("content")
        except:
            try:
                description = page.locator("meta[property='og:description']").get_attribute("content")
            except:
                description = "Description not found"

        try:
            keywords = page.locator("meta[name='keywords']").get_attribute("content")
        except:
            keywords = "Keywords not found"

        main_heading = page.locator("h1").inner_text()
        first_paragraph = page.locator("p").first.inner_text()
        links_count = page.locator("a").count()

        extraction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # -------------------------------
        # SAVE DATA TO FILE
        # -------------------------------
        with open("metadata_report.txt", "w", encoding="utf-8") as file:
            file.write("WEB PAGE RESEARCH REPORT\n")
            file.write("=========================\n\n")
            file.write(f"URL: {url}\n")
            file.write(f"Extraction Time: {extraction_time}\n\n")
            file.write("METADATA\n")
            file.write("--------\n")
            file.write(f"Title: {title}\n")
            file.write(f"Description: {description}\n")
            file.write(f"Keywords: {keywords}\n\n")
            file.write("CONTENT DATA\n")
            file.write("------------\n")
            file.write(f"Main Heading: {main_heading}\n\n")
            file.write(f"First Paragraph:\n{first_paragraph}\n\n")
            file.write(f"Total Links on Page: {links_count}\n")

        browser.close()
        logging.info("Browser closed")

        return {
            "url": url,
            "extraction_time": extraction_time,
            "title": title,
            "description": description,
            "keywords": keywords,
            "main_heading": main_heading,
            "first_paragraph": first_paragraph,
            "total_links": links_count
        }


# -------------------------------
# FLASK ROUTE
# -------------------------------
@app.route("/extract", methods=["GET"])
def extract():
    try:
        data = extract_metadata()
        return jsonify({
            "status": "success",
            "data": data
        })
    except Exception as e:
        logging.error(str(e))
        return jsonify({
            "status": "failure",
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True)