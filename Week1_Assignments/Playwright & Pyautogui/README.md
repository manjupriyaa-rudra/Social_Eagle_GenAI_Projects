# Metadata Extraction & Gmail Automation - README

## Project Purpose

This project combines **web page metadata extraction** using Playwright with **Gmail email automation** using pyautogui. The workflow is designed so that you first extract metadata and content from a web page and save it as a report, then trigger sending that report via Gmail.

Workflow Steps

## Metadata extraction

1. Open the browser and navigate to the target web page.
2. Extract the following data:
    Page title
    Meta description
    Meta keywords
    Main heading (h1)
    First paragraph
    Total links on the page
3. Save all extracted data to metadata_report.txt.
4. Log all actions in project_log.log.
5. Output: A ready-to-send report file with all the necessary metadata and content.

## GMAIL Automation

1. After the metadata report is ready, run the Gmail automation script.
2. Opens Gmail in the default browser.
3. Automatically fills in the recipient email, subject, and body.
4. Attaches the metadata_report.txt file via the system file dialog.
5. Sends the email.
Note: Ensure the attachment dialog is focused and coordinates are correctly set for your screen resolution.

## Expected Output

1. metadata_report.txt containing structured metadata and page content.
2. project_log.log with detailed execution steps.
3. Gmail email sent to the configured recipient with the report attached.
4. Console prints of extracted data and extraction timestamp.

## Functions Used

Playwright (sync API): For browser automation and web page content extraction.

Logging: To record execution steps and timestamps.

datetime: For timestamps in logs and reports.

PyAutoGUI: To automate Gmail email composition and file attachment.

pyperclip: For safe copy-paste of text.

webbrowser: To open Gmail in the default browser.

os & time: File existence checks and delays to ensure smooth execution.