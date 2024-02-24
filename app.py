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
        if (vector_search is None):
            return redirect(url_for('search',search_query=search_query))
        else:
            return redirect(url_for('vectorSearch',search_query=search_query))
    return render_template('index.html')

@app.route('/search/<search_query>', methods=['GET'])
def search(search_query):
    print('search query ', search_query)
    results = run_query(search_query, None)
    return render_template('index.html', results=results, search_query=search_query, vector='unchecked')

@app.route('/vectorSearch/<search_query>', methods=['GET'])
def vectorSearch(search_query):
    print('vector search for ', search_query)
    results = run_query(search_query, True)
    return render_template('index.html', results=results, search_query=search_query, vector='checked')

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

def run_query(search_query, vector_search):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    if vector_search:
        search = {  '$vectorSearch': {
                        'index': 'vectorIndex', 
                        'path': 'vectorPlot', 
                        'queryVector': generate_vector(search_query),
                        'numCandidates': 150, 
                        'limit': 20
                    }
                }
    else:
        search = {  '$search': {
                        'text': {
                            'query': search_query,
                            'path': 'fullplot',
                            # 'fuzzy': {
                            #     'maxEdits': 2,
                            # },                        
                        },
                        'highlight': { 
                            'path': 'fullplot' 
                        }
                    }
                }

    pipeline = [
        search,
        {
            '$project': {
                '_id': 0,
                'title': 1,
                'fullplot': 1,
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
