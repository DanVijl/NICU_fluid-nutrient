# NICU Fluid Management App - User Documentation

## Overview

The NICU Fluid Management App is designed to assist healthcare providers in calculating and managing fluid, feeding, and nutrient intake for neonates in the NICU. The application accounts for key dependencies such as gestational age, weight, and postnatal age, while balancing enteral and parenteral nutrition requirements.

This application helps manage babies from 400 grams up to 7 kg, taking into consideration various factors that influence potential intake, including daily glucose, lipid and protein requirements, phototherapy, and the balance between enteral and parenteral feeding.

## Getting Started

### System Requirements
- Modern web browser (Chrome, Firefox, Safari, or Edge)
- Internet connection

### Starting the Application
1. Navigate to the application directory
2. Run the start script:
   ```
   ./start_app.sh
   ```
3. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Using the Application

The application is organized into four main tabs:

### 1. Patient Information

In this tab, you'll enter the patient's basic information:

- **Patient Demographics**
  - Patient ID
  - Date of Birth
  - Gestational Age at Birth (weeks)
  - Birth Weight (grams)
  - Current Weight (grams) - Note: If lower than birth weight, birth weight will be used
  - Postnatal Age (days)

- **Clinical Status**
  - Phototherapy (None/Single/Double)
  - Clinical Condition (Normal, Sepsis, Hyperglycemia, etc.)
  - Additional Notes

After entering all required information, click "Save Patient Information" to proceed to the Nutrition Planning tab.

### 2. Nutrition Planning

This tab allows you to plan the patient's nutrition:

- **Fluid Requirements**
  - The system automatically calculates the recommended fluid range based on the patient's weight category and postnatal age
  - Enter the target total fluid volume

- **Parenteral Nutrition**
  - Select TPN Type (NICU-mix or Samenstelling B)
  - Enter TPN Volume (ml/kg/day)
  - Select Lipid Type (Intralipid 20% or SMOF 20%)
  - Enter Lipid Volume (ml/kg/day)
  - Select Glucose Concentration (5%, 10%, 12.5%, etc.)
  - Enter Glucose Volume (ml/kg/day)

- **Enteral Nutrition**
  - Select Enteral Feeding Type (Breast milk, Donor milk, Formula)
  - Enter Enteral Volume (ml/kg/day)
  - Select Feeding Frequency (feeds per 24 hours)
  - Enter BMF Concentration (g/100ml) if applicable

The system will display the total fluid intake and a progress bar showing where it falls within the recommended range. Click "Calculate Nutrition Values" to proceed to the Results Dashboard.

### 3. Results Dashboard

This tab displays the calculated nutrition values:

- **Summary**
  - Total Fluid Intake (ml/kg/day)
  - Parenteral/Enteral Ratio

- **Nutrient Intake**
  - Energy (kcal/kg/day)
  - Protein (g/kg/day)
  - Carbohydrates (g/kg/day)
  - Fat (g/kg/day)
  - Glucose Infusion Rate (mg/kg/min)

- **Electrolyte Intake**
  - Sodium (mmol/kg/day)
  - Potassium (mmol/kg/day)
  - Calcium (mmol/kg/day)
  - Phosphate (mmol/kg/day)
  - Magnesium (mmol/kg/day)

- **Recommendations**
  - The system generates recommendations based on the protocols
  - Alerts for values outside recommended ranges

You can export the nutrition plan by clicking "Export Nutrition Plan".

### 4. Feeding Schedule

This tab displays the feeding schedule based on the enteral volume and feeding frequency:

- Schedule showing feeding times and volumes
- Option to print the schedule for nursing staff

## TPN Compositions

The application uses two types of TPN:

### NICU-mix
- Energy: 0.29 kcal/ml
- Protein: 0.0743 g/ml
- Sodium: 0.0543 mmol/ml
- Potassium: 0.0714 mmol/ml
- Calcium: 0.0257 mmol/ml
- Phosphate: 0.0343 mmol/ml
- Magnesium: 0.00429 mmol/ml

### Samenstelling B
- Energy: 0.29 kcal/ml
- Protein: 0.0743 g/ml
- Sodium: 0.00714 mmol/ml
- Potassium: 0.0171 mmol/ml
- Calcium: 0.0257 mmol/ml
- Phosphate: 0.0214 mmol/ml
- Magnesium: 0.00571 mmol/ml

## Fluid Requirements

The application calculates fluid requirements based on weight category and postnatal age:

### Term Infants
- Day 1: 40-60 ml/kg/day
- Day 2: 50-70 ml/kg/day
- Day 3: 60-80 ml/kg/day
- Day 4: 60-100 ml/kg/day
- Days 5-7: 100-140 ml/kg/day
- Days 8-14: 140-170 ml/kg/day
- Days 15+: 140-160 ml/kg/day

### Premature Infants >1500g
- Day 1: 60-80 ml/kg/day
- Day 2: 80-100 ml/kg/day
- Day 3: 100-120 ml/kg/day
- Day 4: 120-140 ml/kg/day
- Days 5-7: 140-160 ml/kg/day
- Days 8-14: 140-160 ml/kg/day
- Days 15+: 140-160 ml/kg/day

### Premature Infants 1000-1500g
- Day 1: 70-90 ml/kg/day
- Day 2: 90-110 ml/kg/day
- Day 3: 110-130 ml/kg/day
- Day 4: 130-150 ml/kg/day
- Days 5-7: 160-180 ml/kg/day
- Days 8-14: 140-160 ml/kg/day
- Days 15+: 140-160 ml/kg/day

### Premature Infants <1000g
- Day 1: 80-100 ml/kg/day
- Day 2: 100-120 ml/kg/day
- Day 3: 120-140 ml/kg/day
- Day 4: 140-160 ml/kg/day
- Days 5-7: 160-180 ml/kg/day
- Days 8-14: 140-160 ml/kg/day
- Days 15+: 140-160 ml/kg/day

### Phototherapy Adjustment
- Single phototherapy: Add 10-20 ml/kg/day
- Double phototherapy: Add 20-30 ml/kg/day

## Troubleshooting

### Common Issues

1. **Application doesn't start**
   - Ensure Python and required packages are installed
   - Check if port 5000 is already in use

2. **Calculations seem incorrect**
   - Verify patient weight and age are entered correctly
   - Check that all volumes are entered in ml/kg/day

3. **Recommendations don't appear**
   - Ensure you've clicked "Calculate Nutrition Values"
   - Check that all required fields are filled

### Support

For additional support or to report issues, please contact the development team.

## Technical Information

The NICU Fluid Management App is built using:
- Frontend: HTML, CSS, JavaScript with Bootstrap
- Backend: Python with Flask framework
- Data Storage: JSON files for reference data

## Acknowledgments

This application was developed based on the protocols provided by the NICU department, including:
- Protocol parenterale voeding op de NICU (Versie 6)
- N3 aanbeveling 2024 enterale voeding
