from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import settings

app = Flask(__name__)

mongo_uri = settings.MONGODB_URI
db_name = settings.DB
collection_name = settings.COLLECTION

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search_query']
        vector_search = request.form.get('vector_search')
        min_year = request.form['min_year']
        if min_year == '':
            min_year = 1900
        min_rating = request.form['min_rating']
        if min_rating == '':
            min_rating = 0
        if (vector_search is None):
            return redirect(url_for('search',search_query=search_query, min_year=min_year, min_rating=min_rating))
        else:
            return redirect(url_for('vectorSearch',search_query=search_query, min_year=min_year, min_rating=min_rating))
    return render_template('index.html')

@app.route('/search/<search_query>/<int(signed=True):min_year>/<float(signed=True):min_rating>', methods=['GET'])
def search(search_query, min_year, min_rating):
    print('search query ', search_query)
    results = run_query(search_query, None, min_year, min_rating)
    return render_template('index.html', results=results, search_query=search_query, vector='unchecked', min_year=min_year, min_rating=min_rating)

@app.route('/vectorSearch/<search_query>/<int(signed=True):min_year>/<float(signed=True):min_rating>', methods=['GET'])
def vectorSearch(search_query, min_year, min_rating):
    print('vector search for ', search_query)
    results = run_query(search_query, True, min_year, min_rating)
    return render_template('index.html', results=results, search_query=search_query, vector='checked', min_year=min_year, min_rating=min_rating)

def generate_vector(data):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return model.encode(data).tolist()

def highlight_words_in_plot(plot):
    for word in ['happy','fun']:
        plot = plot.replace(word, f'<span class="highlight">{word}</span>')
    return plot

def add_highlights(highlight):
    txt = ""
    
    # BUILD OUT HIGHLIGHTS FROM FULLPLOT FIELD
    for text in highlight[0]["texts"]:
        if text["type"] == "hit":
            txt += f'<b><span class="highlight">{text["value"]} </span></b>'
        else:
            txt += text["value"]
                
    return txt

def run_query(search_query, vector_search, min_year, min_rating):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    if vector_search:
        search = {  '$vectorSearch': {
                        'index': 'vectorIndex', 
                        'path': 'vectorPlot', 
                        'queryVector': generate_vector(search_query),
                        'numCandidates': 150, 
                        'limit': 20,
                        "filter": {
                            "$and": [{"year": {"$gt": min_year}},
                                    {"imdb.rating": {"$gte": min_rating}}
                            ]
                        }
                    }
                }
    else:
        search = {  '$search': {
                        'compound': {
                            'must': [{
                                'text': {
                                    'query': search_query,
                                    'path': 'fullplot',
                                }
                            }],
                            'filter': [{
                                'range': {
                                    'path': 'year',
                                    'gt': min_year
                                }},
                                {'range': {
                                    'path': 'imdb.rating',
                                    'gte': min_rating
                                },
                            }]
                        },
                        'highlight': { 
                            'path': 'fullplot' 
                        }
                    }
                }
    print('search query: ', search)
    pipeline = [
        search,
        {
            '$project': {
                '_id': 0,
                'title': 1,
                'fullplot': 1,
                'year': 1,
                'imdb.rating': 1,
                'poster':1,
                'score': {
                    '$meta': 'searchScore',
                },
                'highlight': {'$meta': 'searchHighlights'},
            }
        },
        {'$limit': 20}
    ]
    
    results = list(collection.aggregate(pipeline))
    print('Search executed for ', search_query)
    client.close()
    
    if not(vector_search):
        for item in results:
            print('got result: ', item['title'])
            item['fullplot'] = add_highlights(item['highlight'])
    
    return results

if __name__ == '__main__':
    app.run(debug=True)
