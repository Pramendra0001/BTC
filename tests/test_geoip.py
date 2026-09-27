"""
BTC-SHIELD — Real MMDB & Offline GeoIP Resolution Integration Test Suite
SIH 26146: "AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic"
Validates DB-IP Lite integration, real MMDB binary reading, normalized schema extraction,
RFC 5737 / RFC 1918 deterministic offline fallback, zero-egress enforcement, and CC BY 4.0 attribution.
"""
import os
import socket
import pytest
import maxminddb
from app.services.geoip_service import GeoIPService

COUNTRY_MMDB_PATH = "offline/geoip/DB-IP-Country-Lite.mmdb"
ASN_MMDB_PATH = "offline/geoip/DB-IP-ASN-Lite.mmdb"

def test_real_geoip_mmdb_acceptance_criteria_10_points(monkeypatch):
    """
    Real GeoIP Acceptance Test covering all 10 authoritative SIH criteria:
    1. Verify actual MMDB files exist on disk.
    2. Verify they are non-empty (> 1 MB binary size).
    3. Open them directly with maxminddb.
    4. Perform a real public-IP lookup.
    5. Verify country data (ISO code + country name).
    6. Verify ASN data (AS number + AS organization).
    7. Verify source == 'DB-IP-Lite'.
    8. Verify mode == 'LOCAL_MMDB'.
    9. Verify private/test addresses use deterministic fallback.
    10. Verify no external HTTP/network API is called (socket guard).
    """
    # 1. Verify the actual MMDB files exist
    assert os.path.exists(COUNTRY_MMDB_PATH), f"Missing country MMDB at {COUNTRY_MMDB_PATH}"
    assert os.path.exists(ASN_MMDB_PATH), f"Missing ASN MMDB at {ASN_MMDB_PATH}"

    # 2. Verify they are non-empty
    country_size = os.path.getsize(COUNTRY_MMDB_PATH)
    asn_size = os.path.getsize(ASN_MMDB_PATH)
    assert country_size > 1_000_000, f"Country MMDB unexpectedly small ({country_size} bytes)"
    assert asn_size > 1_000_000, f"ASN MMDB unexpectedly small ({asn_size} bytes)"

    # 3. Open them directly with maxminddb
    with maxminddb.open_database(COUNTRY_MMDB_PATH) as c_reader:
        raw_c = c_reader.get("8.8.8.8")
        assert raw_c is not None
        assert "country" in raw_c

    with maxminddb.open_database(ASN_MMDB_PATH) as a_reader:
        raw_a = a_reader.get("8.8.8.8")
        assert raw_a is not None
        assert "autonomous_system_number" in raw_a

    # 10. Verify no external HTTP API is called (Socket guard interceptor)
    external_calls = []
    real_connect = socket.socket.connect

    def guarded_connect(self, address):
        external_calls.append(address)
        raise RuntimeError(f"Prohibited external network call during GeoIP lookup: {address}")

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)

    # Initialize GeoIPService and execute real lookups
    service = GeoIPService()

    # 4. Perform a real public-IP lookup (8.8.8.8)
    res_google = service.lookup("8.8.8.8")
    assert res_google["valid"] is True

    # 5. Verify country data
    assert res_google["country"] == "US"
    assert res_google["country_name"] == "United States"

    # 6. Verify ASN data
    assert res_google["asn"] == "AS15169"
    assert "Google" in res_google["asn_org"]

    # 7. Verify source == 'DB-IP-Lite'
    assert res_google["source"] == "DB-IP-Lite"
    assert "DB-IP.com" in res_google["attribution"]

    # 8. Verify mode == 'LOCAL_MMDB'
    assert res_google["mode"] == "LOCAL_MMDB"
    assert res_google["is_fallback"] is False

    # Second public IP check (1.1.1.1)
    res_cf = service.lookup("1.1.1.1")
    assert res_cf["country"] == "AU"
    assert res_cf["asn"] == "AS13335"
    assert "Cloudflare" in res_cf["asn_org"]
    assert res_cf["mode"] == "LOCAL_MMDB"
    assert res_cf["source"] == "DB-IP-Lite"

    # 9. Verify private/test addresses still use fallback
    res_test = service.lookup("192.0.2.1")
    assert res_test["valid"] is True
    assert res_test["is_fallback"] is True
    assert res_test["mode"] == "OFFLINE_FALLBACK"
    assert res_test["country"] == "US"
    assert res_test["city"] == "TEST-NET-1"

    res_priv = service.lookup("10.0.0.1")
    assert res_priv["valid"] is True
    assert res_priv["is_fallback"] is True
    assert res_priv["mode"] == "OFFLINE_FALLBACK"
    assert res_priv["country"] == "LOCAL"

    # 10. Assert 0 external network calls were attempted
    assert len(external_calls) == 0, f"External network calls detected: {external_calls}"

def test_geoip_service_initialization_and_status():
    service = GeoIPService()
    status = service.validate_status()
    assert status["is_operational"] is True
    assert status["active_mode"] in ("LOCAL_MMDB", "MMDB")
    assert status["geoip_mode"] == "LOCAL_MMDB"
    assert status["geoip_source"] == "DB-IP-Lite"
    assert "DB-IP.com" in status["attribution"]
    assert status["city_db_resolved_path"] is not None
    assert status["asn_db_resolved_path"] is not None

def test_geoip_invalid_ip_handling():
    service = GeoIPService()
    res_none = service.lookup(None)
    assert res_none["valid"] is False
    assert res_none["status"] == "INVALID_IP"

    res_bad = service.lookup("999.999.999.999")
    assert res_bad["valid"] is False
    assert res_bad["status"] == "INVALID_SYNTAX"

    res_empty = service.lookup("   ")
    assert res_empty["valid"] is False
