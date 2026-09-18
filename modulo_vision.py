import cv2
import numpy as np
import os
import random
import time

MODEL_PATH = "modelo_ia/keras_model.h5"
LABELS_PATH = "modelo_ia/labels.txt"

# Try loading TensorFlow conditionally inside the class to prevent crashes on Mac
TF_AVAILABLE = False # Will be updated if loaded successfully

class VisionModule:
    def __init__(self):
        self.labels = {}
        self.model = None
        self.use_mock = True
        self._load_labels()
        self._load_model()
        
    def _load_labels(self):
        if os.path.exists(LABELS_PATH):
            with open(LABELS_PATH, "r") as f:
                for line in f.readlines():
                    parts = line.strip().split(" ", 1)
                    if len(parts) == 2:
                        self.labels[int(parts[0])] = parts[1]
        else:
            print("Labels not found, using defaults.")
            self.labels = {0: "Apple", 1: "Banana", 2: "Orange", 3: "Soda", 4: "Chips", 5: "Unknown"}

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                from tensorflow.keras.models import load_model
                # Disable scientific notation for clarity
                np.set_printoptions(suppress=True)
                self.model = load_model(MODEL_PATH, compile=False)
                self.use_mock = False
                print("Model loaded successfully.")
            except ImportError:
                print("TensorFlow not found. Cannot load real model.")
            except Exception as e:
                print(f"Failed to load model: {e}")
        else:
            print("Model keras_model.h5 not found. Using mock mode.")

    def process_frame(self, frame):
        """
        Processes a BGR OpenCV frame and returns (label_name, confidence)
        """
        if self.use_mock:
            # Mock mode: return random valid class 20% of the time, Unknown otherwise
            # This allows testing the 1.5s logic without a real model.
            # We want sustained detection, so let's mock a sustained detection based on time.
            t = int(time.time() / 2)  # changes every 2 seconds
            if t % 3 == 0:
                mock_label = self.labels.get(0, "Apple")
                return mock_label, 0.95
            elif t % 3 == 1:
                mock_label = self.labels.get(1, "Banana")
                return mock_label, 0.90
            else:
                return "Unknown", 0.0

        # Real model inference (Google Teachable Machine standard)
        try:
            # Resize to 224x224
            resized_frame = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
            
            # Make the image a numpy array and reshape it to the models input shape.
            image_array = np.asarray(resized_frame, dtype=np.float32).reshape(1, 224, 224, 3)
            
            # Normalize the image
            image_array = (image_array / 127.5) - 1
            
            # Predict (using direct call instead of .predict to prevent Streamlit thread crash on Mac)
            prediction = self.model(image_array, training=False).numpy()
            index = np.argmax(prediction)
            class_name = self.labels.get(index, "Unknown")
            confidence_score = prediction[0][index]
            
            return class_name, float(confidence_score)
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return "Unknown", 0.0
