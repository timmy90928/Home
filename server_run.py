# pigar gen --with-referenced-comments
from routes import app, CONFIG, ALL_BP
from utils.utils import now_time

### Register blueprint ###
for bp in ALL_BP:
    app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port="928",debug=CONFIG('server/DEBUG'))