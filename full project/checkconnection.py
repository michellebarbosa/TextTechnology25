from pymongo import MongoClient

uri = "mongodb+srv://shakesuser:M0ngoPass123@cluster0.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)

try:
    db = client["shakespeare_db"]
    collection = db["plays"]
    doc = collection.find_one()
    print(" Connected successfully!")
    print("Sample play title:", doc["title"])
except Exception as e:
    print(" Connection failed:", e)
