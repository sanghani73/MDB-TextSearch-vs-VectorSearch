
# Atlas Vector Search - a simple demo
In this demo we will use the sample_mflix.movies collection and create two search indexes on the *fullplot* field. One will be a "regular" index and the other will be a vector index using the **all-MiniLM-L6-v2** transformer from huggingface details of which you can find [here](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).

### Setup
This demo uses a simple web application writtn in python using the flask framework. So ensure you have python3 installed and run the following to install the necessary dependencies:

```
pip install -U sentence-transformers pymongo Flask
```

If you want to run this on a the sample data set loaded in Atlas that does not have the vector embeddings stored for the fullplot field then modify and execute the setupVectorSearch.py script. This will take a few minutes to run.

Alternatively, you can use the data in the *movieData.json* export file (you'll need to uncompress *movieData.json.zip*) and import using the following command (replace the details with your uri):

```
mongoimport --uri "mongodb+srv://<username>:<password>@YourAtlasCluster.foo.mongodb.net" -d sample_mflix -c movies-copy --file movieData.json
```

Once you have the data in the movies collection, navigate to the Atlas Search consle and ensure you have a search index created on the *fullplot* field and a vector index created on the *vectorPlot* field. Here are the JSON configurations for both these indexes:

```
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "fullplot": {
        "type": "string"
    }
  }
}
```
```
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "vectorPlot": {
        "dimensions": 384,
        "similarity": "euclidean",
        "type": "knnVector"
      }
    }
  }
}
```
Before running the demo ensure you have updated the Atlas connection details in *settings.py* to match your environment.

### Run
To run the demo, navigate to this directory and execute the following command:

```
python3 app.py
```

This will launch the application on the default endpoint which is [http://127.0.0.1:5000](http://127.0.0.1:5000)

The demo script itself is relatively simple, enter some search criteria for the types of movies you want to see and show the difference between the traditional search (which uses tokenisers and inverted indexes to identify relevant results) and vector search (which uses transformers based on ML models to return contextually relevant results). A good example of this would be to search for  "animal adventure" or "Funny animals" or "something that will make me laugh and cry".