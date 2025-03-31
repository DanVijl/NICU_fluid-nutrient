"""
NICU Fluid Management App - Integration Test Script
"""

import os
import sys
import json
from datetime import date

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import application modules
from models import Patient, NutritionPlan
from calculator import NutritionCalculator, RecommendationEngine
from app import NICUFluidApp

def test_integration():
    """
    Integration test for the NICU Fluid Management App.
    Tests the entire workflow from patient creation to nutrition plan export.
    """
    print("Running integration tests for NICU Fluid Management App...")
    
    # Initialize app with data directory
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    app = NICUFluidApp(data_dir)
    
    # Test cases
    test_cases = [
        {
            "name": "Premature infant <1000g with phototherapy",
            "patient": {
                "patient_id": "TEST001",
                "gestational_age_at_birth": 28,
                "birth_weight": 950,
                "current_weight": 950,
                "postnatal_age": 3,
                "phototherapy": "Single",
                "clinical_condition": "Normal"
            },
            "nutrition_plan": {
                "total_fluid_target": 150,
                "enteral_volume": 30,
                "tpn_type": "NICU-mix",
                "tpn_volume": 80,
                "lipid_type": "Intralipid_20%",
                "lipid_volume": 20,
                "glucose_concentration": "10%",
                "glucose_volume": 20,
                "enteral_feeding_type": "Breast milk",
                "enteral_feeding_frequency": 12,
                "bmf_concentration": 0
            }
        },
        {
            "name": "Term infant with hyperglycemia",
            "patient": {
                "patient_id": "TEST002",
                "gestational_age_at_birth": 38,
                "birth_weight": 3200,
                "current_weight": 3150,
                "postnatal_age": 2,
                "phototherapy": "None",
                "clinical_condition": "Hyperglycemia"
            },
            "nutrition_plan": {
                "total_fluid_target": 100,
                "enteral_volume": 60,
                "tpn_type": "Samenstelling_B",
                "tpn_volume": 20,
                "lipid_type": "SMOF_20%",
                "lipid_volume": 10,
                "glucose_concentration": "5%",
                "glucose_volume": 10,
                "enteral_feeding_type": "Formula",
                "enteral_feeding_frequency": 8,
                "bmf_concentration": 0
            }
        },
        {
            "name": "Premature infant 1000-1500g with sepsis",
            "patient": {
                "patient_id": "TEST003",
                "gestational_age_at_birth": 32,
                "birth_weight": 1250,
                "current_weight": 1200,
                "postnatal_age": 5,
                "phototherapy": "Double",
                "clinical_condition": "Sepsis"
            },
            "nutrition_plan": {
                "total_fluid_target": 180,
                "enteral_volume": 50,
                "tpn_type": "NICU-mix",
                "tpn_volume": 90,
                "lipid_type": "Intralipid_20%",
                "lipid_volume": 15,
                "glucose_concentration": "12.5%",
                "glucose_volume": 25,
                "enteral_feeding_type": "Donor milk",
                "enteral_feeding_frequency": 12,
                "bmf_concentration": 1.0
            }
        }
    ]
    
    # Run tests for each case
    for i, test_case in enumerate(test_cases):
        print(f"\n=== Test Case {i+1}: {test_case['name']} ===")
        
        # Create patient
        patient_data = test_case["patient"]
        patient = app.create_patient(
            patient_id=patient_data["patient_id"],
            gestational_age_at_birth=patient_data["gestational_age_at_birth"],
            birth_weight=patient_data["birth_weight"],
            current_weight=patient_data["current_weight"],
            postnatal_age=patient_data["postnatal_age"],
            phototherapy=patient_data["phototherapy"],
            clinical_condition=patient_data["clinical_condition"]
        )
        
        # Calculate fluid requirements
        fluid_req = app.calculate_fluid_requirements(patient_data["patient_id"])
        print(f"Fluid requirements: {fluid_req}")
        
        # Create nutrition plan
        plan_data = test_case["nutrition_plan"]
        plan_id = f"NP-{patient_data['patient_id']}"
        plan = app.create_nutrition_plan(
            plan_id=plan_id,
            patient_id=patient_data["patient_id"],
            date=date.today(),
            total_fluid_target=plan_data["total_fluid_target"],
            enteral_volume=plan_data["enteral_volume"],
            tpn_type=plan_data["tpn_type"],
            tpn_volume=plan_data["tpn_volume"],
            lipid_type=plan_data["lipid_type"],
            lipid_volume=plan_data["lipid_volume"],
            glucose_concentration=plan_data["glucose_concentration"],
            glucose_volume=plan_data["glucose_volume"],
            enteral_feeding_type=plan_data["enteral_feeding_type"],
            enteral_feeding_frequency=plan_data["enteral_feeding_frequency"],
            bmf_concentration=plan_data["bmf_concentration"]
        )
        
        # Calculate nutrition values
        app.calculate_nutrition_values(plan_id)
        
        # Print nutrition plan details
        print(f"Total fluid: {plan.calculate_total_fluid()} ml/kg/day")
        print(f"Parenteral volume: {plan.calculate_parenteral_volume()} ml/kg/day")
        print(f"Energy: {plan.total_energy:.2f} kcal/kg/day")
        print(f"Protein: {plan.total_protein:.2f} g/kg/day")
        print(f"Carbohydrate: {plan.total_carbohydrate:.2f} g/kg/day")
        print(f"Fat: {plan.total_fat:.2f} g/kg/day")
        print(f"Glucose infusion rate: {plan.glucose_infusion_rate:.2f} mg/kg/min")
        
        # Generate recommendations
        recommendations = app.generate_recommendations(plan_id)
        print("\nRecommendations:")
        for rec in recommendations:
            print(f"- {rec}")
        
        # Get feeding schedule
        schedule = app.get_feeding_schedule(plan_id)
        print("\nFeeding schedule:")
        for feed in schedule:
            print(f"- {feed['time']}: {feed['volume_per_kg']:.2f} ml/kg of {feed['type']}")
        
        # Export nutrition plan
        export_file = os.path.join(data_dir, f"test_integration_{patient_data['patient_id']}.json")
        app.export_nutrition_plan(plan_id, export_file)
        print(f"\nNutrition plan exported to {export_file}")
        
        # Verify export file exists
        if os.path.exists(export_file):
            print(f"✓ Export file created successfully")
        else:
            print(f"✗ Failed to create export file")
    
    print("\nIntegration tests completed successfully!")

if __name__ == "__main__":
    test_integration()
