import os
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from flask import Flask, Response, jsonify
import cv2
import numpy as np
import time
import tensorflow as tf

app = Flask(__name__)

# Configuración del modelo y catálogo
MODEL_PATH = "modelo_ia/keras_model.h5"
LABELS_PATH = "modelo_ia/labels.txt"

CATALOGO = {
    "Pollo": {"price": 5.50},
    "Tortuga": {"price": 12.00},
    "Cohete": {"price": 25.00},
    "Cartas pokemon": {"price": 4.99},
    "Sylveon": {"price": 15.00}
}

# Cargar etiquetas
labels = {}
if os.path.exists(LABELS_PATH):
    with open(LABELS_PATH, "r") as f:
        for line in f.readlines():
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                labels[int(parts[0])] = parts[1]

# Cargar modelo
model = None
if os.path.exists(MODEL_PATH):
    from tensorflow.keras.models import load_model
    np.set_printoptions(suppress=True)
    model = load_model(MODEL_PATH, compile=False)
    print("Modelo IA cargado en el servidor Flask.")

# Variables de estado para la lógica de 1.5s
estado_ia = {
    "tracking_label": None,
    "tracking_start_time": None,
    "pending_items": [] # Items confirmados listos para que Streamlit los recoja
}
confidence_threshold = 0.85
time_threshold = 1.5

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Procesar IA
            label = "Desconocido"
            confidence = 0.0
            
            if model is not None:
                resized = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
                image_array = np.asarray(resized, dtype=np.float32).reshape(1, 224, 224, 3)
                image_array = (image_array / 127.5) - 1
                
                prediction = model(image_array, training=False).numpy()
                index = np.argmax(prediction)
                label = labels.get(index, "Desconocido")
                confidence = float(prediction[0][index])

            # Lógica de 1.5s
            if label != "Desconocido" and label in CATALOGO and confidence >= confidence_threshold:
                if estado_ia["tracking_label"] == label:
                    elapsed = time.time() - estado_ia["tracking_start_time"]
                    if elapsed >= time_threshold:
                        # Confirmar item
                        estado_ia["pending_items"].append({
                            "name": label,
                            "price": CATALOGO[label]["price"],
                            "source": "Visión IA"
                        })
                        # Reset
                        estado_ia["tracking_label"] = None
                        estado_ia["tracking_start_time"] = None
                else:
                    estado_ia["tracking_label"] = label
                    estado_ia["tracking_start_time"] = time.time()
            else:
                estado_ia["tracking_label"] = None
                estado_ia["tracking_start_time"] = None

            # Dibujar HUD estilo supermercado
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (frame.shape[1], 70), (0, 0, 0), -1)
            alpha = 0.6
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
            
            hud_color = (0, 255, 0) if confidence > 0.85 else (255, 255, 255)
            cv2.putText(frame, f"ESCANEANDO: {label} ({confidence*100:.0f}%)", (20, 45),
                        cv2.FONT_HERSHEY_DUPLEX, 1, hud_color, 2)
            
            if estado_ia["tracking_label"]:
                cv2.putText(frame, "Mantenga el producto quieto...", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_pending_items')
def get_pending_items():
    items = estado_ia["pending_items"].copy()
    estado_ia["pending_items"].clear()
    return jsonify({"items": items})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
