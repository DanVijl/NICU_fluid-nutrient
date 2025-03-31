/**
 * NICU Fluid Management App - JavaScript
 */

// Global variables
let patient = null;
let nutritionPlan = null;
let fluidRequirements = null;
let tpnCompositions = null;
let solutionCompositions = null;

// Load reference data
async function loadReferenceData() {
    try {
        const tpnResponse = await fetch('/api/data/tpn_compositions');
        tpnCompositions = await tpnResponse.json();
        
        const solutionResponse = await fetch('/api/data/solution_compositions');
        solutionCompositions = await solutionResponse.json();
        
        console.log('Reference data loaded successfully');
    } catch (error) {
        console.error('Error loading reference data:', error);
        alert('Failed to load reference data. Please refresh the page.');
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Load reference data
    loadReferenceData();
    
    // Set up event listeners
    document.getElementById('patientForm').addEventListener('submit', savePatientInfo);
    document.getElementById('calculateButton').addEventListener('click', calculateNutrition);
    document.getElementById('exportButton').addEventListener('click', exportNutritionPlan);
    document.getElementById('printScheduleButton').addEventListener('click', printSchedule);
    
    // Set up input change listeners for real-time calculations
    document.getElementById('tpnVolume').addEventListener('input', updateTotalVolumes);
    document.getElementById('lipidVolume').addEventListener('input', updateTotalVolumes);
    document.getElementById('glucoseVolume').addEventListener('input', updateTotalVolumes);
    document.getElementById('enteralVolume').addEventListener('input', updateTotalVolumes);
    
    // Initialize date fields
    document.getElementById('dateOfBirth').valueAsDate = new Date();
    document.getElementById('scheduleDate').textContent = new Date().toLocaleDateString();
});

// Save patient information
function savePatientInfo(event) {
    event.preventDefault();
    
    // Create patient object
    patient = {
        patientId: document.getElementById('patientId').value,
        dateOfBirth: document.getElementById('dateOfBirth').value,
        gestationalAge: parseFloat(document.getElementById('gestationalAge').value),
        birthWeight: parseInt(document.getElementById('birthWeight').value),
        currentWeight: parseInt(document.getElementById('currentWeight').value) || parseInt(document.getElementById('birthWeight').value),
        postnatalAge: parseInt(document.getElementById('postnatalAge').value),
        phototherapy: document.querySelector('input[name="phototherapy"]:checked').value,
        clinicalCondition: document.getElementById('clinicalCondition').value,
        additionalNotes: document.getElementById('additionalNotes').value
    };
    
    // Use birth weight if current weight is lower
    if (patient.currentWeight < patient.birthWeight) {
        patient.currentWeight = patient.birthWeight;
        document.getElementById('currentWeight').value = patient.birthWeight;
    }
    
    // Calculate fluid requirements
    calculateFluidRequirements();
    
    // Show nutrition planning tab
    document.getElementById('patientInfoAlert').style.display = 'none';
    document.getElementById('nutritionContent').style.display = 'block';
    document.getElementById('nutrition-tab').click();
    
    // Update patient weight in schedule tab
    document.getElementById('patientWeight').textContent = patient.currentWeight;
    
    console.log('Patient information saved:', patient);
}

