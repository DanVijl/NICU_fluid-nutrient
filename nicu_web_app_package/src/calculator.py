"""
NICU Fluid Management App - Calculation Logic
"""

import json


class NutritionCalculator:
    """
    Nutrition Calculator for NICU fluid management app.
    Performs calculations for fluid requirements and nutrition values.
    """
    def __init__(self, tpn_compositions_file, solution_compositions_file, fluid_requirements_file):
        """
        Initialize the NutritionCalculator with reference data.
        
        Args:
            tpn_compositions_file: Path to JSON file with TPN composition data
            solution_compositions_file: Path to JSON file with solution composition data
            fluid_requirements_file: Path to JSON file with fluid requirement data
        """
        # Load reference data from JSON files
        with open(tpn_compositions_file, 'r') as f:
            self.tpn_compositions = json.load(f)
        
        with open(solution_compositions_file, 'r') as f:
            self.solution_compositions = json.load(f)
        
        with open(fluid_requirements_file, 'r') as f:
            self.fluid_requirements = json.load(f)
    
    def calculate_fluid_requirements(self, patient):
        """
        Calculate fluid requirements based on patient data.
        
        Args:
            patient: Patient object with weight and age information
            
        Returns:
            Dictionary with min and max fluid requirements in ml/kg/day
        """
        weight_category = patient.get_weight_category()
        age_category = patient.get_postnatal_age_category()
        
        # Get base fluid requirements
        if weight_category in self.fluid_requirements["fluid_requirements"] and age_category in self.fluid_requirements["fluid_requirements"][weight_category]:
            base_req = self.fluid_requirements["fluid_requirements"][weight_category][age_category]
            min_fluid = base_req["min"]
            max_fluid = base_req["max"]
            
            # Adjust for phototherapy if needed
            if patient.phototherapy and patient.phototherapy.lower() != "none":
                photo_adj = self.fluid_requirements["fluid_requirements"]["phototherapy_adjustment"][patient.phototherapy.lower()]
                min_fluid += photo_adj["min"]
                max_fluid += photo_adj["max"]
            
            return {"min": min_fluid, "max": max_fluid}
        else:
            return {"min": 0, "max": 0}
    
    def calculate_nutrition_values(self, nutrition_plan, patient):
        """
        Calculate all nutrition values based on the nutrition plan.
        
        Args:
            nutrition_plan: NutritionPlan object with volumes and types
            patient: Patient object for reference
            
        Returns:
            Updated NutritionPlan object with calculated values
        """
        # Reset calculated values
        nutrition_plan.total_energy = 0
        nutrition_plan.total_protein = 0
        nutrition_plan.total_carbohydrate = 0
        nutrition_plan.total_fat = 0
        nutrition_plan.total_sodium = 0
        nutrition_plan.total_potassium = 0
        nutrition_plan.total_calcium = 0
        nutrition_plan.total_phosphate = 0
        nutrition_plan.total_magnesium = 0
        
        # Calculate from TPN
        if nutrition_plan.tpn_volume > 0 and nutrition_plan.tpn_type in self.tpn_compositions:
            tpn = self.tpn_compositions[nutrition_plan.tpn_type]
            nutrition_plan.total_energy += tpn["energy_kcal_per_ml"] * nutrition_plan.tpn_volume
            nutrition_plan.total_protein += tpn["protein_g_per_ml"] * nutrition_plan.tpn_volume
            nutrition_plan.total_carbohydrate += tpn["carbohydrate_g_per_ml"] * nutrition_plan.tpn_volume
            nutrition_plan.total_fat += tpn["fat_g_per_ml"] * nutrition_plan.tpn_volume
            nutrition_plan.total_sodium += tpn["sodium_mmol_per_ml"] * nutrition_plan.tpn_volume
            nutrition_plan.total_potassium += tpn["potassium_mmol_per_ml"] * nutrition_plan.tpn_volume
            nutrition_plan.total_calcium += tpn["calcium_mmol_per_ml"] * nutrition_plan.tpn_volume
            nutrition_plan.total_phosphate += tpn["phosphate_mmol_per_ml"] * nutrition_plan.tpn_volume
            nutrition_plan.total_magnesium += tpn["magnesium_mmol_per_ml"] * nutrition_plan.tpn_volume
        
        # Calculate from lipids
        if nutrition_plan.lipid_volume > 0 and nutrition_plan.lipid_type in self.solution_compositions["lipid_solutions"]:
            lipid = self.solution_compositions["lipid_solutions"][nutrition_plan.lipid_type]
            nutrition_plan.total_energy += lipid["energy_kcal_per_ml"] * nutrition_plan.lipid_volume
            nutrition_plan.total_fat += lipid["fat_g_per_ml"] * nutrition_plan.lipid_volume
        
        # Calculate from glucose
        if nutrition_plan.glucose_volume > 0 and nutrition_plan.glucose_concentration in self.solution_compositions["glucose_solutions"]:
            glucose = self.solution_compositions["glucose_solutions"][nutrition_plan.glucose_concentration]
            nutrition_plan.total_energy += glucose["energy_kcal_per_ml"] * nutrition_plan.glucose_volume
            nutrition_plan.total_carbohydrate += glucose["carbohydrate_g_per_ml"] * nutrition_plan.glucose_volume
            
            # Calculate glucose infusion rate (mg/kg/min)
            glucose_concentration_percent = float(nutrition_plan.glucose_concentration.strip('%'))
            glucose_mg_per_ml = glucose_concentration_percent * 10  # Convert % to mg/ml
            total_glucose_mg = glucose_mg_per_ml * nutrition_plan.glucose_volume
            nutrition_plan.glucose_infusion_rate = total_glucose_mg / (24 * 60)  # Convert to mg/kg/min
        
        # Calculate enteral nutrition contribution
        # This would be expanded based on enteral feeding types and fortifiers
        
        return nutrition_plan
    
    def calculate_glucose_infusion_rate(self, glucose_concentration, glucose_volume):
        """
        Calculate glucose infusion rate in mg/kg/min.
        
        Args:
            glucose_concentration: Concentration as string (e.g., "10%")
            glucose_volume: Volume in ml/kg/day
            
        Returns:
            Glucose infusion rate in mg/kg/min
        """
        glucose_concentration_percent = float(glucose_concentration.strip('%'))
        glucose_mg_per_ml = glucose_concentration_percent * 10  # Convert % to mg/ml
        total_glucose_mg = glucose_mg_per_ml * glucose_volume
        return total_glucose_mg / (24 * 60)  # Convert to mg/kg/min
    
    def get_macronutrient_requirements(self, patient):
        """
        Get macronutrient requirements based on patient data.
        
        Args:
            patient: Patient object with weight and age information
            
        Returns:
            Dictionary with macronutrient requirements
        """
        weight_category = patient.get_weight_category()
        age_category = patient.get_postnatal_age_category()
        
        # This would be expanded with actual macronutrient requirements from protocols
        # For now, returning placeholder values based on weight category
        
        if weight_category == "premature_less_1000g":
            return {
                "glucose_mg_kg_min": {"min": 4, "max": 12},
                "protein_g_kg_day": {"min": 2.5, "max": 3.5},
                "fat_g_kg_day": {"min": 2.5, "max": 3.5}
            }
        elif weight_category == "premature_1000_1500g":
            return {
                "glucose_mg_kg_min": {"min": 4, "max": 12},
                "protein_g_kg_day": {"min": 2.5, "max": 3.5},
                "fat_g_kg_day": {"min": 2.5, "max": 3.5}
            }
        elif weight_category == "premature_greater_1500g":
            return {
                "glucose_mg_kg_min": {"min": 4, "max": 12},
                "protein_g_kg_day": {"min": 2.0, "max": 3.0},
                "fat_g_kg_day": {"min": 2.0, "max": 3.0}
            }
        else:  # term
            return {
                "glucose_mg_kg_min": {"min": 2.5, "max": 5.0},
                "protein_g_kg_day": {"min": 1.5, "max": 2.5},
                "fat_g_kg_day": {"min": 1.0, "max": 3.0}
            }


