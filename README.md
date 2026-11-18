
# Job Application Tracker

## Project Overview

The Job Application Tracker is a web application that was built using Python, Flask, and MySQL. It helps users to organize their job search by managing companies, job opportunities, applications, and professional contacts.

The application also includes a Job Match feature that compares a user's skills against job requirements and calculates a matching percentage.

## Technologies Used

- Python 3
- Flask
- MySQL
- MySQL Connector for Python
- HTML
- CSS

## Features

### Dashboard
Displays the total number of companies, jobs, applications, and contacts stored in the database.

### Companies
Users can add, view, edit, and delete company information.

### Jobs
Users can manage job opportunities, including job titles, employment types, salary ranges, and required skills.

### Applications
Users can track job applications, update their application status, and store resume versions, cover letter information, and interview notes.

### Contacts
Users can manage professional contacts associated with companies.

### Job Match
Users can enter their skills and compare them against the requirements of saved jobs.

The system calculates a match percentage and displays matching and missing skills. Results are ranked from highest to lowest match.

## Database Structure

The application uses four MySQL tables:

1. companies
2. jobs
3. applications
4. contacts

The jobs table references companies.

The applications table references jobs.

The contacts table references companies.

The database schema is provided in `schema.sql`.

## Installation Instructions

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd job_tracker
```

### 2. Install Python Dependencies

Make sure Python 3 and pip are installed.

```bash
python -m pip install -r requirements.txt
```

### 3. Set Up MySQL

Install MySQL Server and MySQL Workbench.

Open MySQL Workbench and connect to your local MySQL server.

Open `schema.sql` and execute the script to create the `job_tracker` database and its tables.

### 4. Configure Database Connection

The application uses environment variables for database credentials.

On Windows PowerShell:

```powershell
$env:DB_HOST = "localhost"
$env:DB_USER = "root"
$env:DB_PASSWORD = Read-Host "Enter your MySQL password"
$env:DB_NAME = "job_tracker"
```

MAke sure to use your own MySQL password. Do not store passwords in source code or upload them to GitHub.

### 5. Run the Application

In the project directory, run:

```bash
python app.py
```

Then open:

http://127.0.0.1:5000/

## How to Use

1. Add a company in the Companies section.
2. Add a job associated with that company.
3. Track an application for the job.
4. Add professional contacts associated with companies.
5. Open Job Match and enter skills separated by commas.
6. Review matching percentages and missing skills.

## Example Job Match

Job: Software Developer

Required Skills: Python, SQL, Flask

User Skills: Python, SQL

Match Result: 67%

Missing Skill: Flask

## AI Usage

AI assistance used during development is documented in `AI_USAGE.md`.

## Demonstration

<div>
    <a href="https://www.loom.com/share/bfb82e0498d64a1c9bbf1d4685e5325a">
      <p>Job Application Tracker - Watch Video</p>
    </a>
    <a href="https://www.loom.com/share/bfb82e0498d64a1c9bbf1d4685e5325a">
      <img style="max-width:300px;" src="https://www.loom.com/v1/videos/bfb82e0498d64a1c9bbf1d4685e5325a/thumbnail.gif">
    </a>
  </div>
