# Bincom Election Result Viewer

A basic Flask app answering the Bincom Preliminary Online Interview Test
(Python track, beginner level).

## What's included
- `app.py` — the Flask application (3 routes, one per question)
- `templates/` — HTML pages (chained select boxes, results tables, entry form)
- `bincom.db` — SQLite database, converted from the supplied `bincom_test.sql`
  so the whole thing runs from a single file with no separate database
  server needed
- `requirements.txt` — just Flask

## What each page does
- **Q1 — `/polling-unit-result`**: Chained combo boxes (LGA → Ward →
  Polling Unit) that reveal the next dropdown once the previous one is
  picked, then shows that polling unit's results.
- **Q2 — `/lga-summed-result`**: Pick an LGA from a select box; the page
  sums `party_score` from `announced_pu_results` for every polling unit
  under that LGA (NOT from `announced_lga_results`, per the test's
  instructions) and displays the totals per party.
- **Q3 — `/new-polling-unit-result`**: A form to enter scores for all
  parties for a polling unit and save them into `announced_pu_results`.

## Running it locally
```bash
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000 in your browser.

## Deploying it (needed for Step 2 of the test — "upload your solution to
temporary hosting")

**Easiest option: PythonAnywhere (free tier)**
1. Create a free account at https://www.pythonanywhere.com
2. Go to the **Files** tab and upload `app.py`, `bincom.db`, and the
   `templates` folder (keep the same folder structure)
3. Go to the **Web** tab → **Add a new web app** → choose **Flask** →
   pick the Python version shown in your dashboard
4. When it asks for your Flask app's path, point it at your uploaded
   `app.py`
5. Click **Reload** on the Web tab — your app is now live at
   `https://yourusername.pythonanywhere.com`

**Alternative: Render.com**
1. Push this folder to a new GitHub repository
2. On Render, create a new **Web Service**, connect the repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python app.py` (or `gunicorn app:app` if you add
   gunicorn to requirements.txt)
5. Render gives you a live URL once deployed

## For the submission form
You'll need:
1. The live link to your deployed app (from PythonAnywhere or Render)
2. A link to your code — push this folder to a GitHub repository
   (public or with view access) and use that repo link
