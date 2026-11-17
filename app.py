
import json
import os

from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db_connection
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-development-only-key")

STATUSES = [
    "Applied", "Screening", "Interview",
    "Offer", "Rejected", "Withdrawn"
]


# ---------------- HELPERS ----------------

def get_skills(value):
    if not value:
        return []
    if isinstance(value, str):
        return json.loads(value)
    return value


# ---------------- DASHBOARD ----------------

@app.route("/")
def dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        counts = {}

        for table in ("companies", "jobs", "applications", "contacts"):
            cursor.execute(f"SELECT COUNT(*) AS total FROM {table}")
            counts[table] = cursor.fetchone()["total"]

        return render_template("dashboard.html", **counts)
    finally:
        cursor.close()
        connection.close()


# ---------------- COMPANIES CRUD ----------------

@app.route("/companies")
def companies():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM companies ORDER BY company_name")
        company_list = cursor.fetchall()
        return render_template("companies.html", companies=company_list)
    finally:
        cursor.close()
        connection.close()


@app.route("/companies/add", methods=["POST"])
def add_company():
    name = request.form.get("company_name", "").strip()

    if not name:
        flash("Company name is required.", "error")
        return redirect(url_for("companies"))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO companies
            (company_name, industry, website, city, state, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            name,
            request.form.get("industry"),
            request.form.get("website"),
            request.form.get("city"),
            request.form.get("state"),
            request.form.get("notes")
        ))
        connection.commit()
        flash("Company added successfully!", "success")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("companies"))


@app.route("/companies/edit/<int:company_id>", methods=["GET", "POST"])
def edit_company(company_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        if request.method == "POST":
            name = request.form.get("company_name", "").strip()

            if not name:
                flash("Company name is required.", "error")
                return redirect(url_for("edit_company", company_id=company_id))

            cursor.execute("""
                UPDATE companies
                SET company_name=%s, industry=%s, website=%s,
                    city=%s, state=%s, notes=%s
                WHERE company_id=%s
            """, (
                name,
                request.form.get("industry"),
                request.form.get("website"),
                request.form.get("city"),
                request.form.get("state"),
                request.form.get("notes"),
                company_id
            ))
            connection.commit()
            flash("Company updated successfully!", "success")
            return redirect(url_for("companies"))

        cursor.execute(
            "SELECT * FROM companies WHERE company_id=%s",
            (company_id,)
        )
        company = cursor.fetchone()

        if not company:
            return "Company not found", 404

        return render_template("edit_company.html", company=company)
    finally:
        cursor.close()
        connection.close()


@app.route("/companies/delete/<int:company_id>", methods=["POST"])
def delete_company(company_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM companies WHERE company_id=%s",
            (company_id,)
        )
        connection.commit()
        flash("Company deleted successfully!", "success")
    except Error:
        connection.rollback()
        flash("Cannot delete a company linked to jobs or contacts.", "error")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("companies"))


# ---------------- JOBS CRUD ----------------

@app.route("/jobs")
def jobs():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT j.*, c.company_name
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.company_id
            ORDER BY j.job_id DESC
        """)
        job_list = cursor.fetchall()

        cursor.execute("""
            SELECT company_id, company_name
            FROM companies ORDER BY company_name
        """)
        company_list = cursor.fetchall()

        return render_template(
            "jobs.html", jobs=job_list, companies=company_list
        )
    finally:
        cursor.close()
        connection.close()


@app.route("/jobs/add", methods=["POST"])
def add_job():
    title = request.form.get("job_title", "").strip()
    company_id = request.form.get("company_id", "").strip()

    if not title or not company_id:
        flash("Job title and company are required.", "error")
        return redirect(url_for("jobs"))

    skills = [
        skill.strip()
        for skill in request.form.get("requirements", "").split(",")
        if skill.strip()
    ]

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO jobs
            (company_id, job_title, job_type, salary_min,
             salary_max, job_url, date_posted, requirements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            company_id,
            title,
            request.form.get("job_type") or None,
            request.form.get("salary_min") or None,
            request.form.get("salary_max") or None,
            request.form.get("job_url") or None,
            request.form.get("date_posted") or None,
            json.dumps(skills)
        ))
        connection.commit()
        flash("Job added successfully!", "success")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("jobs"))


@app.route("/jobs/edit/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        if request.method == "POST":
            title = request.form.get("job_title", "").strip()
            company_id = request.form.get("company_id", "").strip()

            if not title or not company_id:
                flash("Job title and company are required.", "error")
                return redirect(url_for("edit_job", job_id=job_id))

            skills = [
                skill.strip()
                for skill in request.form.get("requirements", "").split(",")
                if skill.strip()
            ]

            cursor.execute("""
                UPDATE jobs
                SET company_id=%s, job_title=%s, job_type=%s,
                    salary_min=%s, salary_max=%s, job_url=%s,
                    date_posted=%s, requirements=%s
                WHERE job_id=%s
            """, (
                company_id,
                title,
                request.form.get("job_type") or None,
                request.form.get("salary_min") or None,
                request.form.get("salary_max") or None,
                request.form.get("job_url") or None,
                request.form.get("date_posted") or None,
                json.dumps(skills),
                job_id
            ))
            connection.commit()
            flash("Job updated successfully!", "success")
            return redirect(url_for("jobs"))

        cursor.execute("SELECT * FROM jobs WHERE job_id=%s", (job_id,))
        job = cursor.fetchone()

        if not job:
            return "Job not found", 404

        cursor.execute("""
            SELECT company_id, company_name
            FROM companies ORDER BY company_name
        """)
        company_list = cursor.fetchall()

        job["skills_text"] = ", ".join(get_skills(job["requirements"]))

        return render_template(
            "edit_job.html", job=job, companies=company_list
        )
    finally:
        cursor.close()
        connection.close()


@app.route("/jobs/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM jobs WHERE job_id=%s", (job_id,))
        connection.commit()
        flash("Job deleted successfully!", "success")
    except Error:
        connection.rollback()
        flash("Cannot delete a job linked to an application.", "error")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("jobs"))


# ---------------- APPLICATIONS CRUD ----------------

@app.route("/applications")
def applications():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT a.*, j.job_title, c.company_name
            FROM applications a
            LEFT JOIN jobs j ON a.job_id = j.job_id
            LEFT JOIN companies c ON j.company_id = c.company_id
            ORDER BY a.application_date DESC, a.application_id DESC
        """)
        application_list = cursor.fetchall()

        cursor.execute("""
            SELECT j.job_id, j.job_title, c.company_name
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.company_id
            ORDER BY c.company_name, j.job_title
        """)
        job_list = cursor.fetchall()

        return render_template(
            "applications.html",
            applications=application_list,
            jobs=job_list,
            statuses=STATUSES
        )
    finally:
        cursor.close()
        connection.close()


