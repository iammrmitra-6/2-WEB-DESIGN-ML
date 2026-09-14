##### BUILDING URL DYNAMICALLY
##### VARIABLE RULE
##### JINJA 2 TEMPLATE ENGINE

##### JINJA2 TEMPLATE ENGINE
'''
{{ }} expressions to print output in html
{%....%} conditions, for loops
{#.....#} this is for comments
'''


from flask import Flask,render_template,request,redirect,url_for

app = Flask(__name__)

@app.route("/")
def hello():
    return "<html><H1>welcome to the flask course</H1></html>"

@app.route("/index")
def index():
    return render_template("index.html")





####variable rule
@app.route("/marks/<int:score>")
def marks(score):
    return "The marks you get is "+ str(score)

#####variable-rule
@app.route("/success/<int:score>")
def success(score):
    res=""
    if score>=50:
        res="PASS"
    else:
        res='FAIL'
    return render_template("result.html",results=res)


#for-loop
@app.route("/successres/<int:score>")
def successres(score):
    res=""
    if score>=50:
        res="PASS"
    else:
        res='FAIL'

    exp={'score':score ,"res":res} 
    return render_template("result1.html",results=exp)

#if-condition
@app.route("/successif/<int:score>")
def successif(score):
    return render_template("result2.html",results=score)



@app.route("/submit",methods=["POST","GET"])
def  submit():
    total_score=0
    if request.method=="POST":
        science=float(request.form["science"])
        maths=float(request.form["maths"])
        c=float(request.form["c"])
        data_science=float(request.form["datascience"])

        total_score=(science+maths+c+data_science)/4
    else:
        return render_template('getresult.html')
    return redirect(url_for('successres',score=total_score))####not working
        


if __name__ == "__main__":
    # Using a different port (5004) can help bypass 'Ghost Servers'
    app.run(debug=True, port=5004)