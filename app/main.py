from flask import Flask
from flask_cors import CORS
from app.rout.search_routes import search_routes

app = Flask(__name__)
CORS(app)

app.register_blueprint(search_routes)

@app.route('/health')
def health_check():
    return {"status": "healthy"}

if __name__ == '__main__':
    print("Starting Elastic server...")
    app.run(debug=True, port=5003)