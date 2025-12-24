# Frognance

Frognance is a web application for personal and group finance management, built with Django. It allows users to track their income and expenses, categorize them, and manage shared budgets in groups.

## Key Features

- **User Authentication**: Secure registration and login system with profile editing capabilities.
- **Transaction Management**: Add, view, and categorize income and expense transactions.
- **Group Budgeting**: Create and manage groups for shared finances, including a role-based member system (admin, member) and an invitation system.
- **Personal & Group Dashboards**: Separate overviews for personal and group financial activities.
- **Data Export**: Export financial transactions to an Excel file.
- **REST API**: A simple API endpoint to fetch user income data with token-based authentication.

## Tech Stack

- **Backend**: Python, Django, Django REST Framework
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, Bootstrap 5 (via `django-crispy-forms`)
- **Other Libraries**: `openpyxl` (for Excel export), `psycopg2-binary` (for PostgreSQL connection).

## Getting Started

### Prerequisites

- Python 3.13+
- PostgreSQL database
- Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/frognance.git
    cd frognance
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory of the project. You can copy the `.env.example` file if it exists.
    ```env
    SECRET_KEY='your-django-secret-key'
    DEBUG='True'
    ALLOWED_HOSTS='127.0.0.1,localhost'
    DB_ENGINE='django.db.backends.postgresql'
    DB_NAME='frognance_db'
    DB_USER='postgres'
    DB_PASSWORD='your_password'
    DB_HOST='localhost'
    DB_PORT='5432'
    ```

5.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser (optional):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000`.

## Development Setup

This project uses `pre-commit` to automate dependency management and ensure code quality.

### Initial Setup

1.  **Install development tools:**
    After activating your virtual environment, install the necessary tools:
    ```bash
    pip install pre-commit
    ```

2.  **Activate pre-commit hooks:**
    This will set up the git hooks that run automatically before each commit.
    ```bash
    pre-commit install
    ```

### How it Works

- **Dependency Management**: This project uses `pip-tools` to lock dependencies. You only need to edit `requirements.in` to add or remove a top-level dependency.
- **Automatic Updates**: When you run `git commit`, a `pre-commit` hook automatically runs `pip-compile`. This updates `requirements.txt` with the exact versions of all dependencies.

### Workflow

1.  **Modify `requirements.in`** to add, change, or remove a dependency.
2.  **Run `git add requirements.in`**.
3.  **Run `git commit`**. The `pre-commit` hook will trigger, update `requirements.txt`, and add it to your commit.
4.  If the hook modifies `requirements.txt`, your commit might be aborted so you can review the changes. Simply `git add requirements.txt` and run `git commit` again.

## API Usage

The application provides a REST API endpoint to retrieve a user's income transactions.

- **Endpoint**: `/api/income/`
- **Method**: `GET`
- **Authentication**: Token-based. You must include an `Authorization` header with your token.
  ```
  Authorization: Token YOUR_AUTH_TOKEN
  ```
- **Response**: A paginated JSON object containing a list of income transactions.

To obtain an authentication token, you can create one via the Django admin panel or by using the `drf-create-token` management command.
