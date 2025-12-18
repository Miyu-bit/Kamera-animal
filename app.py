from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

app = Flask(__name__)
CORS(app)  # Untuk cross-origin requests dari frontend

# Setup database
engine = create_engine('sqlite:///animals.db')
Base = declarative_base()

class Detection(Base):
    __tablename__ = 'detections'
    id = Column(Integer, primary_key=True)
    animal_name = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Load model TensorFlow (pre-trained untuk klasifikasi gambar)
model = tf.keras.applications.MobileNetV2(weights='imagenet')  # Bisa ganti dengan model khusus hewan jika perlu
# Untuk akurasi lebih baik, gunakan model dari TensorFlow Hub: https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/classification/5

def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).resize((224, 224))
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['image']
    img_bytes = file.read()
    img = preprocess_image(img_bytes)
    
    predictions = model.predict(img)
    decoded = tf.keras.applications.imagenet_utils.decode_predictions(predictions, top=1)[0][0]
    animal_name = decoded[1]  # Nama hewan (misalnya 'tiger', 'elephant')
    
    # Simpan ke database
    session = Session()
    detection = Detection(animal_name=animal_name)
    session.add(detection)
    session.commit()
    session.close()
    
    # Tambahkan fakta unik (dari dictionary sederhana; bisa di-upgrade ke API eksternal)
    facts = {
        'tiger': {'habitat': 'Hutan tropis', 'fact': 'Harimau bisa berlari hingga 65 km/jam!', 'sound': 'Roar'},
        'elephant': {'habitat': 'Savana Afrika', 'fact': 'Gajah memiliki memori yang luar biasa.', 'sound': 'Trumpet'},
        # Tambahkan lebih banyak spesies
    }
    info = facts.get(animal_name.lower(), {'habitat': 'Tidak diketahui', 'fact': 'Fakta belum tersedia', 'sound': 'Tidak ada suara'})
    
    return jsonify({'animal': animal_name, 'confidence': float(decoded[2]), 'info': info})

if __name__ == '__main__':
    app.run(debug=True)