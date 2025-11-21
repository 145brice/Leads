from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Contractor Leads SaaS</h1><p>Running on port 5002!</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