@app.route("/applications/add", methods=["POST"])
def add_application():
    job_id = request.form.get("job_id", "").strip()
    application_date = request.form.get("application_date", "").strip()
    status = request.form.get("status", "Applied")

    if not job_id or not application_date or status not in STATUSES:
        flash("Please enter a job, date, and valid status.", "error")
        return redirect(url_for("applications"))

    interview_data = json.dumps({
        "notes": request.form.get("interview_notes", "").strip()
    })

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO applications
            (job_id, application_date, status, resume_version,
             cover_letter_sent, interview_data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            job_id,
            application_date,
            status,
            request.form.get("resume_version") or None,
            1 if request.form.get("cover_letter_sent") else 0,
            interview_data
        ))
        connection.commit()
        flash("Application added successfully!", "success")
    except Error:
        connection.rollback()
        flash("Could not add application.", "error")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("applications"))


@app.route("/applications/edit/<int:application_id>", methods=["GET", "POST"])
def edit_application(application_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        if request.method == "POST":
            job_id = request.form.get("job_id", "").strip()
            application_date = request.form.get("application_date", "").strip()
            status = request.form.get("status", "Applied")

            if not job_id or not application_date or status not in STATUSES:
                flash("Please enter a job, date, and valid status.", "error")
                return redirect(url_for(
                    "edit_application", application_id=application_id
                ))

            interview_data = json.dumps({
                "notes": request.form.get("interview_notes", "").strip()
            })

            try:
                cursor.execute("""
                    UPDATE applications
                    SET job_id=%s, application_date=%s, status=%s,
                        resume_version=%s, cover_letter_sent=%s,
                        interview_data=%s
                    WHERE application_id=%s
                """, (
                    job_id,
                    application_date,
                    status,
                    request.form.get("resume_version") or None,
                    1 if request.form.get("cover_letter_sent") else 0,
                    interview_data,
                    application_id
                ))
                connection.commit()
                flash("Application updated successfully!", "success")
                return redirect(url_for("applications"))
            except Error:
                connection.rollback()
                flash("Could not update application.", "error")
                return redirect(url_for(
                    "edit_application", application_id=application_id
                ))

        cursor.execute("""
            SELECT * FROM applications WHERE application_id=%s
        """, (application_id,))
        application = cursor.fetchone()

        if not application:
            return "Application not found", 404

        cursor.execute("""
            SELECT j.job_id, j.job_title, c.company_name
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.company_id
            ORDER BY c.company_name, j.job_title
        """)
        job_list = cursor.fetchall()

        interview_data = application["interview_data"]

        if isinstance(interview_data, str):
            interview_data = json.loads(interview_data)

        application["interview_notes"] = (
            interview_data or {}
        ).get("notes", "")

        return render_template(
            "edit_application.html",
            application=application,
            jobs=job_list,
            statuses=STATUSES
        )
    finally:
        cursor.close()
        connection.close()


@app.route("/applications/delete/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            DELETE FROM applications WHERE application_id=%s
        """, (application_id,))
        connection.commit()
        flash("Application deleted successfully!", "success")
    except Error:
        connection.rollback()
        flash("Could not delete application.", "error")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("applications"))


# ---------------- CONTACTS CRUD ----------------

@app.route("/contacts")
def contacts():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT ct.*, c.company_name
            FROM contacts ct
            LEFT JOIN companies c ON ct.company_id = c.company_id
            ORDER BY ct.contact_name
        """)
        contact_list = cursor.fetchall()

        cursor.execute("""
            SELECT company_id, company_name
            FROM companies ORDER BY company_name
        """)
        company_list = cursor.fetchall()

        return render_template(
            "contacts.html",
            contacts=contact_list,
            companies=company_list
        )
    finally:
        cursor.close()
        connection.close()


@app.route("/contacts/add", methods=["POST"])
def add_contact():
    name = request.form.get("contact_name", "").strip()
    company_id = request.form.get("company_id", "").strip()

    if not name or not company_id:
        flash("Contact name and company are required.", "error")
        return redirect(url_for("contacts"))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO contacts
            (company_id, contact_name, title, email,
             phone, linkedin_url, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            company_id,
            name,
            request.form.get("title") or None,
            request.form.get("email") or None,
            request.form.get("phone") or None,
            request.form.get("linkedin_url") or None,
            request.form.get("notes") or None
        ))
        connection.commit()
        flash("Contact added successfully!", "success")
    except Error:
        connection.rollback()
        flash("Could not add contact.", "error")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("contacts"))