// Calculate fluid requirements based on patient data
function calculateFluidRequirements() {
    // Determine weight category
    let weightCategory;
    if (patient.currentWeight < 1000) {
        weightCategory = 'premature_less_1000g';
    } else if (patient.currentWeight < 1500) {
        weightCategory = 'premature_1000_1500g';
    } else if (patient.currentWeight < 2500) {
        weightCategory = 'premature_greater_1500g';
    } else {
        weightCategory = 'term';
    }
    
    // Determine age category
    let ageCategory;
    if (patient.postnatalAge === 1) {
        ageCategory = 'day_1';
    } else if (patient.postnatalAge === 2) {
        ageCategory = 'day_2';
    } else if (patient.postnatalAge === 3) {
        ageCategory = 'day_3';
    } else if (patient.postnatalAge === 4) {
        ageCategory = 'day_4';
    } else if (patient.postnatalAge >= 5 && patient.postnatalAge <= 7) {
        ageCategory = 'day_5_7';
    } else if (patient.postnatalAge >= 8 && patient.postnatalAge <= 14) {
        ageCategory = 'day_8_14';
    } else {
        ageCategory = 'day_15_plus';
    }
    
    // Mock fluid requirements (would be replaced with actual API call)
    const mockFluidRequirements = {
        'term': {
            'day_1': {min: 40, max: 60},
            'day_2': {min: 50, max: 70},
            'day_3': {min: 60, max: 80},
            'day_4': {min: 60, max: 100},
            'day_5_7': {min: 100, max: 140},
            'day_8_14': {min: 140, max: 170},
            'day_15_plus': {min: 140, max: 160}
        },
        'premature_greater_1500g': {
            'day_1': {min: 60, max: 80},
            'day_2': {min: 80, max: 100},
            'day_3': {min: 100, max: 120},
            'day_4': {min: 120, max: 140},
            'day_5_7': {min: 140, max: 160},
            'day_8_14': {min: 140, max: 160},
            'day_15_plus': {min: 140, max: 160}
        },
        'premature_1000_1500g': {
            'day_1': {min: 70, max: 90},
            'day_2': {min: 90, max: 110},
            'day_3': {min: 110, max: 130},
            'day_4': {min: 130, max: 150},
            'day_5_7': {min: 160, max: 180},
            'day_8_14': {min: 140, max: 160},
            'day_15_plus': {min: 140, max: 160}
        },
        'premature_less_1000g': {
            'day_1': {min: 80, max: 100},
            'day_2': {min: 100, max: 120},
            'day_3': {min: 120, max: 140},
            'day_4': {min: 140, max: 160},
            'day_5_7': {min: 160, max: 180},
            'day_8_14': {min: 140, max: 160},
            'day_15_plus': {min: 140, max: 160}
        },
        'phototherapy_adjustment': {
            'single': {min: 10, max: 20},
            'double': {min: 20, max: 30}
        }
    };
    
    // Get base fluid requirements
    fluidRequirements = {
        min: mockFluidRequirements[weightCategory][ageCategory].min,
        max: mockFluidRequirements[weightCategory][ageCategory].max
    };
    
    // Adjust for phototherapy
    if (patient.phototherapy !== 'None') {
        const photoType = patient.phototherapy.toLowerCase();
        fluidRequirements.min += mockFluidRequirements.phototherapy_adjustment[photoType].min;
        fluidRequirements.max += mockFluidRequirements.phototherapy_adjustment[photoType].max;
    }
    
    // Update UI
    document.getElementById('minFluid').textContent = fluidRequirements.min;
    document.getElementById('maxFluid').textContent = fluidRequirements.max;
    document.getElementById('totalFluidTarget').value = Math.round((fluidRequirements.min + fluidRequirements.max) / 2);
    
    return fluidRequirements;
}

// Update total volumes when inputs change
function updateTotalVolumes() {
    const tpnVolume = parseFloat(document.getElementById('tpnVolume').value) || 0;
    const lipidVolume = parseFloat(document.getElementById('lipidVolume').value) || 0;
    const glucoseVolume = parseFloat(document.getElementById('glucoseVolume').value) || 0;
    const enteralVolume = parseFloat(document.getElementById('enteralVolume').value) || 0;
    
    const totalParenteral = tpnVolume + lipidVolume + glucoseVolume;
    const totalFluid = totalParenteral + enteralVolume;
    
    document.getElementById('totalParenteralVolume').textContent = totalParenteral.toFixed(1);
    document.getElementById('totalFluid').textContent = totalFluid.toFixed(1);
    
    // Update progress bar
    if (fluidRequirements) {
        const percentage = Math.min(100, Math.round((totalFluid / fluidRequirements.max) * 100));
        document.getElementById('fluidProgressBar').style.width = percentage + '%';
        document.getElementById('fluidProgressBar').textContent = percentage + '%';
        document.getElementById('fluidProgressBar').setAttribute('aria-valuenow', percentage);
        
        // Change color based on whether it's within range
        if (totalFluid < fluidRequirements.min) {
            document.getElementById('fluidProgressBar').className = 'progress-bar bg-warning';
        } else if (totalFluid > fluidRequirements.max) {
            document.getElementById('fluidProgressBar').className = 'progress-bar bg-danger';
        } else {
            document.getElementById('fluidProgressBar').className = 'progress-bar bg-success';
        }
    }
}

