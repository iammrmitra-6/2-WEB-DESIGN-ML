### put and delete ---http verb
#### working with API"s ---json

from flask import Flask, jsonify , request

app = Flask(__name__)

items=[
{"id":1,"name":"Item 1","Description":"This is item 1"},
{"id":2,"name":"Item 2","Description":"This is item 2"},
]

@app.route('/')
def home():
    return "welcome to the sample to do list app"

#### Get :retrieve all the items

@app.route('/item',methods=["GET"])
def get_items():
    return jsonify(items)

###get: retrieve a specific item by Id

@app.route("/item/<int:item_id>",methods=["GET"])
def get_item(item_id):
    item=next((item for item in items if item ["id"]==item_id),None)
    if item is None:
        return jsonify({"error":"item not found"})
    return jsonify(item)



##Post:create a new task 


@app.route("/item", methods=["POST"])
def create_item():
    if not request.json or not "name" in request.json:
        return jsonify({"error":"item not found"})
    new_item={
        "id":items[-1]["id"] +1 if items else 1,
        "name":request.json['name'],
        "description":request.json["description"]
        }
    
    items.append(new_item)
    return jsonify(new_item)

#### Put: Update an existing item


@app.route('/item/<int:item_id>',methods=["PUT"])
def update_item(item_id):
    item =next((item for item in items if item["id"]== item_id),None)
    if item is None:
        return jsonify({"error":"Item not found"})
    item['name']=request.json.get('name',item['name'])
    item['description'] =request.json.get('description',item['description'])
    return jsonify(item)


###Delete :delete an item

@app.route('/item/<int:item_id>',methods=["DELETE"])
def delete_item(item_id):
    global items
    items =[item for item in items if item["id"] != item_id]
    return jsonify({"result":"Item deleted"})
    

if __name__ == "__main__":
    # Using a different port (5005) can help bypass 'Ghost Servers'
    app.run(debug=True, port=5005)