"""
NICU Fluid Management App - Test Script
"""

from models import Patient, NutritionPlan
from calculator import NutritionCalculator, RecommendationEngine
from app import NICUFluidApp
import os
import json
from datetime import date


def test_app():
    """
    Test the NICU Fluid Management App with sample data.
    """
    print("Testing NICU Fluid Management App...")
    
    # Initialize app with data directory
    data_dir = "/home/ubuntu/nicu_app/data"
    app = NICUFluidApp(data_dir)
    
    # Test case 1: Premature infant <1000g
    print("\n=== Test Case 1: Premature infant <1000g ===")
    patient1 = app.create_patient(
        patient_id="P001",
        gestational_age_at_birth=28,
        birth_weight=950,
        current_weight=950,
        postnatal_age=3,
        phototherapy="Single",
        clinical_condition="Normal"
    )
    
    # Calculate fluid requirements
    fluid_req = app.calculate_fluid_requirements("P001")
    print(f"Fluid requirements: {fluid_req}")
    
    # Create nutrition plan
    plan1 = app.create_nutrition_plan(
        plan_id="NP001",
        patient_id="P001",
        date=date.today(),
        total_fluid_target=150,
        enteral_volume=30,
        tpn_type="NICU-mix",
        tpn_volume=80,
        lipid_type="Intralipid_20%",
        lipid_volume=20,
        glucose_concentration="10%",
        glucose_volume=20,
        enteral_feeding_type="Breast milk",
        enteral_feeding_frequency=12,
        bmf_concentration=0
    )
    
    # Calculate nutrition values
    app.calculate_nutrition_values("NP001")
    
    # Print nutrition plan details
    print(f"Total fluid: {plan1.calculate_total_fluid()} ml/kg/day")
    print(f"Parenteral volume: {plan1.calculate_parenteral_volume()} ml/kg/day")
    print(f"Energy: {plan1.total_energy:.2f} kcal/kg/day")
    print(f"Protein: {plan1.total_protein:.2f} g/kg/day")
    print(f"Carbohydrate: {plan1.total_carbohydrate:.2f} g/kg/day")
    print(f"Fat: {plan1.total_fat:.2f} g/kg/day")
    print(f"Glucose infusion rate: {plan1.glucose_infusion_rate:.2f} mg/kg/min")
    
    # Generate recommendations
    recommendations = app.generate_recommendations("NP001")
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"- {rec}")
    
    # Get feeding schedule
    schedule = app.get_feeding_schedule("NP001")
    print("\nFeeding schedule:")
    for feed in schedule:
        print(f"- {feed['time']}: {feed['volume_per_kg']:.2f} ml/kg of {feed['type']}")
    
    # Export nutrition plan
    export_file = "/home/ubuntu/nicu_app/data/test_plan1.json"
    app.export_nutrition_plan("NP001", export_file)
    print(f"\nNutrition plan exported to {export_file}")
    
    # Test case 2: Term infant with phototherapy
    print("\n=== Test Case 2: Term infant with phototherapy ===")
    patient2 = app.create_patient(
        patient_id="P002",
        gestational_age_at_birth=38,
        birth_weight=3200,
        current_weight=3150,
        postnatal_age=2,
        phototherapy="Double",
        clinical_condition="Normal"
    )
    
    # Calculate fluid requirements
    fluid_req = app.calculate_fluid_requirements("P002")
    print(f"Fluid requirements: {fluid_req}")
    
    # Create nutrition plan
    plan2 = app.create_nutrition_plan(
        plan_id="NP002",
        patient_id="P002",
        date=date.today(),
        total_fluid_target=100,
        enteral_volume=60,
        tpn_type="Samenstelling_B",
        tpn_volume=20,
        lipid_type="SMOF_20%",
        lipid_volume=10,
        glucose_concentration="10%",
        glucose_volume=10,
        enteral_feeding_type="Formula",
        enteral_feeding_frequency=8,
        bmf_concentration=0
    )
    
    # Calculate nutrition values
    app.calculate_nutrition_values("NP002")
    
    # Print nutrition plan details
    print(f"Total fluid: {plan2.calculate_total_fluid()} ml/kg/day")
    print(f"Parenteral volume: {plan2.calculate_parenteral_volume()} ml/kg/day")
    print(f"Energy: {plan2.total_energy:.2f} kcal/kg/day")
    print(f"Protein: {plan2.total_protein:.2f} g/kg/day")
    print(f"Carbohydrate: {plan2.total_carbohydrate:.2f} g/kg/day")
    print(f"Fat: {plan2.total_fat:.2f} g/kg/day")
    print(f"Glucose infusion rate: {plan2.glucose_infusion_rate:.2f} mg/kg/min")
    
    # Generate recommendations
    recommendations = app.generate_recommendations("NP002")
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"- {rec}")
    
    # Get feeding schedule
    schedule = app.get_feeding_schedule("NP002")
    print("\nFeeding schedule:")
    for feed in schedule:
        print(f"- {feed['time']}: {feed['volume_per_kg']:.2f} ml/kg of {feed['type']}")
    
    # Export nutrition plan
    export_file = "/home/ubuntu/nicu_app/data/test_plan2.json"
    app.export_nutrition_plan("NP002", export_file)
    print(f"\nNutrition plan exported to {export_file}")
    
    print("\nTesting completed successfully!")


if __name__ == "__main__":
    test_app()