// Calculate nutrition values
function calculateNutrition() {
    if (!patient) {
        alert('Please complete patient information first.');
        return;
    }
    
    // Create nutrition plan object
    nutritionPlan = {
        planId: 'NP-' + patient.patientId,
        patientId: patient.patientId,
        date: new Date().toISOString().split('T')[0],
        totalFluidTarget: parseFloat(document.getElementById('totalFluidTarget').value) || 0,
        tpnType: document.getElementById('tpnType').value,
        tpnVolume: parseFloat(document.getElementById('tpnVolume').value) || 0,
        lipidType: document.getElementById('lipidType').value,
        lipidVolume: parseFloat(document.getElementById('lipidVolume').value) || 0,
        glucoseConcentration: document.getElementById('glucoseConcentration').value,
        glucoseVolume: parseFloat(document.getElementById('glucoseVolume').value) || 0,
        enteralFeedingType: document.getElementById('enteralFeedingType').value,
        enteralVolume: parseFloat(document.getElementById('enteralVolume').value) || 0,
        enteralFeedingFrequency: parseInt(document.getElementById('feedingFrequency').value) || 0,
        bmfConcentration: parseFloat(document.getElementById('bmfConcentration').value) || 0,
        
        // Calculated values
        totalEnergy: 0,
        totalProtein: 0,
        totalCarbohydrate: 0,
        totalFat: 0,
        totalSodium: 0,
        totalPotassium: 0,
        totalCalcium: 0,
        totalPhosphate: 0,
        totalMagnesium: 0,
        glucoseInfusionRate: 0
    };
    
    // Mock TPN compositions (would be replaced with actual data from API)
    const mockTpnCompositions = {
        'NICU-mix': {
            energy_kcal_per_ml: 0.29,
            protein_g_per_ml: 0.0743,
            carbohydrate_g_per_ml: 0.0,
            fat_g_per_ml: 0.0,
            sodium_mmol_per_ml: 0.0543,
            potassium_mmol_per_ml: 0.0714,
            calcium_mmol_per_ml: 0.0257,
            phosphate_mmol_per_ml: 0.0343,
            magnesium_mmol_per_ml: 0.00429
        },
        'Samenstelling_B': {
            energy_kcal_per_ml: 0.29,
            protein_g_per_ml: 0.0743,
            carbohydrate_g_per_ml: 0.0,
            fat_g_per_ml: 0.0,
            sodium_mmol_per_ml: 0.00714,
            potassium_mmol_per_ml: 0.0171,
            calcium_mmol_per_ml: 0.0257,
            phosphate_mmol_per_ml: 0.0214,
            magnesium_mmol_per_ml: 0.00571
        }
    };
    
    // Mock solution compositions
    const mockSolutionCompositions = {
        glucose_solutions: {
            '5%': { energy_kcal_per_ml: 0.2, carbohydrate_g_per_ml: 0.05 },
            '10%': { energy_kcal_per_ml: 0.4, carbohydrate_g_per_ml: 0.1 },
            '12.5%': { energy_kcal_per_ml: 0.5, carbohydrate_g_per_ml: 0.125 },
            '15%': { energy_kcal_per_ml: 0.6, carbohydrate_g_per_ml: 0.15 },
            '17.5%': { energy_kcal_per_ml: 0.7, carbohydrate_g_per_ml: 0.175 },
            '20%': { energy_kcal_per_ml: 0.8, carbohydrate_g_per_ml: 0.2 },
            '25%': { energy_kcal_per_ml: 1.0, carbohydrate_g_per_ml: 0.25 }
        },
        lipid_solutions: {
            'Intralipid_20%': { energy_kcal_per_ml: 1.8, fat_g_per_ml: 0.2 },
            'SMOF_20%': { energy_kcal_per_ml: 1.8, fat_g_per_ml: 0.2 }
        }
    };
    
    // Use actual data if available, otherwise use mock data
    const tpnData = tpnCompositions || mockTpnCompositions;
    const solutionData = solutionCompositions || mockSolutionCompositions;
    
    // Calculate from TPN
    if (nutritionPlan.tpnVolume > 0) {
        const tpn = tpnData[nutritionPlan.tpnType];
        nutritionPlan.totalEnergy += tpn.energy_kcal_per_ml * nutritionPlan.tpnVolume;
        nutritionPlan.totalProtein += tpn.protein_g_per_ml * nutritionPlan.tpnVolume;
        nutritionPlan.totalCarbohydrate += tpn.carbohydrate_g_per_ml * nutritionPlan.tpnVolume;
        nutritionPlan.totalFat += tpn.fat_g_per_ml * nutritionPlan.tpnVolume;
        nutritionPlan.totalSodium += tpn.sodium_mmol_per_ml * nutritionPlan.tpnVolume;
        nutritionPlan.totalPotassium += tpn.potassium_mmol_per_ml * nutritionPlan.tpnVolume;
        nutritionPlan.totalCalcium += tpn.calcium_mmol_per_ml * nutritionPlan.tpnVolume;
        nutritionPlan.totalPhosphate += tpn.phosphate_mmol_per_ml * nutritionPlan.tpnVolume;
        nutritionPlan.totalMagnesium += tpn.magnesium_mmol_per_ml * nutritionPlan.tpnVolume;
    }
    
    // Calculate from lipids
    if (nutritionPlan.lipidVolume > 0) {
        const lipid = solutionData.lipid_solutions[nutritionPlan.lipidType];
        nutritionPlan.totalEnergy += lipid.energy_kcal_per_ml * nutritionPlan.lipidVolume;
        nutritionPlan.totalFat += lipid.fat_g_per_ml * nutritionPlan.lipidVolume;
    }
    
    // Calculate from glucose
    if (nutritionPlan.glucoseVolume > 0) {
        const glucose = solutionData.glucose_solutions[nutritionPlan.glucoseConcentration];
        nutritionPlan.totalEnergy += glucose.energy_kcal_per_ml * nutritionPlan.glucoseVolume;
        nutritionPlan.totalCarbohydrate += glucose.carbohydrate_g_per_ml * nutritionPlan.glucoseVolume;
        
        // Calculate glucose infusion rate (mg/kg/min)
        const glucoseConcentrationPercent = parseFloat(nutritionPlan.glucoseConcentration.replace('%', ''));
        const glucoseMgPerMl = glucoseConcentrationPercent * 10; // Convert % to mg/ml
        const totalGlucoseMg = glucoseMgPerMl * nutritionPlan.glucoseVolume;
        nutritionPlan.glucoseInfusionRate = totalGlucoseMg / (24 * 60); // Convert to mg/kg/min
    }
    
    // Update results UI
    updateResultsUI();
    
    // Generate recommendations
    generateRecommendations();
    
    // Update feeding schedule
    updateFeedingSchedule();
    
    // Show results tab
    document.getElementById('calculationAlert').style.display = 'none';
    document.getElementById('resultsContent').style.display = 'block';
    document.getElementById('scheduleAlert').style.display = 'none';
    document.getElementById('scheduleContent').style.display = 'block';
    document.getElementById('results-tab').click();
    
    console.log('Nutrition plan calculated:', nutritionPlan);
}

