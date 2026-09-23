# BTC-SHIELD — Machine Learning Architecture & Algorithmic Specification

## 1. Overview
BTC-SHIELD relies on unsupervised machine learning to detect previously unseen illicit structures and behavioral anomalies without requiring pre-labeled ground truth.

---

## 2. 23-Dimensional Behavioral Feature Space
The feature extraction engine (`backend/app/services/feature_service.py`) calculates 23 continuous features across four domains:

1. **Volume Dynamics (6 Features):**
   - `total_input_sats`: Aggregate satoshi inputs.
   - `total_output_sats`: Aggregate satoshi outputs.
   - `fee_sats`: Transaction mining fee.
   - `fee_rate_sat_vb`: Fee density in satoshis per virtual byte.
   - `output_value_mean`: Mean output value.
   - `output_value_std`: Standard deviation of output values.

2. **Structural Topology (7 Features):**
   - `num_inputs`: Input UTXO count.
   - `num_outputs`: Output UTXO count.
   - `fan_out_ratio`: Ratio of outputs to inputs ($O / I$).
   - `script_type_entropy`: Shannon entropy across script types (P2PKH, P2SH, P2WPKH, P2TR).
   - `is_rbf_enabled`: Replace-By-Fee signaling flag.
   - `has_op_return`: Presence of OP_RETURN arbitrary data payload.
   - `locktime_type`: Classification of locktime (None, Block Height, UNIX timestamp).

3. **Temporal Dynamics (5 Features):**
   - `block_interarrival_time`: Time delta between successive block confirmations.
   - `burstiness_cv`: Coefficient of variation ($\sigma / \mu$) of transaction inter-arrival times.
   - `propagation_delay_sec`: Time delta between network relay observation and ledger inclusion.
   - `hour_of_day_utc`: Diurnal cyclical feature ($0 - 23$).
   - `day_of_week`: Day of week index ($0 - 6$).

4. **Network Telemetry Correlation (5 Features):**
   - `relay_node_count`: Number of distinct P2P relay nodes broadcasting the transaction.
   - `unique_asn_count`: Diversity of Autonomous System Numbers observed in relay path.
   - `cross_border_hop_count`: Count of geographic jurisdiction boundary crossings.
   - `tor_or_proxy_risk_score`: Heuristic proxy/anonymizer risk rating ($0.0 - 1.0$).
   - `coincident_node_dispersion`: Spatial dispersion metric of broadcasting peer nodes.

---

## 3. Algorithmic Models & Scaling Truth

### 3.1 Isolation Forest Anomaly Radar
- **Implementation:** `sklearn.ensemble.IsolationForest`
- **Parameters:** `n_estimators=50`, `max_samples=min(256, n_samples)`, `contamination="auto"`, `random_state=42`, `n_jobs=1`
- **Normalization:** Raw decision function scores $s \in [-0.5, 0.5]$ are linearly scaled to $[0.0, 100.0]$:
  $$\text{Score} = \min\Big(100.0, \; \max\big(0.0, \; (s_{\text{raw}} - s_{\min}) \cdot \frac{100.0}{s_{\max} - s_{\min}}\big)\Big)$$
- **Interpretation:**
  - `0 - 50`: Baseline normal transaction activity.
  - `50 - 75`: Moderate behavioral variance.
  - `75 - 100`: High multi-dimensional anomaly requiring investigative review.

### 3.2 Cohort Behavioral Clustering (Dual-Scale Architecture)
To handle both focused unit tests and 45,000+ entity production datasets within strict 512 MB RAM limits, BTC-SHIELD uses a dual-scale clustering architecture:

#### A. Small Cohort Mode ($N \le 1,000$ Entities)
- **Algorithm:** Standard `DBSCAN(eps=eps, min_samples=min_samples_val, n_jobs=1)`
- **Adaptive Epsilon:** Derived from the 80th percentile of $k$-NN distances ($k=\min(5, N)$).
- **Behavioral Noise:** Isolated outliers are assigned `cluster_id = -1`.

#### B. Large Cohort Mode ($N > 1,000$ Entities — Production 45k+ Datasets)
- **Memory Scaling Rationale:** Standard DBSCAN on 45,000 23-dimensional vectors triggers an $O(N^2)$ distance graph explosion ($>15\text{ GB}$ RAM), fatal on cloud containers.
- **Engineered Operational Substitute:** `MiniBatchKMeans(n_clusters=12, batch_size=2048, random_state=42, n_init="auto")`.
- **Centroid-Distance Outlier Analysis:**
  1. Computes Euclidean distance from each vector to its assigned cluster centroid.
  2. Sets threshold at the 97th percentile ($\tau = \text{Percentile}_{97.0}(d)$).
  3. Re-assigns the top 3% furthest entities to `cluster_id = -1` (un-clusterable behavioral noise).
- **Algorithmic Reality:** MiniBatchKMeans is **not** mathematically identical to DBSCAN; it is an engineered operational substitute that achieves $O(N \cdot K)$ memory complexity ($\approx 6.4\text{ MB}$ allocation) while strictly satisfying the downstream contract: isolating behavioral noise as `cluster_id = -1`.

---

## 4. Evidentiary Score Distinctions
- **Anomaly Score ($0.0 - 100.0$):** Mathematical outlier score from the Isolation Forest model.
- **Data Sufficiency Confidence ($0 - 100\%$):** System metric measuring observable telemetry depth ($N_{\text{observations}}$, $N_{\text{transactions}}$, $T_{\text{span}}$).
- **Compound Priority Score ($0 - 100$):** Weighted risk index combining ML anomaly scores ($45\%$), heuristic triggers ($35\%$), and network indicators ($20\%$).
