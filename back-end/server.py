from flask import Flask, request
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv
import os
from PIL import Image
from itemsDetections import init_detector
import json 
import io
import base64

load_dotenv()

app = Flask(__name__)
CORS(app)

db_rid_of = mysql.connector.connect(
  host=os.getenv("DB_HOST"),
  user=os.getenv("DB_USER"),
  password=os.getenv("DB_PASSWORD"),
  database=os.getenv("DB_NAME")
)
itemcursor = db_rid_of.cursor(dictionary=True)
items_detector = init_detector(os.getenv("MODEL_PATH"))


@app.route('/detect_items', methods=['POST'])
def detect_items():
    img_data = request.data[23:]
    print(img_data)
    print(type(img_data))
    with open("target.jpeg", "wb") as fh:
        fh.write(base64.b64decode(img_data))
        fh.close()
    img = Image.open("target.jpeg")
    detected_obj = items_detector.detectObjectsFromImage(input_image="target.jpeg", output_image_path="target_output.jpeg", minimum_percentage_probability = 80)
    items_list = []
    for obj in detected_obj:
        byteIO = io.BytesIO()
        resized_img = img.crop(box=obj["box_points"])
        resized_img.save(byteIO, format='JPEG')
        byteArr = byteIO.getvalue()
        items_list.append({'name': obj["name"], 'img': base64.encodebytes(byteArr).decode()})
    json_dump = json.dumps({"items": items_list})
    return json_dump


@app.route("/items/<item_id>", methods=["GET"])
def get_item(item_id):
    itemId = item_id
    item_request = f"SELECT * FROM items INNER JOIN cats ON items.cats_id = cats.id WHERE items.id ='{itemId}'"
    itemcursor.execute(item_request)
    data = itemcursor.fetchall()
    return json.dumps({"data": data})

@app.route("/items", methods=["GET"])
def get_all_items():
    item_request = f"SELECT * FROM items INNER JOIN cats ON items.cats_id = cats.id"
    itemcursor.execute(item_request)
    data = itemcursor.fetchall()
    return json.dumps({"data": data})
    

@app.route("/items", methods=["POST"])
def get_items():
    data = request.json
    items_to_search = data["data"]
    names = f"name = '{items_to_search[0]}'"
    i = 0
    for item in items_to_search:
        if i > 0:
            names += f" OR name = '{item}'"
        i += 1
    item_request = "SELECT * FROM items INNER JOIN cats ON items.cats_id = cats.id WHERE " + names
    itemcursor.execute(item_request)
    data = itemcursor.fetchall()
    return json.dumps({"data": data})


@app.route('/')
def hello():
    return 'Hello, World!'


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)