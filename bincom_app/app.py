"""
Bincom Election Result Viewer
-----------------------------
A basic Flask app answering the Bincom Preliminary Online Interview Test
(Basic Programming Test: Python track).

Q1: View results for a single polling unit (chained LGA -> Ward -> Polling Unit selects)
Q2: View summed total result for all polling units under a selected LGA
Q3: Form to store results for ALL parties for a new polling unit

Database: bincom.db (SQLite version of the supplied bincom_test.sql)
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bincom.db")

app = Flask(__name__)
app.secret_key = "bincom-test-secret-key"  # only needed for flash messages


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return render_template("home.html")


# ---------------------------------------------------------------------
# QUESTION 1: Result for an individual polling unit (chained selects)
# ---------------------------------------------------------------------
@app.route("/polling-unit-result", methods=["GET"])
def polling_unit_result():
    conn = get_db()

    # LGA dropdown (state is fixed to Delta / state_id 25, so we skip a state select)
    lgas = conn.execute(
        "SELECT lga_id, lga_name FROM lga ORDER BY lga_name"
    ).fetchall()

    selected_lga = request.args.get("lga_id", type=int)
    selected_ward = request.args.get("ward_id", type=int)
    selected_pu = request.args.get("polling_unit_uniqueid", type=int)

    wards = []
    polling_units = []
    results = []
    pu_info = None

    if selected_lga:
        wards = conn.execute(
            "SELECT ward_id, ward_name FROM ward WHERE lga_id = ? ORDER BY ward_name",
            (selected_lga,),
        ).fetchall()

    if selected_lga and selected_ward:
        polling_units = conn.execute(
            """SELECT uniqueid, polling_unit_name, polling_unit_number
               FROM polling_unit
               WHERE lga_id = ? AND ward_id = ?
               ORDER BY polling_unit_name""",
            (selected_lga, selected_ward),
        ).fetchall()

    if selected_pu:
        pu_info = conn.execute(
            "SELECT * FROM polling_unit WHERE uniqueid = ?", (selected_pu,)
        ).fetchone()
        results = conn.execute(
            """SELECT party_abbreviation, party_score
               FROM announced_pu_results
               WHERE polling_unit_uniqueid = ?
               ORDER BY party_score DESC""",
            (str(selected_pu),),
        ).fetchall()

    conn.close()
    return render_template(
        "polling_unit_result.html",
        lgas=lgas,
        wards=wards,
        polling_units=polling_units,
        selected_lga=selected_lga,
        selected_ward=selected_ward,
        selected_pu=selected_pu,
        pu_info=pu_info,
        results=results,
    )


# ---------------------------------------------------------------------
# QUESTION 2: Summed total result for all polling units under an LGA
# ---------------------------------------------------------------------
@app.route("/lga-summed-result", methods=["GET"])
def lga_summed_result():
    conn = get_db()

    lgas = conn.execute(
        "SELECT lga_id, lga_name FROM lga ORDER BY lga_name"
    ).fetchall()

    selected_lga = request.args.get("lga_id", type=int)
    lga_name = None
    summed_results = []

    if selected_lga:
        lga_row = conn.execute(
            "SELECT lga_name FROM lga WHERE lga_id = ?", (selected_lga,)
        ).fetchone()
        lga_name = lga_row["lga_name"] if lga_row else None

        # Sum party_score from announced_pu_results for every polling unit
        # that belongs to the selected LGA (per the test: do NOT use
        # announced_lga_results table for this).
        summed_results = conn.execute(
            """SELECT apr.party_abbreviation, SUM(apr.party_score) AS total_score
               FROM announced_pu_results apr
               JOIN polling_unit pu ON pu.uniqueid = CAST(apr.polling_unit_uniqueid AS INTEGER)
               WHERE pu.lga_id = ?
               GROUP BY apr.party_abbreviation
               ORDER BY total_score DESC""",
            (selected_lga,),
        ).fetchall()

    conn.close()
    return render_template(
        "lga_summed_result.html",
        lgas=lgas,
        selected_lga=selected_lga,
        lga_name=lga_name,
        summed_results=summed_results,
    )


# ---------------------------------------------------------------------
# QUESTION 3: Store results for ALL parties for a new polling unit
# ---------------------------------------------------------------------
@app.route("/new-polling-unit-result", methods=["GET", "POST"])
def new_polling_unit_result():
    conn = get_db()
    parties = conn.execute("SELECT partyid, partyname FROM party ORDER BY partyname").fetchall()
    polling_units = conn.execute(
        "SELECT uniqueid, polling_unit_name FROM polling_unit ORDER BY polling_unit_name"
    ).fetchall()

    if request.method == "POST":
        pu_id = request.form.get("polling_unit_uniqueid")
        entered_by = request.form.get("entered_by_user", "Anonymous")

        if not pu_id:
            flash("Please select a polling unit.", "error")
            return redirect(url_for("new_polling_unit_result"))

        rows_to_insert = []
        for party in parties:
            score = request.form.get(f"score_{party['partyid']}", "").strip()
            if score == "":
                continue
            try:
                score_int = int(score)
            except ValueError:
                flash(f"Score for {party['partyname']} must be a number.", "error")
                return redirect(url_for("new_polling_unit_result"))
            rows_to_insert.append((pu_id, party["partyid"], score_int, entered_by))

        if not rows_to_insert:
            flash("Please enter at least one party score.", "error")
            return redirect(url_for("new_polling_unit_result"))

        next_id_row = conn.execute(
            "SELECT COALESCE(MAX(result_id), 0) + 1 AS next_id FROM announced_pu_results"
        ).fetchone()
        next_id = next_id_row["next_id"]

        insert_rows = []
        for i, r in enumerate(rows_to_insert):
            insert_rows.append((next_id + i, r[0], r[1], r[2], r[3], request.remote_addr))

        conn.executemany(
            """INSERT INTO announced_pu_results
               (result_id, polling_unit_uniqueid, party_abbreviation, party_score, entered_by_user, date_entered, user_ip_address)
               VALUES (?, ?, ?, ?, ?, datetime('now'), ?)""",
            insert_rows,
        )
        conn.commit()
        conn.close()
        flash("Results saved successfully!", "success")
        return redirect(url_for("new_polling_unit_result"))

    conn.close()
    return render_template(
        "new_polling_unit_result.html", parties=parties, polling_units=polling_units
    )


if __name__ == "__main__":
    app.run(debug=True)
