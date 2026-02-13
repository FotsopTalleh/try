import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from db import init_db, get_db
from models import create_valentine, get_valentine
import sqlite3

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB limit

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
init_db()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/create', methods=['POST'])
def create_valentine_endpoint():
    try:
        # Generate unique ID
        valentine_id = str(uuid.uuid4())[:8]
        
        # Get message from form data
        message = request.form.get('message', '')
        
        # Handle image uploads
        images = request.files.getlist('images')
        saved_images = []
        
        for image in images:
            if image and allowed_file(image.filename):
                # Generate unique filename
                ext = image.filename.rsplit('.', 1)[1].lower()
                filename = f"{valentine_id}_{uuid.uuid4()}.{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save file
                image.save(filepath)
                saved_images.append(filename)
        
        # Store in database
        with get_db() as conn:
            create_valentine(conn, valentine_id, message, saved_images)
        
        return jsonify({"id": valentine_id}), 201
        
    except Exception as e:
        print(f"Error creating valentine: {e}")
        return jsonify({"error": "Failed to create Valentine"}), 500

@app.route('/api/valentine/<valentine_id>', methods=['GET'])
def get_valentine_endpoint(valentine_id):
    try:
        with get_db() as conn:
            result = get_valentine(conn, valentine_id)
            
            if not result:
                return jsonify({"message": "", "images": []}), 200
            
            valentine, images = result
            
            # Construct image URLs
            image_urls = [f"/uploads/{img['filename']}" for img in images]
            
            return jsonify({
                "message": valentine['message'] or "",
                "images": image_urls
            }), 200
            
    except Exception as e:
        print(f"Error fetching valentine: {e}")
        return jsonify({"error": "Failed to fetch Valentine"}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)