# BTC-SHIELD Machine Learning & Feature Engineering Pipeline

**Module:** Advanced Unsupervised Anomaly Detection & Clustering Core  
**Feature Schema Version:** 2.0  
**Libraries:** `scikit-learn >= 1.5.0`, `numpy >= 1.26.0`, `joblib >= 1.4.0`  

---

## 1. Machine Learning Philosophy

In Bitcoin forensic intelligence, ground-truth labels indicating definitively criminal activity rarely exist. Criminal actors constantly vary their operational patterns (peeling chains, mixer pools, temporal delays, multi-hop VPN relays).

Therefore, BTC-SHIELD employs **strictly unsupervised machine learning**:
1. It does **not** rely on brittle synthetic labels to train binary classifiers.
2. It detects structural, mathematical divergence from empirical peer behavior using **Isolation Forests**.
3. It discovers behavioral clusters and classifies noise points using **DBSCAN**.
4. It extracts discrete, explainable evidence signals directly from feature anomalies.

---

## 2. The 23 Behavioral Feature Dimensions

Each resolved entity (wallet address or network IP) is transformed into a high-dimensional feature vector across five operational domains:

### Domain 1: Transaction Volume & Flow Dynamics
| Feature Name | Type | Description | Forensic Relevance |
|---|---|---|---|
| `tx_count` | Integer | Total count of confirmed transactions | Measures overall activity level |
| `total_sent` | Float (sat) | Cumulative outbound value | Identifies high-volume disbursement |
| `total_received` | Float (sat) | Cumulative inbound value | Identifies collection hubs |
| `net_flow` | Float (sat) | Received minus Sent balance | Detects accumulation vs. wash pass-through |
| `amount_mean` | Float (sat) | Arithmetic mean transaction value | Baseline transacting volume |
| `amount_median` | Float (sat) | Median transaction value | Robust central tendency |
| `amount_std` | Float (sat) | Standard deviation of values | Measures variance in transferred values |
| `amount_variance` | Float | Variance of values | Detects high-volatility laundering |
| `amount_min` | Float (sat) | Smallest transaction value observed | Identifies micro-dusting probing |
| `amount_max` | Float (sat) | Largest transaction value observed | Identifies major capital movements |

### Domain 2: Structural & Fan Topology
| Feature Name | Type | Description | Forensic Relevance |
|---|---|---|---|
| `fan_in` | Integer | Number of transaction inputs | High fan-in indicates UTXO consolidation |
| `fan_out` | Integer | Number of transaction outputs | High fan-out indicates peeling chains or tumbler splits |
| `fan_ratio` | Float | `fan_out / max(fan_in, 1)` | Identifies asymmetric dispersing operations |

### Domain 3: Mining Fee Statistics
| Feature Name | Type | Description | Forensic Relevance |
|---|---|---|---|
| `fee_mean` | Float (sat) | Mean transaction fee paid | Identifies willingness to pay premium for fast blocks |
| `fee_std` | Float (sat) | Standard deviation of fee payments | Detects programmatic automated fee scripts |
| `fee_max` | Float (sat) | Maximum single fee paid | Identifies urgent or erratic transactions |
| `fee_to_value_ratio`| Float | Total fees paid / Total value | Detects irrational fees (e.g. dusting or micro-transactions) |

### Domain 4: Temporal & Velocity Dynamics
| Feature Name | Type | Description | Forensic Relevance |
|---|---|---|---|
| `tx_velocity` | Integer | Number of transactions within observation span | Measures transaction frequency |
| `inter_arrival_mean`| Float (sec) | Mean time delta between consecutive transactions | Temporal baseline |
| `inter_arrival_std` | Float (sec) | Standard deviation of inter-arrival deltas | Irregularity metric |
| `burstiness` | Float | Ratio $\sigma_{\Delta t} / \mu_{\Delta t}$ | High values indicate sudden bursts of automated activity |
| `hour_entropy` | Float (bits)| Shannon entropy over 24-hour distribution | Uniform transacting (high entropy) indicates automated bots |

### Domain 5: Counterparty & Network Telemetry
| Feature Name | Type | Description | Forensic Relevance |
|---|---|---|---|
| `unique_counterparties`| Integer | Count of distinct counterparty wallet addresses | Breadth of interaction network |
| `counterparty_entropy` | Float (bits)| Shannon entropy of interactions per counterparty | Concentrated interactions vs. broad mixing |
| `unique_ip_count` | Integer | Count of distinct relay/source IPs observed | Multi-IP rotation detection |
| `unique_asn_count`| Integer | Count of distinct ASNs observed | Cross-cloud or VPN routing detection |
| `unique_country_count`| Integer | Count of distinct sovereign jurisdictions | Jurisdictional hopping detection |
| `asn_entropy` | Float (bits)| Shannon entropy of ASN observations | Routing dispersion metric |

