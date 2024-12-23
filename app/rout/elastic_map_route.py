import folium
from app.db.elastic.config import Config
from app.db.elastic.elastic_connect import elastic_client
from app.main import app

@app.route('/map')
def show_map():
    try:
        m = folium.Map(location=[0, 0], zoom_start=2)
        query = {
            "query": {
                "match": {
                    "category": "terror_event"
                }
            }
        }
        if elastic_client.indices.exists(index=Config.ES_INDEX_FOR_NEWS):
            results = elastic_client.search(index=Config.ES_INDEX_FOR_NEWS, body=query)
            for hit in results['hits']['hits']:
                doc = hit['_source']
                if 'coordinates' in doc:
                    folium.Marker(
                        location=[doc['coordinates']['lat'], doc['coordinates']['lon']],
                        popup=f"""
                        <b>{doc['title']}</b><br>
                        Category: {doc['category']}<br>
                        Location: {doc['location']}
                        """,
                        icon=folium.Icon(color='red')
                    ).add_to(m)
        else:
            print(f"Index {Config.ES_INDEX_FOR_NEWS} does not exist")
        return m._repr_html_()
    except Exception as e:
        print(f"Error showing map: {e}")
        return f"Error showing map: {str(e)}", 500