// Update results UI
function updateResultsUI() {
    // Calculate total volumes
    const totalParenteral = nutritionPlan.tpnVolume + nutritionPlan.lipidVolume + nutritionPlan.glucoseVolume;
    const totalFluid = totalParenteral + nutritionPlan.enteralVolume;
    
    // Update summary section
    document.getElementById('resultTotalFluid').textContent = totalFluid.toFixed(1);
    document.getElementById('resultParenteralVolume').textContent = totalParenteral.toFixed(1);
    document.getElementById('resultEnteralVolume').textContent = nutritionPlan.enteralVolume.toFixed(1);
    
    // Calculate percentages
    const parenteralPercent = totalFluid > 0 ? Math.round((totalParenteral / totalFluid) * 100) : 0;
    const enteralPercent = totalFluid > 0 ? Math.round((nutritionPlan.enteralVolume / totalFluid) * 100) : 0;
    
    document.getElementById('resultParenteralPercent').textContent = parenteralPercent;
    document.getElementById('resultEnteralPercent').textContent = enteralPercent;
    
    // Update progress bars
    document.getElementById('resultFluidProgressBar').style.width = Math.min(100, Math.round((totalFluid / fluidRequirements.max) * 100)) + '%';
    document.getElementById('parenteralProgressBar').style.width = parenteralPercent + '%';
    document.getElementById('enteralProgressBar').style.width = enteralPercent + '%';
    
    // Update nutrient values
    document.getElementById('resultEnergy').textContent = nutritionPlan.totalEnergy.toFixed(2);
    document.getElementById('resultProtein').textContent = nutritionPlan.totalProtein.toFixed(2);
    document.getElementById('resultCarbohydrate').textContent = nutritionPlan.totalCarbohydrate.toFixed(2);
    document.getElementById('resultFat').textContent = nutritionPlan.totalFat.toFixed(2);
    document.getElementById('resultGIR').textContent = nutritionPlan.glucoseInfusionRate.toFixed(2);
    
    // Update electrolyte values
    document.getElementById('resultSodium').textContent = nutritionPlan.totalSodium.toFixed(3);
    document.getElementById('resultPotassium').textContent = nutritionPlan.totalPotassium.toFixed(3);
    document.getElementById('resultCalcium').textContent = nutritionPlan.totalCalcium.toFixed(3);
    document.getElementById('resultPhosphate').textContent = nutritionPlan.totalPhosphate.toFixed(3);
    document.getElementById('resultMagnesium').textContent = nutritionPlan.totalMagnesium.toFixed(3);
}