---

## 3. Machine Learning Algorithms

### 3.1 Isolation Forest (Ensemble Anomaly Detection)
- **Algorithm Principle:** Anomalous data points require fewer random axis-aligned splits to isolate in feature space compared to normal points clustered in high-density regions.
- **Path Length Formulation:**
  The average path length $h(x)$ of an entity vector $x$ across an ensemble of $T$ isolation trees is compared to the expected path length of an equivalent random binary tree $c(n)$:
  $$c(n) = 2 \ln(n - 1) + 0.5772156649 - \frac{2(n - 1)}{n}$$
  $$s(x, n) = 2^{-\frac{\mathbb{E}(h(x))}{c(n)}}$$
- **Normalized Anomaly Score:**
  Raw decision function outputs $s(x, n)$ are linearly calibrated to a $[0.0, 100.0]$ scale:
  $$\text{Score}(x) = \min(100.0, \max(0.0, (s_{\text{raw}} - s_{\min}) \cdot \frac{100}{s_{\max} - s_{\min}}))$$
  - `0 - 40`: Normal baseline activity.
  - `40 - 60`: Mild behavioral variance.
  - `60 - 80`: High anomaly requiring review.
  - `80 - 100`: Extreme outlier with severe multi-dimensional deviation.

### 3.2 Cohort Behavioral Clustering (Dual-Scale Architecture)

To support both small unit test fixtures and large production cohorts ($45,000+$ entities) within strict container memory bounds ($512\text{ MB}$ RSS), BTC-SHIELD implements a dual-scale clustering architecture:

#### A. Small Cohort Mode ($N \le 1,000$ Entities)
- **Algorithm:** Standard Scikit-Learn `DBSCAN(eps=eps, min_samples=min_samples_val, n_jobs=1)`
- **Adaptive Epsilon Optimization:** Rather than a static hardcoded epsilon, BTC-SHIELD computes the $k$-nearest neighbor distance distribution across all standard-scaled feature vectors ($k=\min(5, N)$) and adaptively selects the 80th percentile distance:
  $$\epsilon = \max\Big(0.5, \; \text{Percentile}_{80}(\text{k-NN Distances})\Big)$$
- **Min Samples:** Dynamically set to $\min(10, \max(3, \lfloor N / 50 \rfloor))$.
- **Noise Classification:** Un-clusterable points in low-density regions are assigned Cluster ID `-1` (behavioral noise points).

#### B. Large Cohort Mode ($N > 1,000$ Entities — Production Benchmark)
- **Problem Statement:** Standard DBSCAN on $45,000$ 23-dimensional vectors triggers an $O(N^2)$ memory allocation explosion ($>15\text{ GB}$ RSS), crashing containers with exit code 137.
- **Engineered Operational Substitute:** `MiniBatchKMeans(n_clusters=12, batch_size=2048, random_state=42, n_init="auto")`.
- **Distance-to-Centroid Outlier Thresholding:**
  1. Computes Euclidean distance $d(x_i)$ from each standard-scaled entity vector to its assigned cluster centroid $\mu_{c(i)}$:
     $$d(x_i) = \| x_i - \mu_{c(i)} \|_2$$
  2. Computes the 97th percentile distance threshold:
     $$\tau = \text{Percentile}_{97.0}\big(\{ d(x_i) \}_{i=1}^N \big)$$
  3. Designates the top 3% furthest entities as behavioral noise:
     $$\text{Cluster}(x_i) = \begin{cases} -1 & \text{if } d(x_i) > \tau \\ c(i) & \text{otherwise} \end{cases}$$
- **Algorithmic Reality:** MiniBatchKMeans is **not** claimed to be mathematically equivalent to DBSCAN. It is an engineered operational substitute that achieves $O(N \cdot K)$ memory complexity ($\approx 6.4\text{ MB}$ allocation) while strictly preserving the downstream contract: assigning `cluster_id = -1` to anomalous cohort outliers.

---

## 4. Model Versioning & Artifact Persistence

All trained models and feature scalers are serialized with metadata:
- **Directory:** `backend/ml_models/`
- **File Format:** `joblib` compressed serialization:
  - `if_model_{version}.joblib`
  - `if_scaler_{version}.joblib`
  - `dbscan_model_{version}.joblib`
  - `dbscan_scaler_{version}.joblib`
- **Database Record:** Logged in the `model_runs` table with hyperparameters, feature column lists, contamination ratios, and training timestamps.
