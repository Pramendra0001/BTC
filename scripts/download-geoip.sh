#!/bin/bash
# ==============================================================================
# BTC-SHIELD — DB-IP Lite Offline GeoIP Database Download Script (Bash/Linux)
# Downloads official CC BY 4.0 DB-IP Lite Country and ASN MMDB databases
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GEOIP_DIR="$REPO_ROOT/offline/geoip"

mkdir -p "$GEOIP_DIR"

COUNTRY_URL="https://download.db-ip.com/free/dbip-country-lite-2026-08.mmdb.gz"
ASN_URL="https://download.db-ip.com/free/dbip-asn-lite-2026-08.mmdb.gz"

echo "================================================================="
echo "      BTC-SHIELD — DB-IP LITE OFFLINE GEOIP DATABASE SETUP       "
echo "================================================================="

echo "[+] Downloading DB-IP Country Lite MMDB..."
curl -sSL "$COUNTRY_URL" -o "$GEOIP_DIR/DB-IP-Country-Lite.mmdb.gz"
gzip -df "$GEOIP_DIR/DB-IP-Country-Lite.mmdb.gz"
echo "    Extracted: $GEOIP_DIR/DB-IP-Country-Lite.mmdb ($(wc -c < "$GEOIP_DIR/DB-IP-Country-Lite.mmdb") bytes)"

echo "[+] Downloading DB-IP ASN Lite MMDB..."
curl -sSL "$ASN_URL" -o "$GEOIP_DIR/DB-IP-ASN-Lite.mmdb.gz"
gzip -df "$GEOIP_DIR/DB-IP-ASN-Lite.mmdb.gz"
echo "    Extracted: $GEOIP_DIR/DB-IP-ASN-Lite.mmdb ($(wc -c < "$GEOIP_DIR/DB-IP-ASN-Lite.mmdb") bytes)"

echo ""
echo "[OK] Both DB-IP Lite databases downloaded and extracted to $GEOIP_DIR"
echo "Attribution: IP geolocation data provided by DB-IP.com (CC BY 4.0)"
echo "================================================================="
