# NICU Fluid Management App Architecture

## Overview
The NICU Fluid Management App will assist healthcare providers in calculating and managing fluid, feeding, and nutrient intake for neonates in the NICU. The app will account for key dependencies such as gestational age, weight, and postnatal age, while balancing enteral and parenteral nutrition requirements.

## Data Model

### Patient Data
- `patient_id`: Unique identifier for the patient
- `gestational_age_at_birth`: Gestational age in weeks at birth
- `birth_weight`: Weight in grams at birth
- `current_weight`: Current weight in grams (if lower than birth weight, birth weight will be used)
- `postnatal_age`: Age in days since birth
- `phototherapy`: None, Single, or Double (affects fluid requirements)
- `clinical_condition`: Normal, Sepsis, Hyperglycemia, etc. (affects nutrient requirements)

### Nutrition Plan
- `plan_id`: Unique identifier for the nutrition plan
- `patient_id`: Reference to the patient
- `date`: Date of the nutrition plan
- `total_fluid_target`: Target fluid volume in ml/kg/day
- `enteral_volume`: Volume of enteral feeding in ml/kg/day
- `parenteral_volume`: Volume of parenteral nutrition in ml/kg/day
- `tpn_type`: NICU-mix or Samenstelling B
- `tpn_volume`: Volume of TPN in ml/kg/day
- `lipid_type`: Type of lipid solution (Intralipid 20%, SMOF 20%)
- `lipid_volume`: Volume of lipid solution in ml/kg/day
- `glucose_concentration`: Concentration of glucose solution (%)
- `glucose_volume`: Volume of glucose solution in ml/kg/day
- `enteral_feeding_type`: Breast milk, Donor milk, Premature formula, etc.
- `enteral_feeding_frequency`: Number of feedings per 24 hours
- `bmf_concentration`: Breast milk fortifier concentration in g/100ml (if applicable)

### Calculated Nutrition Values
- `total_energy`: Total energy intake in kcal/kg/day
- `total_protein`: Total protein intake in g/kg/day
- `total_carbohydrate`: Total carbohydrate intake in g/kg/day
- `total_fat`: Total fat intake in g/kg/day
- `total_sodium`: Total sodium intake in mmol/kg/day
- `total_potassium`: Total potassium intake in mmol/kg/day
- `total_calcium`: Total calcium intake in mmol/kg/day
- `total_phosphate`: Total phosphate intake in mmol/kg/day
- `total_magnesium`: Total magnesium intake in mmol/kg/day
- `glucose_infusion_rate`: Glucose infusion rate in mg/kg/min

## Application Architecture

### Core Components
1. **User Interface Layer**
   - Patient Data Entry Form
   - Nutrition Plan Form
   - Results Display
   - Recommendations View

2. **Business Logic Layer**
   - Patient Manager: Handles patient data and validation
   - Nutrition Calculator: Performs all nutrition calculations
   - Recommendation Engine: Provides suggestions based on protocols
   - Validation Service: Ensures all inputs and calculations are valid

3. **Data Layer**
   - Patient Repository: Stores patient information
   - Nutrition Plan Repository: Stores nutrition plans
   - Reference Data Repository: Stores TPN compositions, fluid requirements, etc.

### Key Modules
1. **Fluid Calculator Module**
   - Calculates fluid requirements based on weight category and postnatal age
   - Adjusts for phototherapy if needed
   - Balances enteral and parenteral fluid volumes

2. **Nutrient Calculator Module**
   - Calculates nutrient intake from both enteral and parenteral sources
   - Ensures requirements for glucose, protein, and lipids are met
   - Calculates electrolyte intake and balance

3. **TPN Composition Module**
   - Manages TPN composition data (NICU-mix and Samenstelling B)
   - Calculates nutrient intake based on TPN volume and type

4. **Enteral Feeding Module**
   - Manages enteral feeding types and schedules
   - Calculates nutrient intake from enteral sources
   - Handles breast milk fortification calculations

5. **Recommendation Module**
   - Provides recommendations based on protocols
   - Suggests adjustments when requirements are not met
   - Alerts for potential issues (e.g., excessive glucose, insufficient protein)

## Technology Stack
- Frontend: Web-based interface using HTML, CSS, JavaScript
- Backend: Python with Flask framework
- Data Storage: JSON files for reference data, SQLite for patient data
- Deployment: Web application with responsive design for desktop and mobile use
