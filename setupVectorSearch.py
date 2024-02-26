# To setup vector search first install the huggingface transformer https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
# pip install -U sentence-transformers
# The following is the index definition for the vector index
# Call this index "vextorIndex" in the search UI
# {
#   "mappings": {
#     "dynamic": false,
#     "fields": [
#       {
#         "type": "vector",
#         "path": "vectorPlot",
#         "numDimensions": 384,
#         "similarity": "euclidean"
#       }
#     ]
#   }
# }
# 
# If need to tidy up the collection, delete the search index and unset the field: db.movies.updateMany({},{$unset:{"vectorPlot":""}})
# Use this to take an export of the data if you need to 
#   mongoexport --uri "mongodb+srv://<username>:<pwd>@youdcluster.l11d4ql.mongodb.net" -d sample_mflix -c movies -o movieData.json
# 

from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
import settings

mongo_uri = settings.MONGODB_URI
db_name = settings.DB
collection_name = settings.COLLECTION

def update_documents_with_vector_plot():
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Find documents with 'plot' field
    documents_to_update = collection.find({"fullplot": {"$exists": True}})

    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    for document in documents_to_update:
        # Here, you can calculate the vectorPlot based on the 'plot' field.
        # For demonstration purposes, we will just use a dummy value.
        
        # print(data)
        vectorPlot = model.encode(document['fullplot']).tolist()

        # Update the document with the new field 'vectorPlot'
        collection.update_one({'_id': document['_id']}, {"$set": {"vectorPlot": vectorPlot}})

    print("Documents updated successfully.")
    client.close()

if __name__ == "__main__":
    update_documents_with_vector_plot()
