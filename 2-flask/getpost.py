#####porting flask using html
###using get post in flask


from flask import Flask,render_template,request

app = Flask(__name__)

@app.route("/")
def hello():
    return "<html><H1>welcome to the flask course</H1></html>"

@app.route("/index")
def index():
    return render_template("index.html")

@app.route('/form',methods=['GET','POST'])
def form():
    if request.method=="POST":
        name=request.form['name']
        return f'hello {name}'
    return render_template('form.html')

@app.route('/submit',methods=['GET','POST'])
def submit():
    if request.method=="POST":
        name=request.form['name']
        return f'hello {name}'
    return render_template('form.html')


if __name__ == "__main__":
    # Using a different port (5003) can help bypass 'Ghost Servers'
    app.run(debug=True, port=5003)