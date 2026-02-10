import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CLOUD DATABASE CONFIGURATION ---
# Ye line automatically Cloud ka Database dhund legi
database_url = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODEL ---
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    service = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Pending')

# Create Tables
with app.app_context():
    db.create_all()

# --- API ENDPOINTS ---

@app.route('/')
def home():
    return "Salon Backend is Live & Running 24/7!"

@app.route('/book', methods=['POST'])
def book():
    data = request.json
    new_booking = Appointment(name=data['name'], phone=data['phone'], service=data['service'])
    db.session.add(new_booking)
    db.session.commit()
    return jsonify({"message": "Booking Confirmed!"})

@app.route('/status', methods=['GET'])
def get_status():
    pending_count = Appointment.query.filter_by(status='Pending').count()
    return jsonify({"people_ahead": pending_count, "wait_time": pending_count * 20})

@app.route('/admin-data', methods=['GET'])
def admin_data():
    pending_list = Appointment.query.filter_by(status='Pending').all()
    output = []
    for p in pending_list:
        output.append({"id": p.id, "name": p.name, "service": p.service})
    return jsonify(output)

@app.route('/complete/<int:id>', methods=['POST'])
def complete_task(id):
    appointment = Appointment.query.get(id)
    if appointment:
        appointment.status = 'Completed'
        db.session.commit()
        return jsonify({"message": "Done"})
    return jsonify({"error": "Not Found"}), 404

if __name__ == '__main__':
    app.run(debug=True)