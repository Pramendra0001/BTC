# BTC-SHIELD — SIH-Compliant Test Datasets

This directory contains pre-generated SIH test datasets containing realistic Bitcoin blockchain transactions correlated with multi-attribute network layer telemetry.

## Available Sample Datasets
- `sample_transactions.csv`: Comma-separated values format containing correlated blockchain and P2P network telemetry.
- `sample_transactions.json`: JSON records format containing rich nested transaction objects.
- `sample_transactions.xml`: XML schema format matching SIH problem statement ingestion specifications.

## Embedded Investigative Scenarios
Each dataset contains baseline legitimate peer-to-peer traffic mixed with 7 distinct investigative scenarios:
1. **NORMAL_BASELINE (60%)**: Standard low-fan-out payments with typical velocities.
2. **BURST_ACTIVITY (8%)**: High-frequency micro-burst transactions from concentrated IPs.
3. **FAN_OUT_PEELING (6%)**: Single input peeling off small amounts across many outputs (peeling chain / tumbling).
4. **FAN_IN_CONSOLIDATION (6%)**: Aggregation of fragmented UTXOs into a single destination address.
5. **AMOUNT_ANOMALY (5%)**: Statistical outlier amounts or irrational fee-to-amount ratios.
6. **GEO_HOPPING (5%)**: Single wallet identity observed from multiple ASNs and disparate geographic countries within narrow time windows.
7. **MULTI_SIGNAL_ANOMALY (10%)**: Compound alerts triggering cross-layer network and on-chain indicators.
