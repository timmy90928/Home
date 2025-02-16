#  pythonw server_run.py
###* requirements ###
#? pigar gen --with-referenced-comments
#? pip freeze > requirements.txt

###* i18n ###
#? pybabel extract -F babel.cfg -o messages.pot .
#? pybabel update -i messages.pot -d translations
#? pybabel compile -d translations

from app import create_app
from waitress import serve
from utils.g import current
from dotenv import load_dotenv # pip install python-dotenv

if __name__ == "__main__":
    load_dotenv()

    if current.config.get('server/DEBUG'):
        APP = create_app('development')
        APP.run(host='0.0.0.0', port=928, debug=True)
    else:
        APP = create_app('production')
        serve(
            APP,
            host='0.0.0.0',
            port=928, 
            threads=8,
            connection_limit=10,  # 最大連線數
        )
    