// Generate recommendations
function generateRecommendations() {
    const recommendations = [];
    
    // Calculate total volumes
    const totalParenteral = nutritionPlan.tpnVolume + nutritionPlan.lipidVolume + nutritionPlan.glucoseVolume;
    const totalFluid = totalParenteral + nutritionPlan.enteralVolume;
    
    // Check fluid requirements
    if (totalFluid < fluidRequirements.min) {
        recommendations.push(`Increase total fluid intake to at least ${fluidRequirements.min} ml/kg/day (current: ${totalFluid.toFixed(1)} ml/kg/day)`);
    } else if (totalFluid > fluidRequirements.max) {
        recommendations.push(`Consider reducing total fluid intake to maximum ${fluidRequirements.max} ml/kg/day (current: ${totalFluid.toFixed(1)} ml/kg/day)`);
    }
    
    // Mock macronutrient requirements based on weight category
    let macroReq;
    if (patient.currentWeight < 1000) {
        macroReq = {
            glucose_mg_kg_min: {min: 4, max: 12},
            protein_g_kg_day: {min: 2.5, max: 3.5},
            fat_g_kg_day: {min: 2.5, max: 3.5}
        };
    } else if (patient.currentWeight < 1500) {
        macroReq = {
            glucose_mg_kg_min: {min: 4, max: 12},
            protein_g_kg_day: {min: 2.5, max: 3.5},
            fat_g_kg_day: {min: 2.5, max: 3.5}
        };
    } else if (patient.currentWeight < 2500) {
        macroReq = {
            glucose_mg_kg_min: {min: 4, max: 12},
            protein_g_kg_day: {min: 2.0, max: 3.0},
            fat_g_kg_day: {min: 2.0, max: 3.0}
        };
    } else {
        macroReq = {
            glucose_mg_kg_min: {min: 2.5, max: 5.0},
            protein_g_kg_day: {min: 1.5, max: 2.5},
            fat_g_kg_day: {min: 1.0, max: 3.0}
        };
    }
    
    // Check glucose infusion rate
    if (nutritionPlan.glucoseInfusionRate < macroReq.glucose_mg_kg_min.min) {
        recommendations.push(`Increase glucose infusion rate to at least ${macroReq.glucose_mg_kg_min.min} mg/kg/min (current: ${nutritionPlan.glucoseInfusionRate.toFixed(2)} mg/kg/min)`);
    } else if (nutritionPlan.glucoseInfusionRate > macroReq.glucose_mg_kg_min.max) {
        recommendations.push(`Consider reducing glucose infusion rate to maximum ${macroReq.glucose_mg_kg_min.max} mg/kg/min (current: ${nutritionPlan.glucoseInfusionRate.toFixed(2)} mg/kg/min)`);
    }
    
    // Check protein intake
    if (nutritionPlan.totalProtein < macroReq.protein_g_kg_day.min) {
        recommendations.push(`Increase protein intake to at least ${macroReq.protein_g_kg_day.min} g/kg/day (current: ${nutritionPlan.totalProtein.toFixed(2)} g/kg/day)`);
    } else if (nutritionPlan.totalProtein > macroReq.protein_g_kg_day.max) {
        recommendations.push(`Consider reducing protein intake to maximum ${macroReq.protein_g_kg_day.max} g/kg/day (current: ${nutritionPlan.totalProtein.toFixed(2)} g/kg/day)`);
    }
    
    // Check fat intake
    if (nutritionPlan.totalFat < macroReq.fat_g_kg_day.min) {
        recommendations.push(`Increase fat intake to at least ${macroReq.fat_g_kg_day.min} g/kg/day (current: ${nutritionPlan.totalFat.toFixed(2)} g/kg/day)`);
    } else if (nutritionPlan.totalFat > macroReq.fat_g_kg_day.max) {
        recommendations.push(`Consider reducing fat intake to maximum ${macroReq.fat_g_kg_day.max} g/kg/day (current: ${nutritionPlan.totalFat.toFixed(2)} g/kg/day)`);
    }
    
    // Special clinical considerations
    if (patient.clinicalCondition === 'Sepsis') {
        recommendations.push('In sepsis, consider reducing lipid intake and monitoring triglyceride levels');
    } else if (patient.clinicalCondition === 'Hyperglycemia') {
        recommendations.push('In hyperglycemia, consider reducing glucose infusion rate and monitoring blood glucose levels');
    }
    
    // Update recommendations list
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    
    if (recommendations.length === 0) {
        recommendationsList.innerHTML = '<li>All nutritional requirements are met.</li>';
    } else {
        recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            recommendationsList.appendChild(li);
        });
    }
}

