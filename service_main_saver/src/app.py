import pymongo

def save_to_mongodb(data):
    """Menyimpan data ke MongoDB."""
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        collection.insert_one(data)
        print("Data berhasil disimpan ke MongoDB:", data)
    except Exception as e:
        print("Error saat menyimpan ke MongoDB:", e)
    finally:
        client.close()