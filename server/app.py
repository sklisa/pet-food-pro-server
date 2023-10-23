from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
import logging
import os
import time

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app = Flask(__name__)

# Connect to MongoDB
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_URI = f"mongodb+srv://pet-food-pro-admin:{MONGO_PASSWORD}@petfoodpro.6adpv0f.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client.PetFoodPro

@app.route('/')
def hello():
    return "Hello World!"

# Get product data from MongoDB
@app.route('/get-product-data', methods=['GET', 'POST'])    # Must also add GET to work in manual testing
def get_product_data():
    collection = db.product
    data = list(collection
                .find({}, {'_id': False})   # exclude id field
                .sort([('brand', pymongo.ASCENDING), ('product', pymongo.ASCENDING)])   # sort by brand and product
            )
    logging.info(f"Mongodb data length {len(data)}")
    data_core_nutrients = unfold_core_nutrients(data)
    return jsonify(data_core_nutrients)


def unfold_core_nutrients(data):
    data_core_nutrients = []
    for item in data:
        assert item['coreNutrients'][0]['nutrient'] == 'crude protein'
        item['crudeProtein'] = item['coreNutrients'][0]['percentage']

        assert item['coreNutrients'][1]['nutrient'] == 'crude fat'
        item['crudeFat'] = item['coreNutrients'][1]['percentage']

        assert item['coreNutrients'][2]['nutrient'] == 'crude fiber'
        item['crudeFiber'] = item['coreNutrients'][2]['percentage']

        assert item['coreNutrients'][3]['nutrient'] == 'moisture'
        item['moisture'] = item['coreNutrients'][3]['percentage']

        data_core_nutrients.append(item.copy())
    return data_core_nutrients


# Get product data from MongoDB
@app.route('/get-brands', methods=['GET', 'POST'])
def get_brands():
    collection = db.brand
    data = list(collection.find({}, {'_id': False}))   # exclude id field
    logging.info(f"Mongodb brand data length {len(data)}")
    print(sorted(data[0]['brands']))
    sorted_brands = sorted(data[0]['brands'])
    return jsonify(sorted_brands)


# Get product data from MongoDB
@app.route('/put-feedback', methods=['PUT'])
def put_feedback():
    collection = db.feedback
    feedback_data = {
        'createdDate': int(time.time()),
        'data': request.json['feedback']
    }
    try:
        collection.insert_one(feedback_data)    # Upload feedback data
        return jsonify({'message': 'Feedback submitted successfully'})
    except Exception as e:
        print("An exception occurred when submitting feedback to MongoDB:", e)
        return jsonify({'error': 'Feedback submission failed'}), 400


if __name__ == '__main__':
    # Deployment
    app.run()
    # Local
    # app.run(host='127.0.0.1', port=9874, debug=True)