// Update feeding schedule
function updateFeedingSchedule() {
    if (nutritionPlan.enteralFeedingFrequency <= 0 || nutritionPlan.enteralVolume <= 0) {
        document.getElementById('scheduleTableBody').innerHTML = '<tr><td colspan="3">No enteral feeding scheduled</td></tr>';
        return;
    }
    
    // Update schedule info
    document.getElementById('scheduleFeedingType').textContent = nutritionPlan.enteralFeedingType;
    document.getElementById('scheduleFrequency').textContent = nutritionPlan.enteralFeedingFrequency;
    document.getElementById('scheduleVolume').textContent = nutritionPlan.enteralVolume.toFixed(1);
    
    // Calculate volume per feed
    const volumePerFeed = nutritionPlan.enteralVolume / nutritionPlan.enteralFeedingFrequency;
    const absoluteVolumePerFeed = (volumePerFeed * patient.currentWeight) / 1000; // Convert to ml
    
    // Create schedule
    const scheduleTableBody = document.getElementById('scheduleTableBody');
    scheduleTableBody.innerHTML = '';
    
    const hoursBetweenFeeds = 24 / nutritionPlan.enteralFeedingFrequency;
    
    for (let i = 0; i < nutritionPlan.enteralFeedingFrequency; i++) {
        const hour = Math.floor(i * hoursBetweenFeeds);
        const minute = Math.round((i * hoursBetweenFeeds - hour) * 60);
        const timeStr = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${timeStr}</td>
            <td>${volumePerFeed.toFixed(2)} ml/kg</td>
            <td>${absoluteVolumePerFeed.toFixed(2)} ml</td>
        `;
        scheduleTableBody.appendChild(row);
    }
}

// Export nutrition plan
function exportNutritionPlan() {
    if (!nutritionPlan) {
        alert('Please calculate nutrition values first.');
        return;
    }
    
    // In a real application, this would call an API endpoint
    // For this demo, we'll create a JSON string and download it
    
    const exportData = {
        patient: {
            patientId: patient.patientId,
            gestationalAge: patient.gestationalAge,
            birthWeight: patient.birthWeight,
            currentWeight: patient.currentWeight,
            postnatalAge: patient.postnatalAge,
            phototherapy: patient.phototherapy,
            clinicalCondition: patient.clinicalCondition
        },
        nutritionPlan: {
            planId: nutritionPlan.planId,
            date: nutritionPlan.date,
            totalFluidTarget: nutritionPlan.totalFluidTarget,
            tpnType: nutritionPlan.tpnType,
            tpnVolume: nutritionPlan.tpnVolume,
            lipidType: nutritionPlan.lipidType,
            lipidVolume: nutritionPlan.lipidVolume,
            glucoseConcentration: nutritionPlan.glucoseConcentration,
            glucoseVolume: nutritionPlan.glucoseVolume,
            enteralFeedingType: nutritionPlan.enteralFeedingType,
            enteralVolume: nutritionPlan.enteralVolume,
            enteralFeedingFrequency: nutritionPlan.enteralFeedingFrequency,
            bmfConcentration: nutritionPlan.bmfConcentration
        },
        calculatedValues: {
            totalEnergy: nutritionPlan.totalEnergy,
            totalProtein: nutritionPlan.totalProtein,
            totalCarbohydrate: nutritionPlan.totalCarbohydrate,
            totalFat: nutritionPlan.totalFat,
            totalSodium: nutritionPlan.totalSodium,
            totalPotassium: nutritionPlan.totalPotassium,
            totalCalcium: nutritionPlan.totalCalcium,
            totalPhosphate: nutritionPlan.totalPhosphate,
            totalMagnesium: nutritionPlan.totalMagnesium,
            glucoseInfusionRate: nutritionPlan.glucoseInfusionRate
        }
    };
    
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `nutrition_plan_${patient.patientId}_${nutritionPlan.date}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}

// Print feeding schedule
function printSchedule() {
    if (!nutritionPlan || nutritionPlan.enteralFeedingFrequency <= 0) {
        alert('Please calculate a valid nutrition plan with enteral feeding first.');
        return;
    }
    
    const printWindow = window.open('', '_blank');
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Feeding Schedule - Patient ${patient.patientId}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { font-size: 18px; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .footer { margin-top: 30px; font-size: 12px; }
            </style>
        </head>
        <body>
            <h1>Feeding Schedule - ${new Date().toLocaleDateString()}</h1>
            <p><strong>Patient ID:</strong> ${patient.patientId}</p>
            <p><strong>Weight:</strong> ${patient.currentWeight} grams</p>
            <p><strong>Feeding Type:</strong> ${nutritionPlan.enteralFeedingType}</p>
            <p><strong>Total Volume:</strong> ${nutritionPlan.enteralVolume.toFixed(1)} ml/kg/day</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Volume per kg</th>
                        <th>Volume (ml)</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
    `);
    
    const volumePerFeed = nutritionPlan.enteralVolume / nutritionPlan.enteralFeedingFrequency;
    const absoluteVolumePerFeed = (volumePerFeed * patient.currentWeight) / 1000; // Convert to ml
    const hoursBetweenFeeds = 24 / nutritionPlan.enteralFeedingFrequency;
    
    for (let i = 0; i < nutritionPlan.enteralFeedingFrequency; i++) {
        const hour = Math.floor(i * hoursBetweenFeeds);
        const minute = Math.round((i * hoursBetweenFeeds - hour) * 60);
        const timeStr = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
        
        printWindow.document.write(`
            <tr>
                <td>${timeStr}</td>
                <td>${volumePerFeed.toFixed(2)} ml/kg</td>
                <td>${absoluteVolumePerFeed.toFixed(2)} ml</td>
                <td></td>
            </tr>
        `);
    }
    
    printWindow.document.write(`
                </tbody>
            </table>
            
            <div class="footer">
                <p>Generated by NICU Fluid Management App on ${new Date().toLocaleString()}</p>
            </div>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.focus();
    
    // Print after a short delay to ensure content is loaded
    setTimeout(() => {
        printWindow.print();
    }, 500);
}
