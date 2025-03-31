# NICU Fluid Management App - User Interface Design

## Overview
The user interface for the NICU Fluid Management App will be designed to be intuitive, efficient, and error-resistant for healthcare providers in the NICU setting. The interface will allow for quick data entry while providing clear visualization of calculated results and recommendations.

## Main Screens

### 1. Patient Information Screen
- **Patient Demographics Section**
  - Patient ID/Name
  - Date of Birth
  - Gestational Age at Birth (weeks)
  - Birth Weight (grams)
  - Current Weight (grams)
  - Postnatal Age (days) - auto-calculated or manually entered
  
- **Clinical Status Section**
  - Phototherapy (None/Single/Double)
  - Clinical Condition (Normal, Sepsis, Hyperglycemia, etc.)
  - Additional Notes

### 2. Nutrition Planning Screen
- **Fluid Requirements Section**
  - Calculated Fluid Requirements (min-max range)
  - Target Total Fluid Volume (ml/kg/day)
  
- **Parenteral Nutrition Section**
  - TPN Type Selection (NICU-mix/Samenstelling B)
  - TPN Volume (ml/kg/day)
  - Lipid Type Selection (Intralipid 20%/SMOF 20%)
  - Lipid Volume (ml/kg/day)
  - Glucose Concentration Selection (5%, 10%, etc.)
  - Glucose Volume (ml/kg/day)
  - Total Parenteral Volume (auto-calculated)
  
- **Enteral Nutrition Section**
  - Enteral Feeding Type (Breast milk, Donor milk, Formula type)
  - Enteral Volume (ml/kg/day)
  - Feeding Frequency (feeds per 24 hours)
  - Breast Milk Fortifier (if applicable)
  - BMF Concentration (g/100ml)

### 3. Results Dashboard
- **Summary Section**
  - Total Fluid Intake (ml/kg/day)
  - Parenteral/Enteral Ratio
  
- **Nutrient Intake Section**
  - Energy (kcal/kg/day)
  - Protein (g/kg/day)
  - Carbohydrates (g/kg/day)
  - Fat (g/kg/day)
  - Glucose Infusion Rate (mg/kg/min)
  
- **Electrolyte Intake Section**
  - Sodium (mmol/kg/day)
  - Potassium (mmol/kg/day)
  - Calcium (mmol/kg/day)
  - Phosphate (mmol/kg/day)
  - Magnesium (mmol/kg/day)
  
- **Recommendations Section**
  - Auto-generated recommendations based on protocols
  - Alerts for values outside recommended ranges

### 4. Feeding Schedule Screen
- **Schedule Generator**
  - Based on total enteral volume and feeding frequency
  - Volume per feed (ml)
  - Timing of feeds
  
- **Printable Schedule**
  - For nursing staff to follow

## UI Components

### Navigation
- Tab-based navigation between main screens
- Persistent patient information header
- Save/Load buttons for nutrition plans

### Input Controls
- Number inputs with min/max validation
- Dropdown selectors for categorical data
- Radio buttons for binary choices
- Date pickers for dates

### Visualization
- Progress bars for fluid volumes (showing target range)
- Charts comparing actual vs. recommended nutrient intake
- Color coding for values outside recommended ranges

### Responsive Design
- Optimized for both desktop and tablet use in clinical settings
- Printable reports for documentation

## Workflow

1. User enters or selects patient information
2. System calculates recommended fluid volumes based on weight and age
3. User enters planned parenteral and enteral nutrition components
4. System calculates total nutrient intake and displays results
5. System generates recommendations if values are outside recommended ranges
6. User adjusts plan as needed until satisfied
7. User saves plan and/or prints reports

## Error Prevention
- Input validation to prevent impossible values
- Warnings for unusual values that are still possible
- Confirmation dialogs for potentially dangerous combinations
- Auto-calculation where possible to reduce manual entry errors
