#####porting flask using html


from flask import Flask,render_template

app = Flask(__name__)

@app.route("/")
def hello():
    return "<html><H1>welcome to the flask course</H1></html>"

@app.route("/index")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    # Using a different port (5002) can help bypass 'Ghost Servers'
    app.run(debug=True, port=5002)