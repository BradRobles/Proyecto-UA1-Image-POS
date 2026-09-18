from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='modelo_ia/tfjs_model')
CORS(app)

@app.route('/model/<path:path>')
def send_model(path):
    return send_from_directory('modelo_ia/tfjs_model', path)

if __name__ == '__main__':
    app.run(port=5001)
