import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import json
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///nicu_app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import our application modules
from models import Patient, NutritionPlan
from calculator import NutritionCalculator, RecommendationEngine
from app import NICUFluidApp

# Initialize NICU Fluid App
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
nicu_app = NICUFluidApp(data_dir)

# Database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PatientDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    gestational_age_at_birth = db.Column(db.Float, nullable=False)
    birth_weight = db.Column(db.Integer, nullable=False)
    current_weight = db.Column(db.Integer, nullable=False)
    postnatal_age = db.Column(db.Integer, nullable=False)
    phototherapy = db.Column(db.String(20))
    clinical_condition = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    nutrition_plans = db.relationship('NutritionPlanDB', backref='patient', lazy=True)

class NutritionPlanDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.String(100), unique=True, nullable=False)
    patient_id = db.Column(db.String(100), db.ForeignKey('patient_db.patient_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_fluid_target = db.Column(db.Float)
    enteral_volume = db.Column(db.Float)
    tpn_type = db.Column(db.String(50))
    tpn_volume = db.Column(db.Float)
    lipid_type = db.Column(db.String(50))
    lipid_volume = db.Column(db.Float)
    glucose_concentration = db.Column(db.String(20))
    glucose_volume = db.Column(db.Float)
    enteral_feeding_type = db.Column(db.String(50))
    enteral_feeding_frequency = db.Column(db.Integer)
    bmf_concentration = db.Column(db.Float)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # Calculated values stored as JSON
    calculated_values = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    feeding_schedule = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Application routes
@app.route('/')
def index():
    """Render the landing page"""
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Render the dashboard page"""
    patients = PatientDB.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', patients=patients)

@app.route('/app')
@login_required
def nicu_app_page():
    """Render the main application page"""
    return render_template('app.html')

# API endpoints
@app.route('/api/data/tpn_compositions', methods=['GET'])
@login_required
def get_tpn_compositions():
    """API endpoint to get TPN compositions"""
    try:
        with open(os.path.join(data_dir, 'tpn_compositions.json'), 'r') as f:
            tpn_compositions = json.load(f)
        return jsonify(tpn_compositions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/solution_compositions', methods=['GET'])
@login_required
def get_solution_compositions():
    """API endpoint to get solution compositions"""
    try:
        with open(os.path.join(data_dir, 'solution_compositions.json'), 'r') as f:
            solution_compositions = json.load(f)
        return jsonify(solution_compositions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/fluid_requirements', methods=['GET'])
@login_required
def get_fluid_requirements():
    """API endpoint to get fluid requirements"""
    try:
        with open(os.path.join(data_dir, 'fluid_requirements.json'), 'r') as f:
            fluid_requirements = json.load(f)
        return jsonify(fluid_requirements)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/patients', methods=['GET'])
@login_required
def get_patients():
    """API endpoint to get all patients for the current user"""
    try:
        patients = PatientDB.query.filter_by(user_id=current_user.id).all()
        result = []
        for patient in patients:
            result.append({
                'patient_id': patient.patient_id,
                'gestational_age_at_birth': patient.gestational_age_at_birth,
                'birth_weight': patient.birth_weight,
                'current_weight': patient.current_weight,
                'postnatal_age': patient.postnatal_age,
                'phototherapy': patient.phototherapy,
                'clinical_condition': patient.clinical_condition,
                'created_at': patient.created_at.isoformat()
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/patient/<patient_id>', methods=['GET'])
@login_required
def get_patient(patient_id):
    """API endpoint to get a specific patient"""
    try:
        patient = PatientDB.query.filter_by(patient_id=patient_id, user_id=current_user.id).first()
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        result = {
            'patient_id': patient.patient_id,
            'gestational_age_at_birth': patient.gestational_age_at_birth,
            'birth_weight': patient.birth_weight,
            'current_weight': patient.current_weight,
            'postnatal_age': patient.postnatal_age,
            'phototherapy': patient.phototherapy,
            'clinical_condition': patient.clinical_condition,
            'created_at': patient.created_at.isoformat()
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/patient', methods=['POST'])
@login_required
def create_patient():
    """API endpoint to create a patient"""
    try:
        data = request.json
        
        # Generate a unique patient ID if not provided
        patient_id = data.get('patientId', f"P-{uuid.uuid4().hex[:8]}")
        
        # Create patient in memory for calculations
        patient = nicu_app.create_patient(
            patient_id=patient_id,
            gestational_age_at_birth=float(data['gestationalAge']),
            birth_weight=int(data['birthWeight']),
            current_weight=int(data.get('currentWeight', data['birthWeight'])),
            postnatal_age=int(data['postnatalAge']),
            phototherapy=data.get('phototherapy', None),
            clinical_condition=data.get('clinicalCondition', 'Normal')
        )
        
        # Calculate fluid requirements
        fluid_req = nicu_app.calculate_fluid_requirements(patient_id)
        
        # Save patient to database
        db_patient = PatientDB(
            patient_id=patient_id,
            user_id=current_user.id,
            gestational_age_at_birth=float(data['gestationalAge']),
            birth_weight=int(data['birthWeight']),
            current_weight=int(data.get('currentWeight', data['birthWeight'])),
            postnatal_age=int(data['postnatalAge']),
            phototherapy=data.get('phototherapy', None),
            clinical_condition=data.get('clinicalCondition', 'Normal')
        )
        
        db.session.add(db_patient)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "patient_id": patient_id,
            "fluid_requirements": fluid_req
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/nutrition_plans/<patient_id>', methods=['GET'])
@login_required
def get_nutrition_plans(patient_id):
    """API endpoint to get all nutrition plans for a patient"""
    try:
        patient = PatientDB.query.filter_by(patient_id=patient_id, user_id=current_user.id).first()
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        plans = NutritionPlanDB.query.filter_by(patient_id=patient_id, user_id=current_user.id).all()
        result = []
        for plan in plans:
            result.append({
                'plan_id': plan.plan_id,
                'date': plan.date.isoformat(),
                'total_fluid_target': plan.total_fluid_target,
                'created_at': plan.created_at.isoformat()
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/nutrition_plan/<plan_id>', methods=['GET'])
@login_required
def get_nutrition_plan(plan_id):
    """API endpoint to get a specific nutrition plan"""
    try:
        plan = NutritionPlanDB.query.filter_by(plan_id=plan_id, user_id=current_user.id).first()
        if not plan:
            return jsonify({"error": "Nutrition plan not found"}), 404
        
        result = {
            'plan_id': plan.plan_id,
            'patient_id': plan.patient_id,
            'date': plan.date.isoformat(),
            'total_fluid_target': plan.total_fluid_target,
            'enteral_volume': plan.enteral_volume,
            'tpn_type': plan.tpn_type,
            'tpn_volume': plan.tpn_volume,
            'lipid_type': plan.lipid_type,
            'lipid_volume': plan.lipid_volume,
            'glucose_concentration': plan.glucose_concentration,
            'glucose_volume': plan.glucose_volume,
            'enteral_feeding_type': plan.enteral_feeding_type,
            'enteral_feeding_frequency': plan.enteral_feeding_frequency,
            'bmf_concentration': plan.bmf_concentration,
            'calculated_values': json.loads(plan.calculated_values) if plan.calculated_values else {},
            'recommendations': json.loads(plan.recommendations) if plan.recommendations else [],
            'feeding_schedule': json.loads(plan.feeding_schedule) if plan.feeding_schedule else []
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/nutrition_plan', methods=['POST'])
@login_required
def create_nutrition_plan():
    """API endpoint to create a nutrition plan"""
    try:
        data = request.json
        
        # Check if patient exists and belongs to current user
        patient = PatientDB.query.filter_by(patient_id=data['patientId'], user_id=current_user.id).first()
        if not patient:
            return jsonify({"error": "Patient not found or access denied"}), 404
        
        # Create a unique plan ID
        plan_id = f"NP-{data['patientId']}-{date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4]}"
        
        # Create nutrition plan in memory for calculations
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
        
        # Calculate nutrition values
        nicu_app.calculate_nutrition_values(plan_id)
        
        # Generate recommendations
        recommendations = nicu_app.generate_recommendations(plan_id)
        
        # Get feeding schedule
        feeding_schedule = nicu_app.get_feeding_schedule(plan_id)
        
        # Prepare calculated values
        calculated_values = {
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
        }
        
        # Save nutrition plan to database
        db_plan = NutritionPlanDB(
            plan_id=plan_id,
            patient_id=data['patientId'],
            user_id=current_user.id,
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
            bmf_concentration=float(data.get('bmfConcentration', 0)),
            calculated_values=json.dumps(calculated_values),
            recommendations=json.dumps(recommendations),
            feeding_schedule=json.dumps(feeding_schedule)
        )
        
        db.session.add(db_plan)
        db.session.commit()
        
        # Prepare response
        response = {
            "success": True,
            "plan_id": plan_id,
            "calculated_values": calculated_values,
            "recommendations": recommendations,
            "feeding_schedule": feeding_schedule
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export_plan/<plan_id>', methods=['GET'])
@login_required
def export_plan(plan_id):
    """API endpoint to export a nutrition plan"""
    try:
        # Check if plan exists and belongs to current user
        plan = NutritionPlanDB.query.filter_by(plan_id=plan_id, user_id=current_user.id).first()
        if not plan:
            return jsonify({"error": "Nutrition plan not found or access denied"}), 404
        
        # Get patient data
        patient = PatientDB.query.filter_by(patient_id=plan.patient_id, user_id=current_user.id).first()
        
        # Prepare export data
        export_data = {
            "patient": {
                "patient_id": patient.patient_id,
                "gestational_age_at_birth": patient.gestational_age_at_birth,
                "birth_weight": patient.birth_weight,
                "current_weight": patient.current_weight,
                "postnatal_age": patient.postnatal_age,
                "phototherapy": patient.phototherapy,
                "clinical_condition": patient.clinical_condition
            },
            "nutrition_plan": {
                "plan_id": plan.plan_id,
                "date": plan.date.isoformat(),
                "total_fluid_target": plan.total_fluid_target,
                "enteral_volume": plan.enteral_volume,
                "tpn_type": plan.tpn_type,
                "tpn_volume": plan.tpn_volume,
                "lipid_type": plan.lipid_type,
                "lipid_volume": plan.lipid_volume,
                "glucose_concentration": plan.glucose_concentration,
                "glucose_volume": plan.glucose_volume,
                "enteral_feeding_type": plan.enteral_feeding_type,
                "enteral_feeding_frequency": plan.enteral_feeding_frequency,
                "bmf_concentration": plan.bmf_concentration
            },
            "calculated_values": json.loads(plan.calculated_values) if plan.calculated_values else {},
            "recommendations": json.loads(plan.recommendations) if plan.recommendations else [],
            "feeding_schedule": json.loads(plan.feeding_schedule) if plan.feeding_schedule else []
        }
        
        return jsonify(export_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
