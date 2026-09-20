# Demonstration Script

## Step-by-Step SIH Demo (16 Steps)

1. **Introduction:** Introduce BTC-SHIELD and the objective of detecting illicit crypto activity.
2. **Data Generation:** Show the `generate_dataset.py` script running, highlighting the deterministic behavior.
3. **Ingestion:** Run the ingestion pipeline to load the data.
4. **Dashboard View:** Show the overall metrics (Total TXs, Total Alerts).
5. **Alert Queue:** Navigate to the Alert queue, sorted by Priority.
6. **Peeling Chain Anomaly:** Select a `FAN_OUT_PEELING` alert.
7. **Graph Visualization (Peeling):** Show the network graph view representing the fan-out structure.
8. **Consolidation Anomaly:** Select a `FAN_IN_CONSOLIDATION` alert.
9. **Graph Visualization (Consolidation):** Show the corresponding network map.
10. **Geo-Hopping Anomaly:** Highlight an IP-based anomaly detected by DBSCAN.
11. **ML Explainability:** Show the modal explaining *why* the Isolation Forest flagged the transaction.
12. **Case Management:** Create a new "Case" and attach 3 alerts to it.
13. **RBAC Demo:** Log out and log in as a "Viewer" to show disabled buttons.
14. **Audit Log:** Show the admin view of the audit logs recording the case creation.
15. **System Architecture:** Briefly flash the architecture slide.
16. **Q&A Transition:** Conclude the functional demo.

## Common Questions
- *How does the synthetic data work?* It uses defined statistical distributions for various money laundering topologies.
- *Is this purely rule-based?* No, it uses both rules (heuristics) and ML (Isolation Forest).
