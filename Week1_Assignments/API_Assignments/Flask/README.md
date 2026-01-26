# Personalized Quote Generator

**Framework:** This application is built using the **Flask** web framework for Python.

A simple Flask web application that delivers **daily personalized quotes** in different categories: Power, Push, and Super Energizer. Each user receives a consistent quote for the day based on the date.

---

## Features

- Generates daily quotes based on the current date (same quote every day for consistency).  
- Three categories of quotes:
  - **Power Quotes** – motivational and discipline-focused.
  - **Push Quotes** – encouragement to take action and make progress.
  - **Super Energizer Quotes** – boost confidence and courage.  
- Personalized by user name via query parameter.  
- Returns quotes in JSON format for easy integration with other apps or frontends.

---

## Output

- When a request is made to the `/quote` endpoint, the API returns a **JSON object** containing:
  - **team** – the team name (Social Eagle Batch 5)
  - **category** – the type of quote returned (Power, Push, or Super Energizer)
  - **quote** – the personalized quote including the user's name  

**Example Response:**

```json
{
  "team": "Social Eagle Batch 5",
  "category": "Power Quote",
  "quote": "Alice, keep leading with discipline and consistency."
}
