# NICU Fluid Management App - Technical Documentation

## Architecture Overview

The NICU Fluid Management App follows a modular architecture with clear separation of concerns:

1. **Data Layer**: JSON files storing reference data for TPN compositions, solution compositions, and fluid requirements
2. **Model Layer**: Python classes representing patients and nutrition plans
3. **Business Logic Layer**: Calculator and recommendation engine for processing nutrition data
4. **Presentation Layer**: Web-based user interface with HTML, CSS, and JavaScript
5. **API Layer**: Flask server providing endpoints for the frontend to interact with the backend

## Directory Structure

```
nicu_app/
├── data/                      # Reference data in JSON format
│   ├── fluid_requirements.json
│   ├── solution_compositions.json
│   └── tpn_compositions.json
├── docs/                      # Documentation
│   ├── app_architecture.md
│   ├── data_model.md
│   ├── todo.md
│   ├── ui_design.md
│   └── user_documentation.md
├── src/                       # Source code
│   ├── models.py              # Data models
│   ├── calculator.py          # Calculation logic
│   ├── app.py                 # Main application class
│   ├── server.py              # Flask server
│   └── templates/             # Frontend templates
│       ├── index.html         # Main HTML template
│       └── static/            # Static assets
│           └── app.js         # Frontend JavaScript
├── start_app.sh               # Application startup script
└── test_integration.py        # Integration tests
```

## Component Details

### Data Models (models.py)

#### Patient Class
Represents a patient in the NICU with methods to determine weight and age categories.

Key attributes:
- `patient_id`: Unique identifier
- `gestational_age_at_birth`: In weeks
- `birth_weight`: In grams
- `current_weight`: In grams (uses birth weight if current is lower)
- `postnatal_age`: In days
- `phototherapy`: None, Single, or Double
- `clinical_condition`: Normal, Sepsis, Hyperglycemia, etc.

#### NutritionPlan Class
Represents a nutrition plan for a patient with methods to calculate volumes and feeding schedules.

Key attributes:
- `plan_id`: Unique identifier
- `patient_id`: Reference to patient
- `date`: Date of plan
- `total_fluid_target`: Target fluid volume in ml/kg/day
- `enteral_volume`: Volume of enteral feeding in ml/kg/day
- `tpn_type`: NICU-mix or Samenstelling_B
- `tpn_volume`: Volume of TPN in ml/kg/day
- `lipid_type`: Type of lipid solution
- `lipid_volume`: Volume of lipid solution in ml/kg/day
- `glucose_concentration`: Concentration of glucose solution
- `glucose_volume`: Volume of glucose solution in ml/kg/day
- Various calculated nutrition values (energy, protein, etc.)

### Calculation Logic (calculator.py)

#### NutritionCalculator Class
Performs calculations for fluid requirements and nutrition values.

Key methods:
- `calculate_fluid_requirements`: Determines fluid needs based on weight, age, and phototherapy
- `calculate_nutrition_values`: Calculates all nutrition values from the nutrition plan
- `calculate_glucose_infusion_rate`: Calculates GIR in mg/kg/min
- `get_macronutrient_requirements`: Determines macronutrient needs based on weight category

#### RecommendationEngine Class
Generates recommendations based on patient data and nutrition plan.

Key methods:
- `generate_recommendations`: Creates a list of recommendations based on calculated values and protocols

### Main Application (app.py)

#### NICUFluidApp Class
Coordinates between models, calculators, and user interface.

Key methods:
- `create_patient`: Creates a new patient record
- `create_nutrition_plan`: Creates a new nutrition plan
- `calculate_fluid_requirements`: Calculates fluid requirements for a patient
- `calculate_nutrition_values`: Calculates nutrition values for a plan
- `generate_recommendations`: Generates recommendations for a plan
- `get_feeding_schedule`: Creates a feeding schedule based on the plan
- `export_nutrition_plan`: Exports a plan to JSON format

### Web Server (server.py)

Flask application providing API endpoints for the frontend:
- `/`: Serves the main application page
- `/api/data/tpn_compositions`: Returns TPN composition data
- `/api/data/solution_compositions`: Returns solution composition data
- `/api/data/fluid_requirements`: Returns fluid requirement data
- `/api/patient`: Creates a new patient
- `/api/nutrition_plan`: Creates and calculates a nutrition plan
- `/api/export_plan/<plan_id>`: Exports a nutrition plan to JSON

### Frontend (templates/index.html, static/app.js)

The frontend is built with HTML, CSS (Bootstrap), and JavaScript:
- Tab-based interface with four main sections
- Real-time calculations for fluid volumes
- Interactive forms for patient and nutrition data
- Results dashboard with visualizations
- Printable feeding schedule

## Calculation Algorithms

### Fluid Requirements
1. Determine weight category based on current weight
2. Determine age category based on postnatal age
3. Look up base fluid requirements from reference data
4. Apply phototherapy adjustment if needed

### Nutrition Values
1. Calculate contribution from TPN based on volume and type
2. Calculate contribution from lipids based on volume and type
3. Calculate contribution from glucose based on volume and concentration
4. Calculate glucose infusion rate
5. Sum all contributions for total values

### Recommendations
1. Compare total fluid to recommended range
2. Compare glucose infusion rate to recommended range
3. Compare protein intake to recommended range
4. Compare fat intake to recommended range
5. Add special recommendations based on clinical condition

## Data Formats

### TPN Compositions
```json
{
  "NICU-mix": {
    "energy_kcal_per_ml": 0.29,
    "protein_g_per_ml": 0.0743,
    "sodium_mmol_per_ml": 0.0543,
    ...
  },
  "Samenstelling_B": {
    ...
  }
}
```

### Fluid Requirements
```json
{
  "fluid_requirements": {
    "term": {
      "day_1": {"min": 40, "max": 60},
      ...
    },
    "premature_greater_1500g": {
      ...
    },
    ...
    "phototherapy_adjustment": {
      "single": {"min": 10, "max": 20},
      "double": {"min": 20, "max": 30}
    }
  }
}
```

## Testing

The application includes integration tests that verify:
1. Patient creation with different weight categories
2. Fluid requirement calculations
3. Nutrition value calculations
4. Recommendation generation
5. Feeding schedule creation
6. Plan export functionality

## Deployment

The application is deployed as a local web server using Flask:
1. The `start_app.sh` script installs dependencies and starts the server
2. The server runs on localhost:5050
3. Users access the application through a web browser

## Future Enhancements

Potential areas for future development:
1. User authentication and role-based access
2. Patient data persistence with a database
3. Historical tracking of nutrition plans
4. Growth chart integration
5. Mobile application version
6. Integration with hospital information systems
