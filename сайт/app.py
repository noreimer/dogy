import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from flask import Flask, request, jsonify, render_template
import sqlite3
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.applications.inception_v3 import InceptionV3, preprocess_input as incv3_preproc
from tensorflow.keras.applications.xception import Xception, preprocess_input as xception_preproc
from tensorflow.keras.layers import GlobalAveragePooling2D
import tensorflow as tf

app = Flask(__name__)

# Настройки
UPLOAD_FOLDER = 'interest'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Путь к базе данных
app.config['DATABASE'] = os.path.join(app.instance_path, 'breed.db')

# Загрузка модели
model_path = "dog_breed_classifier.h5"
model = load_model(model_path)

# Список пород (убедитесь, что он соответствует вашей модели)
dog_breeds = ['affenpinscher', 'afghan_hound', 'african_hunting_dog', 'airedale', 'american_staffordshire_terrier', 'appenzeller', 'australian_terrier', 'basenji', 'basset', 'beagle', 'bedlington_terrier',
               'bernese_mountain_dog', 'black-and-tan_coonhound', 'blenheim_spaniel', 'bloodhound', 'bluetick', 'border_collie', 'border_terrier', 'borzoi', 'boston_bull', 'bouvier_des_flandres', 'boxer',
               'brabancon_griffon', 'briard', 'brittany_spaniel', 'bull_mastiff', 'cairn', 'cardigan', 'chesapeake_bay_retriever', 'chihuahua', 'chow', 'clumber', 'cocker_spaniel', 'collie', 'curly-coated_retriever',
               'dandie_dinmont', 'dhole', 'dingo', 'doberman', 'english_foxhound', 'english_setter', 'english_springer', 'entlebucher', 'eskimo_dog', 'flat-coated_retriever', 'french_bulldog', 'german_shepherd',
               'german_short-haired_pointer', 'giant_schnauzer', 'golden_retriever', 'gordon_setter', 'great_dane', 'great_pyrenees', 'greater_swiss_mountain_dog', 'groenendael', 'ibizan_hound', 'irish_setter',
               'irish_terrier', 'irish_water_spaniel', 'irish_wolfhound', 'italian_greyhound', 'japanese_spaniel', 'keeshond', 'kelpie', 'kerry_blue_terrier', 'komondor', 'kuvasz', 'labrador_retriever',
               'lakeland_terrier', 'leonberg', 'lhasa', 'malamute', 'malinois', 'maltese_dog', 'mexican_hairless', 'miniature_pinscher', 'miniature_poodle', 'miniature_schnauzer', 'newfoundland', 'norfolk_terrier',
               'norwegian_elkhound', 'norwich_terrier', 'old_english_sheepdog', 'otterhound', 'papillon', 'pekinese', 'pembroke', 'pomeranian', 'pug', 'redbone', 'rhodesian_ridgeback', 'rottweiler', 'saint_bernard',
               'saluki', 'samoyed', 'schipperke', 'scotch_terrier', 'scottish_deerhound', 'sealyham_terrier', 'shetland_sheepdog', 'shih-tzu', 'siberian_husky', 'silky_terrier', 'soft-coated_wheaten_terrier',
               'staffordshire_bullterrier', 'standard_poodle', 'standard_schnauzer', 'sussex_spaniel', 'tibetan_mastiff', 'tibetan_terrier',
               'toy_poodle', 'toy_terrier', 'vizsla', 'walker_hound', 'weimaraner', 'welsh_springer_spaniel', 'west_highland_white_terrier', 'whippet', 'wire-haired_fox_terrier', 'yorkshire_terrier']



# Размер изображения
IMG_SIZE = (299, 299, 3)

def get_db():
    """Подключение к базе данных"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def extract_features(model_class, preproc_func, data):
    base_input = tf.keras.layers.Input(shape=IMG_SIZE)
    x = tf.keras.layers.Lambda(preproc_func)(base_input)
    base_model = model_class(weights='imagenet', include_top=False, input_shape=IMG_SIZE)(x)
    out = GlobalAveragePooling2D()(base_model)
    feature_extractor = tf.keras.models.Model(base_input, out)
    return feature_extractor.predict(data, batch_size=1, verbose=0)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    try:
        # Обработка изображения
        img = load_img(file_path, target_size=IMG_SIZE[:2])
        img_array = np.expand_dims(np.array(img), axis=0)
        
        feats_incv3 = extract_features(InceptionV3, incv3_preproc, img_array)
        feats_xcep = extract_features(Xception, xception_preproc, img_array)
        final_feats = np.concatenate([feats_incv3, feats_xcep], axis=-1)
        
        preds = model.predict(final_feats)
        breed = dog_breeds[np.argmax(preds[0])]
        
        return jsonify({
            "breed": breed,
            "filename": file.filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_breed_info')
def get_breed_info():
    breed_english = request.args.get('breed')
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM dog_breeds WHERE breed_english = ?", (breed_english,))
    breed_data = cursor.fetchone()
    conn.close()
    
    if breed_data:
        return jsonify({
            'breed_english': breed_data['breed_english'],
            'breed_russian': breed_data['breed_russian'],
            'fact1': breed_data['fact1'],
            'fact2': breed_data['fact2'],
            'fact3': breed_data['fact3']
        })
    else:
        return jsonify({'error': 'Breed not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)