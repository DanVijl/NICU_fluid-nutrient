"""
NICU Fluid Management App - Data Models
"""

class Patient:
    """
    Patient model for NICU fluid management app.
    Stores patient information and provides methods for categorization.
    """
    def __init__(self, patient_id, gestational_age_at_birth, birth_weight, current_weight=None, 
                 postnatal_age=1, phototherapy=None, clinical_condition="Normal"):
        """
        Initialize a new Patient object.
        
        Args:
            patient_id: Unique identifier for the patient
            gestational_age_at_birth: Gestational age in weeks at birth
            birth_weight: Weight in grams at birth
            current_weight: Current weight in grams (if lower than birth weight, birth weight will be used)
            postnatal_age: Age in days since birth
            phototherapy: None, "Single", or "Double" (affects fluid requirements)
            clinical_condition: "Normal", "Sepsis", "Hyperglycemia", etc. (affects nutrient requirements)
        """
        self.patient_id = patient_id
        self.gestational_age_at_birth = gestational_age_at_birth  # in weeks
        self.birth_weight = birth_weight  # in grams
        self.current_weight = current_weight if current_weight and current_weight > birth_weight else birth_weight  # in grams
        self.postnatal_age = postnatal_age  # in days
        self.phototherapy = phototherapy  # None, "Single", or "Double"
        self.clinical_condition = clinical_condition  # "Normal", "Sepsis", "Hyperglycemia", etc.
    
    def get_weight_category(self):
        """
        Determine weight category for fluid and nutrient calculations.
        
        Returns:
            String representing weight category: "premature_less_1000g", "premature_1000_1500g", 
            "premature_greater_1500g", or "term"
        """
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
        """
        Determine postnatal age category for fluid requirements.
        
        Returns:
            String representing age category: "day_1", "day_2", etc.
        """
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


class NutritionPlan:
    """
    Nutrition Plan model for NICU fluid management app.
    Stores nutrition plan details and provides methods for calculations.
    """
    def __init__(self, plan_id, patient_id, date, total_fluid_target=None,
                 enteral_volume=0, tpn_type="NICU-mix", tpn_volume=0,
                 lipid_type="Intralipid_20%", lipid_volume=0,
                 glucose_concentration="10%", glucose_volume=0,
                 enteral_feeding_type=None, enteral_feeding_frequency=None,
                 bmf_concentration=0):
        """
        Initialize a new NutritionPlan object.
        
        Args:
            plan_id: Unique identifier for the nutrition plan
            patient_id: Reference to the patient
            date: Date of the nutrition plan
            total_fluid_target: Target fluid volume in ml/kg/day
            enteral_volume: Volume of enteral feeding in ml/kg/day
            tpn_type: "NICU-mix" or "Samenstelling_B"
            tpn_volume: Volume of TPN in ml/kg/day
            lipid_type: "Intralipid_20%" or "SMOF_20%"
            lipid_volume: Volume of lipid solution in ml/kg/day
            glucose_concentration: Concentration of glucose solution (e.g., "5%", "10%")
            glucose_volume: Volume of glucose solution in ml/kg/day
            enteral_feeding_type: "Breast milk", "Donor milk", etc.
            enteral_feeding_frequency: Number of feedings per 24 hours
            bmf_concentration: Breast milk fortifier concentration in g/100ml
        """
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
        """
        Calculate total parenteral volume.
        
        Returns:
            Total parenteral volume in ml/kg/day
        """
        self.parenteral_volume = self.tpn_volume + self.lipid_volume + self.glucose_volume
        return self.parenteral_volume
    
    def calculate_total_fluid(self):
        """
        Calculate total fluid intake.
        
        Returns:
            Total fluid intake in ml/kg/day
        """
        return self.enteral_volume + self.calculate_parenteral_volume()
    
    def get_feeding_volume_per_feed(self):
        """
        Calculate volume per feed based on total enteral volume and feeding frequency.
        
        Returns:
            Volume per feed in ml/kg or None if frequency is not set
        """
        if self.enteral_feeding_frequency and self.enteral_feeding_frequency > 0:
            return self.enteral_volume / self.enteral_feeding_frequency
        return None