class RecommendationEngine:
    """
    Recommendation Engine for NICU fluid management app.
    Generates recommendations based on patient data and nutrition plan.
    """
    def __init__(self, nutrition_calculator):
        """
        Initialize the RecommendationEngine with a NutritionCalculator.
        
        Args:
            nutrition_calculator: NutritionCalculator object for calculations
        """
        self.nutrition_calculator = nutrition_calculator
    
    def generate_recommendations(self, patient, nutrition_plan):
        """
        Generate recommendations based on patient data and nutrition plan.
        
        Args:
            patient: Patient object with clinical information
            nutrition_plan: NutritionPlan object with calculated values
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Check fluid requirements
        fluid_req = self.nutrition_calculator.calculate_fluid_requirements(patient)
        total_fluid = nutrition_plan.calculate_total_fluid()
        
        if total_fluid < fluid_req["min"]:
            recommendations.append(f"Increase total fluid intake to at least {fluid_req['min']} ml/kg/day (current: {total_fluid} ml/kg/day)")
        elif total_fluid > fluid_req["max"]:
            recommendations.append(f"Consider reducing total fluid intake to maximum {fluid_req['max']} ml/kg/day (current: {total_fluid} ml/kg/day)")
        
        # Check glucose infusion rate
        macro_req = self.nutrition_calculator.get_macronutrient_requirements(patient)
        
        if nutrition_plan.glucose_infusion_rate < macro_req["glucose_mg_kg_min"]["min"]:
            recommendations.append(f"Increase glucose infusion rate to at least {macro_req['glucose_mg_kg_min']['min']} mg/kg/min (current: {nutrition_plan.glucose_infusion_rate:.2f} mg/kg/min)")
        elif nutrition_plan.glucose_infusion_rate > macro_req["glucose_mg_kg_min"]["max"]:
            recommendations.append(f"Consider reducing glucose infusion rate to maximum {macro_req['glucose_mg_kg_min']['max']} mg/kg/min (current: {nutrition_plan.glucose_infusion_rate:.2f} mg/kg/min)")
        
        # Check protein intake
        if nutrition_plan.total_protein < macro_req["protein_g_kg_day"]["min"]:
            recommendations.append(f"Increase protein intake to at least {macro_req['protein_g_kg_day']['min']} g/kg/day (current: {nutrition_plan.total_protein:.2f} g/kg/day)")
        elif nutrition_plan.total_protein > macro_req["protein_g_kg_day"]["max"]:
            recommendations.append(f"Consider reducing protein intake to maximum {macro_req['protein_g_kg_day']['max']} g/kg/day (current: {nutrition_plan.total_protein:.2f} g/kg/day)")
        
        # Check fat intake
        if nutrition_plan.total_fat < macro_req["fat_g_kg_day"]["min"]:
            recommendations.append(f"Increase fat intake to at least {macro_req['fat_g_kg_day']['min']} g/kg/day (current: {nutrition_plan.total_fat:.2f} g/kg/day)")
        elif nutrition_plan.total_fat > macro_req["fat_g_kg_day"]["max"]:
            recommendations.append(f"Consider reducing fat intake to maximum {macro_req['fat_g_kg_day']['max']} g/kg/day (current: {nutrition_plan.total_fat:.2f} g/kg/day)")
        
        # Special clinical considerations
        if patient.clinical_condition == "Sepsis":
            recommendations.append("In sepsis, consider reducing lipid intake and monitoring triglyceride levels")
        elif patient.clinical_condition == "Hyperglycemia":
            recommendations.append("In hyperglycemia, consider reducing glucose infusion rate and monitoring blood glucose levels")
        
        return recommendations
