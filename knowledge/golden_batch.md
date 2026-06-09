# Golden Batch Reference — IndPenSim V3

## Batch Overview
- dataset: IndPenSim V3 penicillin fermentation
- total_batches: 10
- best_batch: 8
- outlier_batch: 9

## Process Variable Limits
# Format: variable: [min, max, unit]
pH: [6.40, 6.70, pH]
Temperature: [297.5, 299.5, K]
Dissolved_Oxygen: [7.0, 15.0, mg/L]
Penicillin_Concentration: [0.0, 25.0, g/L]
Sugar_Feed_Rate: [8.0, 150.0, L/h]
OUR: [0.0, 2.0, g/min]
CER: [0.0, 1.8, g/h]

## Deviation Thresholds
# Format: variable: [lower_alert, upper_alert, unit]
pH: [6.35, 6.75, pH]
Temperature: [297.0, 300.0, K]
Dissolved_Oxygen: [6.0, null, mg/L]
Penicillin_end_of_batch_min: [18.0, null, g/L]

## Fermentation Phases
# Format: phase: [start_hour, end_hour, description]
lag: [0, 20, low growth minimal penicillin]
exponential: [20, 100, rapid biomass growth]
production: [100, 200, peak penicillin synthesis]
decline: [200, null, nutrient depletion]