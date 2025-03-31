# NICU Fluid Management App Data Model

## Patient Model
```python
class Patient:
    def __init__(self, patient_id, gestational_age_at_birth, birth_weight, current_weight=None, 
                 postnatal_age=1, phototherapy=None, clinical_condition="Normal"):
        self.patient_id = patient_id
        self.gestational_age_at_birth = gestational_age_at_birth  # in weeks
        self.birth_weight = birth_weight  # in grams
        self.current_weight = current_weight if current_weight and current_weight > birth_weight else birth_weight  # in grams
        self.postnatal_age = postnatal_age  # in days
        self.phototherapy = phototherapy  # None, "Single", or "Double"
        self.clinical_condition = clinical_condition  # "Normal", "Sepsis", "Hyperglycemia", etc.
    
    def get_weight_category(self):
        """Determine weight category for fluid and nutrient calculations"""
        weight = self.current_weight
        if weight < 1000:
            return "premature_less_1000g"
        elif weight < 1500:
            return "premature_1000_1500g"
        elif weight < 2500:
            return "premature_greater_1500g"
        else:
            return "term"
    
    def get_postnatal_age_category(self):
        """Determine postnatal age category for fluid requirements"""
        age = self.postnatal_age
        if age == 1:
            return "day_1"
        elif age == 2:
            return "day_2"
        elif age == 3:
            return "day_3"
        elif age == 4:
            return "day_4"
        elif 5 <= age <= 7:
            return "day_5_7"
        elif 8 <= age <= 14:
            return "day_8_14"
        else:
            return "day_15_plus"
```

## Nutrition Plan Model
```python
class NutritionPlan:
    def __init__(self, plan_id, patient_id, date, total_fluid_target=None,
                 enteral_volume=0, tpn_type="NICU-mix", tpn_volume=0,
                 lipid_type="Intralipid_20%", lipid_volume=0,
                 glucose_concentration="10%", glucose_volume=0,
                 enteral_feeding_type=None, enteral_feeding_frequency=None,
                 bmf_concentration=0):
        self.plan_id = plan_id
        self.patient_id = patient_id
        self.date = date
        self.total_fluid_target = total_fluid_target  # ml/kg/day
        self.enteral_volume = enteral_volume  # ml/kg/day
        self.parenteral_volume = 0  # Calculated field
        self.tpn_type = tpn_type  # "NICU-mix" or "Samenstelling_B"
        self.tpn_volume = tpn_volume  # ml/kg/day
        self.lipid_type = lipid_type  # "Intralipid_20%" or "SMOF_20%"
        self.lipid_volume = lipid_volume  # ml/kg/day
        self.glucose_concentration = glucose_concentration  # "5%", "10%", etc.
        self.glucose_volume = glucose_volume  # ml/kg/day
        self.enteral_feeding_type = enteral_feeding_type  # "Breast milk", "Donor milk", etc.
        self.enteral_feeding_frequency = enteral_feeding_frequency  # feedings per 24 hours
        self.bmf_concentration = bmf_concentration  # g/100ml
        
        # Calculated nutrition values
        self.total_energy = 0  # kcal/kg/day
        self.total_protein = 0  # g/kg/day
        self.total_carbohydrate = 0  # g/kg/day
        self.total_fat = 0  # g/kg/day
        self.total_sodium = 0  # mmol/kg/day
        self.total_potassium = 0  # mmol/kg/day
        self.total_calcium = 0  # mmol/kg/day
        self.total_phosphate = 0  # mmol/kg/day
        self.total_magnesium = 0  # mmol/kg/day
        self.glucose_infusion_rate = 0  # mg/kg/min
    
    def calculate_parenteral_volume(self):
        """Calculate total parenteral volume"""
        self.parenteral_volume = self.tpn_volume + self.lipid_volume + self.glucose_volume
        return self.parenteral_volume
    
    def calculate_total_fluid(self):
        """Calculate total fluid intake"""
        return self.enteral_volume + self.calculate_parenteral_volume()
```

## Nutrition Calculator
```python
class NutritionCalculator:
    def __init__(self, tpn_compositions, solution_compositions, fluid_requirements):
        self.tpn_compositions = tpn_compositions
        self.solution_compositions = solution_compositions
        self.fluid_requirements = fluid_requirements
    
    def calculate_fluid_requirements(self, patient):
        """Calculate fluid requirements based on patient data"""
        weight_category = patient.get_weight_category()
        age_category = patient.get_postnatal_age_category()
        
        # Get base fluid requirements
        if weight_category in self.fluid_requirements and age_category in self.fluid_requirements[weight_category]:
            base_req = self.fluid_requirements[weight_category][age_category]
            min_fluid = base_req["min"]
            max_fluid = base_req["max"]
            
            # Adjust for phototherapy if needed
            if patient.phototherapy:
                photo_adj = self.fluid_requirements["phototherapy_adjustment"][patient.phototherapy.lower()]
                min_fluid += photo_adj["min"]
                max_fluid += photo_adj["max"]
            
            return {"min": min_fluid, "max": max_fluid}
        else:
            return {"min": 0, "max": 0}
    
    def calculate_nutrition_values(self, nutrition_plan, patient):
        """Calculate all nutrition values based on the nutrition plan"""
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
        
        # Additional calculations for enteral feeding would go here
        
        return nutrition_plan
```

## Recommendation Engine
```python
class RecommendationEngine:
    def __init__(self, fluid_requirements, macronutrient_requirements):
        self.fluid_requirements = fluid_requirements
        self.macronutrient_requirements = macronutrient_requirements
    
    def generate_recommendations(self, patient, nutrition_plan):
        """Generate recommendations based on patient data and nutrition plan"""
        recommendations = []
        
        # Check fluid requirements
        fluid_req = self.calculate_fluid_requirements(patient)
        total_fluid = nutrition_plan.calculate_total_fluid()
        
        if total_fluid < fluid_req["min"]:
            recommendations.append(f"Increase total fluid intake to at least {fluid_req['min']} ml/kg/day")
        elif total_fluid > fluid_req["max"]:
            recommendations.append(f"Consider reducing total fluid intake to maximum {fluid_req['max']} ml/kg/day")
        
        # Check glucose infusion rate
        weight_category = patient.get_weight_category()
        age_category = patient.get_postnatal_age_category()
        
        # Additional checks for macronutrients, electrolytes, etc. would go here
        
        return recommendations
```
