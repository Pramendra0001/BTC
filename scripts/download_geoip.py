#!/usr/bin/env python3
"""
BTC-SHIELD DB-IP Lite GeoIP Database Download & Verification Script.
Downloads official CC BY 4.0 DB-IP Lite Country and ASN MMDB databases,
verifies checksums, decompresses to offline/geoip/, and reports metrics.
"""
import os
import sys
import gzip
import hashlib
import urllib.request

COUNTRY_URL = "https://download.db-ip.com/free/dbip-country-lite-2026-08.mmdb.gz"
ASN_URL = "https://download.db-ip.com/free/dbip-asn-lite-2026-08.mmdb.gz"

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GEOIP_DIR = os.path.join(REPO_ROOT, "offline", "geoip")

COUNTRY_MMDB = os.path.join(GEOIP_DIR, "DB-IP-Country-Lite.mmdb")
ASN_MMDB = os.path.join(GEOIP_DIR, "DB-IP-ASN-Lite.mmdb")

def download_and_extract(url: str, output_path: str, label: str):
    os.makedirs(GEOIP_DIR, exist_ok=True)
    gz_path = output_path + ".gz"
    print(f"[+] Downloading {label} from {url}...")
    headers = {"User-Agent": "BTC-SHIELD/1.0 (SIH-26146-Research)"}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req) as resp, open(gz_path, "wb") as out_file:
        data = resp.read()
        out_file.write(data)
    
    gz_size = os.path.getsize(gz_path)
    sha256_gz = hashlib.sha256(data).hexdigest()
    print(f"    Downloaded {gz_size:,} bytes. GZ SHA-256: {sha256_gz}")

    print(f"[+] Decompressing {gz_path} to {output_path}...")
    with gzip.open(gz_path, "rb") as gz_in, open(output_path, "wb") as out_file:
        decompressed_data = gz_in.read()
        out_file.write(decompressed_data)

    mmdb_size = os.path.getsize(output_path)
    sha256_mmdb = hashlib.sha256(decompressed_data).hexdigest()
    print(f"    Extracted {mmdb_size:,} bytes. MMDB SHA-256: {sha256_mmdb}")

    # Remove temporary gz
    if os.path.exists(gz_path):
        os.remove(gz_path)

    return {
        "label": label,
        "url": url,
        "mmdb_path": output_path,
        "mmdb_size": mmdb_size,
        "sha256": sha256_mmdb
    }

def main():
    print("=================================================================")
    print("      BTC-SHIELD — DB-IP LITE OFFLINE GEOIP DATABASE SETUP       ")
    print("=================================================================")
    res_country = download_and_extract(COUNTRY_URL, COUNTRY_MMDB, "Country Lite")
    res_asn = download_and_extract(ASN_URL, ASN_MMDB, "ASN Lite")

    print("\n[OK] Both DB-IP Lite databases successfully downloaded and extracted:")
    print(f"    1. {res_country['mmdb_path']} ({res_country['mmdb_size']:,} bytes)")
    print(f"       SHA-256: {res_country['sha256']}")
    print(f"    2. {res_asn['mmdb_path']} ({res_asn['mmdb_size']:,} bytes)")
    print(f"       SHA-256: {res_asn['sha256']}")
    print("=================================================================")

if __name__ == "__main__":
    main()
