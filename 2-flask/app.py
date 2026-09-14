from flask import Flask

app = Flask(__name__)

@app.route("/")
def welcome():
    return "welcome to this flask course ....hello my name is shannidhya mitra "

@app.route("/index")
def index():
    return "welcome to the index page"

if __name__ == "__main__":
    # Using a different port (5001) can help bypass 'Ghost Servers'
    app.run(debug=True, port=5001)
