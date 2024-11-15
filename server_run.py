# pigar gen --with-referenced-comments
# pip freeze > requirements.txt
from routes import app, CONFIG, ALL_BP, systray
from utils.utils import now_time
from wsgiref.simple_server import make_server
from dotenv import load_dotenv # pip install python-dotenv
load_dotenv()

### Register blueprint ###
for bp in ALL_BP:
    app.register_blueprint(bp)

if __name__ == "__main__":
    if CONFIG('server/DEBUG') == True:
        app.run(host="0.0.0.0",port="928",debug=True)
    else:
        systray.start()
        app.run(host="0.0.0.0",port="928",debug=False)