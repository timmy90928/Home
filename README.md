# Home
[![Author](https://img.shields.io/badge/Author-%20WeiWen%20Wu-blue)](https://github.com/timmy90928) ![GitHub last commit](https://img.shields.io/github/last-commit/timmy90928/Home) ![GitHub repo size](https://img.shields.io/github/repo-size/timmy90928/Home) ![GitHub Release](https://img.shields.io/github/v/release/timmy90928/Home) ![GitHub Release Date](https://img.shields.io/github/release-date/timmy90928/Home)

Home management system.

Develop
-------
### Install Dependencies
```bash
pip install -r requirements.txt
```

### I18n
```bash
pybabel compile -d translations
```

### Migrate
```bash
set FLASK_APP=server_run.py
flask db init
```

### Run from sources
Run `server_run.py`
```bash
# Run the server in the background (only works on Windows).
pythonw server_run.py   
```

### Make
Run `make.bat`. ([tutorial](./docs/build.md))

### Nginx
1. Download [nginx](https://nginx.org/en/download.html)
1. Copy [nginx.conf](./docs/nginx.conf) to `...\nginx\conf\nginx.conf`

Functions 
---------
* Account management.
* Server management.
* Travel diary.(travel map)
* Accounting function.
* System tray icon.

### For version update records, please see [version.md](./docs/version.md)
