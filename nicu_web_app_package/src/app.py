"""
NICU Fluid Management App - Main Application
"""

from models import Patient, NutritionPlan
from calculator import NutritionCalculator, RecommendationEngine
import json
import os


class NICUFluidApp:
    """
    Main application class for NICU Fluid Management App.
    Coordinates between models, calculators, and user interface.
    """
    def __init__(self, data_dir):
        """
        Initialize the NICU Fluid Management App.
        
        Args:
            data_dir: Directory containing reference data files
        """
        self.data_dir = data_dir
        
        # Initialize calculator with reference data
        tpn_compositions_file = os.path.join(data_dir, 'tpn_compositions.json')
        solution_compositions_file = os.path.join(data_dir, 'solution_compositions.json')
        fluid_requirements_file = os.path.join(data_dir, 'fluid_requirements.json')
        
        self.calculator = NutritionCalculator(
            tpn_compositions_file,
            solution_compositions_file,
            fluid_requirements_file
        )
        
        self.recommendation_engine = RecommendationEngine(self.calculator)
        
        # Storage for patients and nutrition plans
        self.patients = {}
        self.nutrition_plans = {}
    
    def create_patient(self, patient_id, gestational_age_at_birth, birth_weight, current_weight=None, 
                      postnatal_age=1, phototherapy=None, clinical_condition="Normal"):
        """
        Create a new patient.
        
        Args:
            patient_id: Unique identifier for the patient
            gestational_age_at_birth: Gestational age in weeks at birth
            birth_weight: Weight in grams at birth
            current_weight: Current weight in grams
            postnatal_age: Age in days since birth
            phototherapy: None, "Single", or "Double"
            clinical_condition: "Normal", "Sepsis", "Hyperglycemia", etc.
            
        Returns:
            Newly created Patient object
        """
        patient = Patient(
            patient_id,
            gestational_age_at_birth,
            birth_weight,
            current_weight,
            postnatal_age,
            phototherapy,
            clinical_condition
        )
        
        self.patients[patient_id] = patient
        return patient
    
    def create_nutrition_plan(self, plan_id, patient_id, date, **kwargs):
        """
        Create a new nutrition plan for a patient.
        
        Args:
            plan_id: Unique identifier for the nutrition plan
            patient_id: Reference to the patient
            date: Date of the nutrition plan
            **kwargs: Additional parameters for the nutrition plan
            
        Returns:
            Newly created NutritionPlan object
        """
        if patient_id not in self.patients:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        nutrition_plan = NutritionPlan(plan_id, patient_id, date, **kwargs)
        self.nutrition_plans[plan_id] = nutrition_plan
        return nutrition_plan
    
    def calculate_fluid_requirements(self, patient_id):
        """
        Calculate fluid requirements for a patient.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            Dictionary with min and max fluid requirements
        """
        if patient_id not in self.patients:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        patient = self.patients[patient_id]
        return self.calculator.calculate_fluid_requirements(patient)
    
    def calculate_nutrition_values(self, plan_id):
        """
        Calculate nutrition values for a nutrition plan.
        
        Args:
            plan_id: ID of the nutrition plan
            
        Returns:
            Updated NutritionPlan object with calculated values
        """
        if plan_id not in self.nutrition_plans:
            raise ValueError(f"Nutrition plan with ID {plan_id} not found")
        
        nutrition_plan = self.nutrition_plans[plan_id]
        patient = self.patients[nutrition_plan.patient_id]
        
        return self.calculator.calculate_nutrition_values(nutrition_plan, patient)
    
    def generate_recommendations(self, plan_id):
        """
        Generate recommendations for a nutrition plan.
        
        Args:
            plan_id: ID of the nutrition plan
            
        Returns:
            List of recommendation strings
        """
        if plan_id not in self.nutrition_plans:
            raise ValueError(f"Nutrition plan with ID {plan_id} not found")
        
        nutrition_plan = self.nutrition_plans[plan_id]
        patient = self.patients[nutrition_plan.patient_id]
        
        # Ensure nutrition values are calculated
        self.calculate_nutrition_values(plan_id)
        
        return self.recommendation_engine.generate_recommendations(patient, nutrition_plan)
    
    def get_feeding_schedule(self, plan_id):
        """
        Generate a feeding schedule for a nutrition plan.
        
        Args:
            plan_id: ID of the nutrition plan
            
        Returns:
            List of feeding times and volumes
        """
        if plan_id not in self.nutrition_plans:
            raise ValueError(f"Nutrition plan with ID {plan_id} not found")
        
        nutrition_plan = self.nutrition_plans[plan_id]
        
        if not nutrition_plan.enteral_feeding_frequency or nutrition_plan.enteral_feeding_frequency <= 0:
            return []
        
        volume_per_feed = nutrition_plan.get_feeding_volume_per_feed()
        
        # Create a schedule based on frequency
        schedule = []
        hours_between_feeds = 24 / nutrition_plan.enteral_feeding_frequency
        
        for i in range(nutrition_plan.enteral_feeding_frequency):
            hour = int(i * hours_between_feeds)
            minute = int((i * hours_between_feeds - hour) * 60)
            time_str = f"{hour:02d}:{minute:02d}"
            schedule.append({
                "time": time_str,
                "volume_per_kg": volume_per_feed,
                "type": nutrition_plan.enteral_feeding_type
            })
        
        return schedule
    
    def export_nutrition_plan(self, plan_id, filename):
        """
        Export a nutrition plan to a JSON file.
        
        Args:
            plan_id: ID of the nutrition plan
            filename: Path to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        if plan_id not in self.nutrition_plans:
            raise ValueError(f"Nutrition plan with ID {plan_id} not found")
        
        nutrition_plan = self.nutrition_plans[plan_id]
        patient = self.patients[nutrition_plan.patient_id]
        
        # Ensure nutrition values are calculated
        self.calculate_nutrition_values(plan_id)
        
        # Create a dictionary with all relevant information
        export_data = {
            "patient": {
                "patient_id": patient.patient_id,
                "gestational_age_at_birth": patient.gestational_age_at_birth,
                "birth_weight": patient.birth_weight,
                "current_weight": patient.current_weight,
                "postnatal_age": patient.postnatal_age,
                "phototherapy": patient.phototherapy,
                "clinical_condition": patient.clinical_condition,
                "weight_category": patient.get_weight_category()
            },
            "nutrition_plan": {
                "plan_id": nutrition_plan.plan_id,
                "date": str(nutrition_plan.date),
                "total_fluid_target": nutrition_plan.total_fluid_target,
                "enteral_volume": nutrition_plan.enteral_volume,
                "parenteral_volume": nutrition_plan.calculate_parenteral_volume(),
                "tpn_type": nutrition_plan.tpn_type,
                "tpn_volume": nutrition_plan.tpn_volume,
                "lipid_type": nutrition_plan.lipid_type,
                "lipid_volume": nutrition_plan.lipid_volume,
                "glucose_concentration": nutrition_plan.glucose_concentration,
                "glucose_volume": nutrition_plan.glucose_volume,
                "enteral_feeding_type": nutrition_plan.enteral_feeding_type,
                "enteral_feeding_frequency": nutrition_plan.enteral_feeding_frequency,
                "bmf_concentration": nutrition_plan.bmf_concentration
            },
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
                "glucose_infusion_rate": nutrition_plan.glucose_infusion_rate
            },
            "recommendations": self.generate_recommendations(plan_id),
            "feeding_schedule": self.get_feeding_schedule(plan_id)
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting nutrition plan: {e}")
            return False
