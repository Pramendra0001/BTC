# BTC-SHIELD — Offline GeoIP & ASN Database Configuration

This directory contains the local MaxMind database files required for offline spatial and autonomous system intelligence resolution.

## Expected Files
- `GeoLite2-City.mmdb` — Country, Region, and City location database
- `GeoLite2-ASN.mmdb` — Autonomous System Number (ASN) and Organization database

## Instructions
1. Download or copy your licensed or free `GeoLite2-City.mmdb` and `GeoLite2-ASN.mmdb` files into this directory.
2. Ensure the files are named exactly:
   - `offline/geoip/GeoLite2-City.mmdb`
   - `offline/geoip/GeoLite2-ASN.mmdb`
3. Restart or reload the BTC-SHIELD backend container.

## Air-Gapped Fallback Guarantee
If MMDB database files are omitted or absent, BTC-SHIELD automatically activates its **deterministic offline RFC 5737 / RFC 1918 fallback resolver**.
- Real-time resolution continues without exceptions.
- Telemetry indicators explicitly report `is_fallback: true` and `status: FALLBACK` to maintain complete investigative transparency.
- Zero outbound DNS lookups or external network requests are ever attempted.
