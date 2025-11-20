# Home Management System

[![Author](https://img.shields.io/badge/Author-%20WeiWen%20Wu-blue)](https://github.com/timmy90928) ![GitHub last commit](https://img.shields.io/github/last-commit/timmy90928/Home) ![GitHub repo size](https://img.shields.io/github/repo-size/timmy90928/Home) ![GitHub Release](https://img.shields.io/github/v/release/timmy90928/Home) ![GitHub Release Date](https://img.shields.io/github/release-date/timmy90928/Home)

A comprehensive Home Management System built with Flask, designed to help you manage personal finances, travel diaries, and server configurations.

## Features

*   **Accounting**: Track your income and expenses with detailed records and monthly analysis.
*   **Travel Diary**: Record your travel footprints on an interactive map (supports GPS positioning).
*   **Server Management**: Monitor and manage your home server status.
*   **Account Management**: User authentication and role-based access control (including Viewer role).
*   **System Tray Icon**: Quickly access the system status from your desktop tray.
*   **Internationalization (i18n)**: Supports multiple languages.

## Tech Stack

*   **Backend**: Python, Flask, Waitress
*   **Database**: SQLAlchemy, Flask-Migrate
*   **Frontend**: HTML, CSS, JavaScript, Jinja2 Templates
*   **Others**: PyBabel (i18n), Pystray (System Tray)

## Installation

### Prerequisites

*   Python 3.8+
*   pip

### Steps

1.  **Clone the repository**
    ```bash
    git clone https://github.com/timmy90928/Home.git
    cd Home
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Initialize Database**
    ```bash
    set FLASK_APP=server_run.py
    flask db init
    flask db migrate
    flask db upgrade
    ```

4.  **Compile Translations**
    ```bash
    pybabel compile -d translations
    ```

## Usage

### Development Mode
To run the server in debug mode:
```bash
# Create a .env file if needed, or just run:
python server_run.py
```
*Note: Ensure `server/DEBUG` config is set to True in your configuration or environment.*

### Production Mode
To run the server using Waitress (production-ready WSGI server):
```bash
# Run the server in the background (Windows optimized)
pythonw server_run.py
```

### System Tray
The application includes a system tray icon for quick access and status monitoring.

## Deployment

### Nginx Configuration
1.  Download [nginx](https://nginx.org/en/download.html).
2.  Copy the provided configuration file:
    *   Source: `[nginx.conf](./docs/nginx.conf)`
    *   Destination: `...\nginx\conf\nginx.conf`
3.  Start Nginx.

## Development

### Internationalization (i18n)
To update translations:
```bash
# Extract messages
pybabel extract -F babel.cfg -o messages.pot .

# Update translation files
pybabel update -i messages.pot -d translations

# Compile translations
pybabel compile -d translations
```

### Database Migrations
```bash
set FLASK_APP=server_run.py
flask db migrate -m "Migration message"
flask db upgrade
```

## Version History
For a detailed log of changes, please refer to [version.md](./docs/version.md).
