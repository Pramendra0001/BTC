"""
BTC-SHIELD — Real MMDB & Offline GeoIP Resolution Test Suite
Verifies DB-IP Lite integration, normalized schema extraction, RFC 5737 fallback, and attribution.
"""
import pytest
from app.services.geoip_service import GeoIPService

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

def test_geoip_public_ip_google():
    service = GeoIPService()
    res = service.lookup("8.8.8.8")
    assert res["valid"] is True
    assert res["country"] == "US"
    assert res["country_name"] == "United States"
    assert res["asn"] == "AS15169"
    assert "Google" in res["asn_org"]
    assert res["mode"] == "LOCAL_MMDB"
    assert res["source"] == "DB-IP-Lite"
    assert "DB-IP.com" in res["attribution"]
    assert res["is_fallback"] is False

def test_geoip_public_ip_cloudflare():
    service = GeoIPService()
    res = service.lookup("1.1.1.1")
    assert res["valid"] is True
    assert res["country"] == "AU"
    assert res["country_name"] == "Australia"
    assert res["asn"] == "AS13335"
    assert "Cloudflare" in res["asn_org"]
    assert res["mode"] == "LOCAL_MMDB"
    assert res["source"] == "DB-IP-Lite"
    assert res["is_fallback"] is False

def test_geoip_rfc5737_documentation_fallback():
    service = GeoIPService()
    res = service.lookup("192.0.2.1")
    assert res["valid"] is True
    assert res["country"] == "US"
    assert res["asn"] == "AS64496"
    assert res["city"] == "TEST-NET-1"
    assert res["is_fallback"] is True
    assert res["mode"] == "OFFLINE_FALLBACK"

def test_geoip_rfc1918_private_fallback():
    service = GeoIPService()
    res = service.lookup("10.0.0.1")
    assert res["valid"] is True
    assert res["country"] == "LOCAL"
    assert res["asn"] == "AS0"
    assert res["is_fallback"] is True
    assert res["mode"] == "OFFLINE_FALLBACK"

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
