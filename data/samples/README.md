# BTC-SHIELD Synthetic Investigation Dataset v2.0

Exactly **10,000 synthetic transaction records** for BTC-SHIELD.

This is not an official NTRO dataset and does not represent real seized,
intercepted, or attributed Bitcoin activity.

The supplied SIH Problem Statement 26146 describes a synthetic dataset modeled
on Bitcoin P2P/transaction fields and lists Dataset Link as Nil.

## Files
- `btc_shield_synthetic_transactions_10000.csv`
- `btc_shield_synthetic_transactions_10000.json`
- `btc_shield_synthetic_transactions_10000.xml`
- `dataset_manifest_10000.json`
- `README.md`

## Scenarios
Normal baseline; common-input entity clustering; high-value anomalies;
rapid temporal behavior; peeling chains; mixing/CoinJoin-like structures;
IP/wallet correlation anomalies; multi-hop graph flows.

Generation seed: `26146`.

The `scenario` field is ground-truth evaluation metadata only and must not be
used as an ML input feature.