@app.route("/contacts/edit/<int:contact_id>", methods=["GET", "POST"])
def edit_contact(contact_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        if request.method == "POST":
            name = request.form.get("contact_name", "").strip()
            company_id = request.form.get("company_id", "").strip()

            if not name or not company_id:
                flash("Contact name and company are required.", "error")
                return redirect(url_for(
                    "edit_contact", contact_id=contact_id
                ))

            try:
                cursor.execute("""
                    UPDATE contacts
                    SET company_id=%s, contact_name=%s, title=%s,
                        email=%s, phone=%s, linkedin_url=%s, notes=%s
                    WHERE contact_id=%s
                """, (
                    company_id,
                    name,
                    request.form.get("title") or None,
                    request.form.get("email") or None,
                    request.form.get("phone") or None,
                    request.form.get("linkedin_url") or None,
                    request.form.get("notes") or None,
                    contact_id
                ))
                connection.commit()
                flash("Contact updated successfully!", "success")
                return redirect(url_for("contacts"))
            except Error:
                connection.rollback()
                flash("Could not update contact.", "error")
                return redirect(url_for(
                    "edit_contact", contact_id=contact_id
                ))

        cursor.execute("""
            SELECT * FROM contacts WHERE contact_id=%s
        """, (contact_id,))
        contact = cursor.fetchone()

        if not contact:
            return "Contact not found", 404

        cursor.execute("""
            SELECT company_id, company_name
            FROM companies ORDER BY company_name
        """)
        company_list = cursor.fetchall()

        return render_template(
            "edit_contact.html",
            contact=contact,
            companies=company_list
        )
    finally:
        cursor.close()
        connection.close()


@app.route("/contacts/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            DELETE FROM contacts WHERE contact_id=%s
        """, (contact_id,))
        connection.commit()
        flash("Contact deleted successfully!", "success")
    except Error:
        connection.rollback()
        flash("Could not delete contact.", "error")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("contacts"))


# ---------------- JOB MATCH ----------------

@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    skills_input = ""
    results = None

    if request.method == "POST":
        skills_input = request.form.get("skills", "").strip()

        user_skills = {
            skill.strip().casefold()
            for skill in skills_input.split(",")
            if skill.strip()
        }

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT j.job_id, j.job_title, j.requirements,
                       c.company_name
                FROM jobs j
                LEFT JOIN companies c
                    ON j.company_id = c.company_id
            """)

            jobs_list = cursor.fetchall()
            results = []

            for job in jobs_list:
                required_skills = get_skills(job["requirements"])

                if not isinstance(required_skills, list):
                    required_skills = []

                required_skills = [
                    str(skill).strip()
                    for skill in required_skills
                    if str(skill).strip()
                ]

                matching_skills = [
                    skill for skill in required_skills
                    if skill.casefold() in user_skills
                ]

                missing_skills = [
                    skill for skill in required_skills
                    if skill.casefold() not in user_skills
                ]

                if required_skills:
                    match_percentage = round(
                        len(matching_skills) / len(required_skills) * 100
                    )
                else:
                    match_percentage = 0

                results.append({
                    "job_id": job["job_id"],
                    "job_title": job["job_title"],
                    "company_name": job["company_name"] or "Unknown Company",
                    "match_percentage": match_percentage,
                    "matching_skills": matching_skills,
                    "missing_skills": missing_skills
                })

            results.sort(
                key=lambda job: job["match_percentage"],
                reverse=True
            )

        finally:
            cursor.close()
            connection.close()

    return render_template(
        "job_match.html",
        skills_input=skills_input,
        results=results
    )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)

