from pymongo import MongoClient
import settings

mongo_uri = settings.MONGODB_URI
db_name = settings.DB
collection_name = settings.COLLECTION

def delete_duplicate_movies():
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Get a list of unique titles and their corresponding document _ids
    pipeline = [
        {
            '$group': {
                '_id': '$title',
                'unique_ids': {'$addToSet': '$_id'},
                'count': {'$sum': 1}
            }
        },
        {
            '$match': {
                'count': {'$gt': 1}
            }
        }
    ]
    duplicate_titles = list(collection.aggregate(pipeline))

    # Delete duplicate documents
    for duplicate in duplicate_titles:
        # Keep the first document and delete the rest
        doc_to_keep_id = duplicate['unique_ids'][0]
        duplicate_ids_to_delete = duplicate['unique_ids'][1:]

        # Delete the duplicate documents
        collection.delete_many({'_id': {'$in': duplicate_ids_to_delete}})
        print(f"Deleted {len(duplicate_ids_to_delete)} duplicate(s) for title: {duplicate['_id']}")

    print("Duplicate deletion process completed.")

if __name__ == "__main__":
    delete_duplicate_movies()
