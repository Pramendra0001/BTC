# BTC-SHIELD — Local Machine Learning Model Artifacts

This directory persists local machine learning model artifacts generated during offline model training runs.

## Supported Model Types
- **Isolation Forest (`isolation_forest.joblib`)**: Unsupervised decision tree ensemble identifying statistical outliers across high-dimensional behavioral features. Scores are scaled to `[0, 100]`.
- **DBSCAN (`dbscan.joblib`)**: Density-based spatial clustering identifying dense cohorts of peer wallets and flagging dispersed behavioral outliers.
- **Robust Feature Scaler (`scaler.joblib`)**: Standardizes transaction velocities, fan-in/fan-out ratios, and entropy metrics.

## Zero External Dependency
All models are trained, serialized, and evaluated strictly on-device using local `scikit-learn` and `joblib`. No cloud endpoints, remote inference services, or external APIs are used.
