from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import json
from datetime import date

app = Flask(__name__)
app.secret_key = 'supergeheim123'

# Pad naar data-map en gebruikersbestand
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
USERS_FILE = os.path.join(data_dir, 'users.json')

# Helpers voor gebruikersbeheer
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# App modules laden
from models import Patient, NutritionPlan
from calculator import NutritionCalculator, RecommendationEngine
from app import NICUFluidApp

# NICU app initialiseren
nicu_app = NICUFluidApp(data_dir)

# ROUTES
@app.route('/')
def index():
    username = session.get('username')
    return render_template('index.html', username=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match")
            return render_template('register.html')

        users = load_users()

        if username in users:
            flash("Username already exists")
            return render_template('register.html')

        users[username] = password
        save_users(users)

        flash("Account successfully created!")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()

        if username in users and users[username] == password:
            session['username'] = username
            flash("Login successful!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("Je moet eerst inloggen.")
        return redirect(url_for('login'))

    # Simpele demo-data (vervang met echte data later)
    patients = []  # of bijv. load from file
    recent_plans = []
    nutrition_plans = 0
    today_plans = 0
    active_patients = 0

    return render_template(
        'dashboard.html',
        username=session['username'],
        patients=patients,
        recent_plans=recent_plans,
        nutrition_plans=nutrition_plans,
        today_plans=today_plans,
        active_patients=active_patients
    )

@app.route('/app')
def app_page():
    if 'username' not in session:
        flash("Je moet eerst inloggen.")
        return redirect(url_for('login'))
    return render_template('app.html', username=session['username'])

# API ROUTES
@app.route('/api/data/tpn_compositions', methods=['GET'])
def get_tpn_compositions():
    try:
        with open(os.path.join(data_dir, 'tpn_compositions.json'), 'r') as f:
            tpn_compositions = json.load(f)
        return jsonify(tpn_compositions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/solution_compositions', methods=['GET'])
def get_solution_compositions():
    try:
        with open(os.path.join(data_dir, 'solution_compositions.json'), 'r') as f:
            solution_compositions = json.load(f)
        return jsonify(solution_compositions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/fluid_requirements', methods=['GET'])
def get_fluid_requirements():
    try:
        with open(os.path.join(data_dir, 'fluid_requirements.json'), 'r') as f:
            fluid_requirements = json.load(f)
        return jsonify(fluid_requirements)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/patient', methods=['POST'])
def create_patient():
    try:
        data = request.json
        patient = nicu_app.create_patient(
            patient_id=data['patientId'],
            gestational_age_at_birth=float(data['gestationalAge']),
            birth_weight=int(data['birthWeight']),
            current_weight=int(data.get('currentWeight', data['birthWeight'])),
            postnatal_age=int(data['postnatalAge']),
            phototherapy=data.get('phototherapy', None),
            clinical_condition=data.get('clinicalCondition', 'Normal')
        )
        fluid_req = nicu_app.calculate_fluid_requirements(data['patientId'])
        return jsonify({
            "success": True,
            "patient_id": patient.patient_id,
            "fluid_requirements": fluid_req
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/nutrition_plan', methods=['POST'])
def create_nutrition_plan():
    try:
        data = request.json
        plan_id = f"NP-{data['patientId']}-{date.today().strftime('%Y%m%d')}"
        nutrition_plan = nicu_app.create_nutrition_plan(
            plan_id=plan_id,
            patient_id=data['patientId'],
            date=date.today(),
            total_fluid_target=float(data.get('totalFluidTarget', 0)),
            enteral_volume=float(data.get('enteralVolume', 0)),
            tpn_type=data.get('tpnType', 'NICU-mix'),
            tpn_volume=float(data.get('tpnVolume', 0)),
            lipid_type=data.get('lipidType', 'Intralipid_20%'),
            lipid_volume=float(data.get('lipidVolume', 0)),
            glucose_concentration=data.get('glucoseConcentration', '10%'),
            glucose_volume=float(data.get('glucoseVolume', 0)),
            enteral_feeding_type=data.get('enteralFeedingType', None),
            enteral_feeding_frequency=int(data.get('enteralFeedingFrequency', 0)),
            bmf_concentration=float(data.get('bmfConcentration', 0))
        )
        nicu_app.calculate_nutrition_values(plan_id)
        recommendations = nicu_app.generate_recommendations(plan_id)
        feeding_schedule = nicu_app.get_feeding_schedule(plan_id)
        response = {
            "success": True,
            "plan_id": plan_id,
            "calculated_values": {
                "total_energy": nutrition_plan.total_energy,
                "total_protein": nutrition_plan.total_protein,
                "total_carbohydrate": nutrition_plan.total_carbohydrate,
                "total_fat": nutrition_plan.total_fat,
                "total_sodium": nutrition_plan.total_sodium,
                "total_potassium": nutrition_plan.total_potassium,
                "total_calcium": nutrition_plan.total_calcium,
                "total_phosphate": nutrition_plan.total_phosphate,
                "total_magnesium": nutrition_plan.total_magnesium,
                "glucose_infusion_rate": nutrition_plan.glucose_infusion_rate,
                "total_parenteral_volume": nutrition_plan.calculate_parenteral_volume(),
                "total_fluid": nutrition_plan.calculate_total_fluid()
            },
            "recommendations": recommendations,
            "feeding_schedule": feeding_schedule
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export_plan/<plan_id>', methods=['GET'])
def export_plan(plan_id):
    try:
        filename = os.path.join(data_dir, f"nutrition_plan_{plan_id}.json")
        success = nicu_app.export_nutrition_plan(plan_id, filename)
        if success:
            return jsonify({"success": True, "filename": filename})
        else:
            return jsonify({"error": "Failed to export plan"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
