# Machine Learning Integration

## Anomaly Detection Approach
BTC-SHIELD relies on unsupervised machine learning to detect previously unseen illicit structures.

### Feature Definitions
- **Fan-Out Ratio:** `O / I` (Outputs / Inputs)
- **Velocity:** `Total Value / Time Window`
- **Fee Ratio:** `Fee / Total Value`

### Models
1. **Isolation Forest:**
   - **Algorithm:** Constructs decision trees partitioning the feature space. Anomalies have shorter average path lengths.
   - **Parameters:** `n_estimators=100`, `contamination=0.05`
2. **DBSCAN:**
   - **Algorithm:** Density-based spatial clustering. Used to detect Geo-Hopping anomalies based on IP distances.
   - **Parameters:** `eps=0.5`, `min_samples=5`

## Evaluation Metrics
Since labels (`scenario_label`) are only used for evaluation in synthetic data, we use:
- Precision / Recall on known anomalies.
- ROC-AUC to evaluate the anomaly score thresholds.

## Distinction between Scores
- **Anomaly Score:** Mathematical outlier score from the ML model (0.0 to 1.0).
- **Confidence:** System heuristic confidence that the classification is accurate.
- **Priority:** Actionable metric calculated by `Anomaly Score * Total Value in USD`.
