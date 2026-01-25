from playwright.sync_api import sync_playwright
import logging
from datetime import datetime

# -------------------------------
# LOGGING CONFIGURATION
# -------------------------------
logging.basicConfig(
    filename="project_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create execution header in log file
logging.info("\n" + "="*50)
logging.info(f"NEW EXECUTION STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logging.info("="*50 + "\n")

logging.info("Program started")


def run():
    with sync_playwright() as p:
        logging.info("Launching browser")

        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
            )
        
        context = browser.new_context(viewport=None)  # Disable default viewport

        page = context.new_page()

        # Increase default timeout to avoid timeout errors
        page.set_default_timeout(60000)

        #url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
        url = "https://www.bbc.com/news/technology"
        logging.info(f"Opening website: {url}")

        page.goto(url)

        # Wait until main content loads (not network idle)
        #page.wait_for_load_state("body")
        #page.wait_for_selector("body")

        logging.info("Page loaded successfully")

        # -------------------------------
        # METADATA EXTRACTION (SAFE)
        # -------------------------------

        # Page Title
        title = page.title()
        logging.info("Page title extracted")
        print(title)

        # Meta Description (safe extraction)
        try:
            description = page.locator("meta[name='description']").get_attribute("content")
        except:
            try:
                description = page.locator("meta[property='og:description']").get_attribute("content")
            except:
                description = "Description not found"
        logging.info("Meta description extracted")
        print(description)

        # Meta Keywords (safe extraction)
        try:
            keywords = page.locator("meta[name='keywords']").get_attribute("content")
        except:
            keywords = "Keywords not found"
        logging.info("Meta keywords extracted")
        print(keywords)

        # -------------------------------
        # CONTENT EXTRACTION
        # -------------------------------

        main_heading = page.locator("h1").inner_text()
        logging.info("Main heading extracted")
        print(main_heading)

        first_paragraph = page.locator("p").first.inner_text()
        logging.info("First paragraph extracted")
        print(first_paragraph)

        links_count = page.locator("a").count()
        logging.info("Links count extracted")
        print(links_count)

        extraction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(extraction_time)

        # -------------------------------
        # SAVE DATA TO TEXT FILE
        # -------------------------------

        logging.info("Writing data to text file")

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

        logging.info("Data successfully saved to metadata_report.txt")

        page.wait_for_timeout(5000)
        browser.close()
        logging.info("Browser closed")

  
if __name__ == "__main__":
    run()
    logging.info("Program finished successfully")
