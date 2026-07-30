Aztech E-Commerce & ERP Platform

Aztech is a monolithic e-commerce and internal enterprise resource planning (ERP) platform built with Django 5.2 and PostgreSQL. It features a custom, dynamic workflow engine and a database-driven theming system.

🏗 Architectural Pillars

Dynamic Workflow Engine: Bypasses static choices for status fields. Uses a native WorkflowState model to allow Super Admins to define business process stages (e.g., "Pending", "Shipped") dynamically from the dashboard.

Abstract Base Models: Centralized BaseModel provides:

UUID primary keys for secure, non-sequential resource identification.

Standard created_at and updated_at auditing.

Unified status integration with the custom workflow engine.

Singleton Store Settings: Global brand configurations (name, theme colors) are stored in the database, allowing real-time UI updates via a global context processor.

Role-Based Access Control (RBAC): Custom dynamic role management with granular boolean permission flags for ERP modules.

💻 Tech Stack

Framework: Django 5.2

Database: PostgreSQL

Frontend: Tailwind CSS (CDN-based for rapid prototyping)

Serialization: Django REST Framework (DRF) for API-driven interactions

📂 Project Structure

aztech/                 # Project configuration
base_utils/             # Core abstract models and workflow logic
dashboard/              # ERP management views
store/                  # E-commerce storefront logic
users/                  # Custom user models and authentication
utils/                  # Global context processors and helper utilities
static/                 # Global assets (CSS, JS, Images)
templates/              # Global master layouts (base.html)


🚀 Getting Started

1. Database Setup

Create a PostgreSQL database named aztech_db and update your credentials in aztech/settings.py.

2. Dependencies

pip install django Pillow psycopg2-binary djangorestframework


3. Migrations & Server

python manage.py makemigrations
python manage.py migrate
python manage.py runserver


🌿 Professional Workflow

We strictly follow a feature-branch workflow. Never commit directly to main.

Sync: git checkout main && git pull origin main

Branch: git checkout -b feature/your-feature-name

Commit: Use imperative mood (e.g., "Add product model" instead of "Added").

Push: git push -u origin feature/your-feature-name

PR: Open a Pull Request on GitHub for peer review and merging into main.