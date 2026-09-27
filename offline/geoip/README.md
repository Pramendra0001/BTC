# BTC-SHIELD — Local & Offline GeoIP / ASN Database Configuration

This directory contains local open-source binary MMDB database files enabling spatial IP geolocation and Autonomous System (ASN) correlation in fully air-gapped Linux environments.

## Active Integrated Database: DB-IP Lite (Open-Source)
BTC-SHIELD integrates the open-source **DB-IP Lite** IP-to-Country and IP-to-ASN databases under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

### Files Present:
1. **`DB-IP-Country-Lite.mmdb`**
   - **Type**: Binary MaxMind-format MMDB (Country / Region resolution)
   - **Release**: August 2026
   - **Size**: 8,284,207 bytes (~8.28 MB)
   - **SHA-256**: `5b370d4cf40259be3113118a1362ca6e704bdcab1842a102cdb6233b501e8558`
   - **Fields Extracted**: ISO 3166-1 alpha-2 country code (`country`), English country name (`country_name`), continent code.

2. **`DB-IP-ASN-Lite.mmdb`**
   - **Type**: Binary MaxMind-format MMDB (Autonomous System Number & Organization)
   - **Release**: August 2026
   - **Size**: 9,626,826 bytes (~9.63 MB)
   - **SHA-256**: `27bd730c5a754d656bdcf76b80cb92631cf7d98e2e7a3863c617a9d288f64cf5`
   - **Fields Extracted**: AS Number (`asn`, e.g., `AS15169`), AS Organization name (`asn_org`, e.g., `Google LLC`, `Cloudflare, Inc.`).

### Mandatory Attribution Notice:
> **IP geolocation data provided by DB-IP.com**  
> Distributed under Creative Commons Attribution 4.0 International (CC BY 4.0).  
> https://db-ip.com

---

## MaxMind GeoLite2 Backward Compatibility
BTC-SHIELD also supports optional MaxMind GeoLite2 databases:
- `GeoLite2-City.mmdb` or `GeoLite2-Country.mmdb`
- `GeoLite2-ASN.mmdb`

When placed in this directory or in `data/geoip/`, the platform auto-detects them and parses both schemas seamlessly.

---

## Air-Gapped Fallback Guarantee
If MMDB database files are omitted or when resolving documentation testnets (RFC 5737: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) or private subnets (RFC 1918: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`):
- BTC-SHIELD automatically activates its **deterministic offline fallback resolver**.
- No runtime exceptions or timeouts are generated.
- Telemetry explicitly flags `is_fallback: true` and `mode: OFFLINE_FALLBACK`.
- Zero external DNS or HTTP requests are ever attempted, preserving the air-gap boundary.

---

## Download & Refresh Utilities
To download or refresh the local DB-IP Lite databases on an internet-connected build machine before deploying to an air-gapped server:
```bash
# Python (cross-platform):
python scripts/download_geoip.py

# Bash (Linux/macOS):
bash scripts/download-geoip.sh
```
