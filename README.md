Aztech E-Commerce & ERP Platform

Aztech is a monolithic e-commerce and internal enterprise resource planning (ERP) platform built with Django and PostgreSQL.

The current storefront brand operated by this instance is Loom, which is dynamically configurable via the database.

🏗 Architecture & Design Patterns

This project is built using a Django Model-View-Template (MVT) architecture, with a planned roadmap to decouple the frontend using Django REST Framework and React.

Key Architectural Decisions:

Dynamic Role-Based Access Control (RBAC): Bypasses Django's default groups. Roles are completely dynamic, stored as database records with boolean permission flags (e.g., can_view_financials, can_manage_inventory).

Custom User Model: Built from scratch to associate users with dynamic roles and employee metadata.

Singleton Settings Pattern: Store configurations (like the "Loom" brand name) are stored in the database to allow real-time changes without code deployments.

Abstract Base Models: Centralized UUID primary keys and created_at/updated_at timestamps to ensure data consistency across all applications.

Custom Dashboards: Bypasses Django's default /admin in favor of bespoke, role-restricted MVT dashboards for Employees, Shareholders, and Admins.

💻 Tech Stack

Backend Framework: Django (Python)

Database: PostgreSQL (with psycopg2-binary)

Image Processing: Pillow

🚀 Local Setup Instructions

Follow these steps to run the Aztech platform on your local machine.

1. Database Setup

Ensure PostgreSQL is installed and running. Create a new database named aztech_db. Update the DATABASES configuration in aztech/settings.py with your local Postgres password.

2. Environment Setup

Clone the repository and spin up your virtual environment:

git clone https://github.com/YOUR-USERNAME/aztech.git
cd aztech
python -m venv venv
# Activate on Windows: venv\Scripts\activate
# Activate on Mac/Linux: source venv/bin/activate


3. Install Dependencies

pip install django Pillow psycopg2-binary


4. Run Migrations & Start Server

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


🌿 Git Workflow (Feature Branching)

This project strictly follows a feature-branch workflow. Never commit directly to the main branch.

Ensure your local main is up to date: git checkout main && git pull origin main

Create a new branch for your feature: git checkout -b feature/name-of-feature

Write code and commit logically: git commit -m "Add descriptive message"

Push your branch: git push -u origin feature/name-of-feature

Open a Pull Request on GitHub to merge into main.