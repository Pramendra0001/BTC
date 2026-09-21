# BTC-SHIELD 100,000 Ground-Ready Synthetic Dataset

## Recommended integration
1. Load `btc_shield_transactions_100000.csv` into the existing transaction ingestion path.
2. Load `btc_shield_edges_100000.csv` for transaction-to-transaction graph traversal.
3. Load `btc_shield_wallets.csv` for wallet/entity pages and aggregation.
4. Load `btc_shield_enrichment_100000.csv` for dashboard analytics and investigation views.
5. Join enrichment/edges on `txid` and wallet data on `address`.

## Core transaction schema
timestamp, src_ip, dst_ip, src_port, dst_port, txid, input_addresses, output_addresses, input_amounts, output_amounts, fee, script_type, geo_country, asn, scenario_label

## Scenario distribution
{
  "NORMAL_BASELINE": 78263,
  "FAN_OUT_PEELING": 3555,
  "AMOUNT_ANOMALY": 2520,
  "FAN_IN_CONSOLIDATION": 3619,
  "GEO_HOPPING": 2052,
  "MULTI_SIGNAL_ANOMALY": 2552,
  "MIXING_COINJOIN_LIKE": 1002,
  "BURST_ACTIVITY": 5469,
  "IP_WALLET_CORRELATION": 968
}

## Realism design
- 100,000 transactions across 9 months.
- Heavy-tailed transaction amounts.
- Input/output totals satisfy: inputs = outputs + fee.
- Reused wallet addresses create temporal money-flow continuity.
- Fan-in, fan-out/peeling, bursts, amount anomalies, geographic discontinuities and mixing-like patterns are embedded as graph structures.
- Separate enrichment and edge tables prevent the core ingestion schema from being polluted with dashboard-only fields.
- Documentation-only IP ranges avoid accidental real-world attribution.

## Important
All data is synthetic. Do not present it as real NTRO/intercepted Bitcoin activity or real criminal evidence.
