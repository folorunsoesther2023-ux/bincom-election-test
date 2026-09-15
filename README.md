# Bincom Election Result Viewer

A basic programming test solution for Bincom's Preliminary Online Interview — built with **Python (Flask)** and **SQLite**, using data converted from the provided `bincom_test.sql` dummy election database.

**Live demo:** https://estherr.pythonanywhere.com

## About

The database contains dummy 2011 election results for polling units, wards, and LGAs within Delta State (state ID: 25). Each polling unit's results are stored across multiple rows in `announced_pu_results` (one row per party).

This app answers the three required questions:

### Question 1 — Polling Unit Result
Displays the result for any individual polling unit, selected via a chained combo box (LGA → Ward → Polling Unit).

### Question 2 — LGA Summed Result
Displays the summed total result of all polling units under a selected local government. Local Government is chosen using a select box. Totals are calculated directly from `announced_pu_results` (not from the pre-announced `announced_lga_results` table, which is reserved for comparison purposes).

### Question 3 — Add New Result
A form to store results for all parties for a new polling unit.

## Tech Stack
- Python 3 / Flask
- SQLite (converted from the provided MySQL dump)
- HTML/CSS (server-rendered templates)
- Hosted on PythonAnywhere

## Project Structure
```
bincom_app/
├── app.py              # Flask application and routes
├── templates/           # HTML templates
├── static/               # CSS/JS assets
└── bincom_test.db      # SQLite database
```

## Running Locally
```bash
pip install flask
python app.py
```
Then visit `http://localhost:5000` in your browser.

## Author
Esther — submitted as part of the Bincom Preliminary Online Interview Test.
