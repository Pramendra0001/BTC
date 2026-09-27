# BTC-SHIELD — Offline GeoIP & ASN Database Configuration

This directory contains the local MMDB databases used by BTC-SHIELD for offline IP geolocation and ASN intelligence.

## Required Files

The offline deployment expects these DB-IP Lite MMDB files:

- `DB-IP-Country-Lite.mmdb` — IP country/location database
- `DB-IP-ASN-Lite.mmdb` — IP Autonomous System Number (ASN) and organization database

The backend is configured to load them from:

    /app/offline/geoip/DB-IP-Country-Lite.mmdb
    /app/offline/geoip/DB-IP-ASN-Lite.mmdb

## Offline Operation

The databases are loaded locally by the backend using the `maxminddb` Python library. No external GeoIP API or network service is required during offline operation.

When the MMDB files are available, the GeoIP service reports:

- `active_mode: MMDB`
- `is_operational: true`
- `is_fallback: false` for successfully resolved addresses

Example verification:

    8.8.8.8 -> US
    ASN -> AS15169
    Organization -> Google LLC
    Fallback -> false

## Air-Gapped Fallback

If the MMDB files are unavailable, BTC-SHIELD automatically uses its deterministic offline RFC 5737 / RFC 1918 fallback resolver.

The fallback mode does not require Internet access and reports the fallback status explicitly through GeoIP telemetry.

## Verification

Verify that both databases exist before starting the offline deployment:

    ls -lh offline/geoip/*.mmdb
