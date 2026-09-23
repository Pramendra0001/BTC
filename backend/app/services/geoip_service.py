"""
BTC-SHIELD GeoIP and Network Resolution Service.
Provides offline and local IP-to-Country and IP-to-ASN resolution with strict dual-mode architecture:

1. REAL MMDB RESOLUTION:
   When local MaxMind database files (GeoLite2-City.mmdb, GeoLite2-ASN.mmdb) are present
   and the `maxminddb` reader library is installed, real binary database lookups are executed.

2. DETERMINISTIC OFFLINE FALLBACK:
   When database files or the library are unavailable (e.g. air-gapped environments without
   downloaded proprietary datasets), the service resolves RFC 5737 documentation testnets
   and RFC 1918 private subnets deterministically with zero external egress.
"""
import os
import ipaddress
import logging
from typing import Dict, Any, Optional, Tuple
from app.core.config import settings

logger = logging.getLogger("btcshield.geoip")

# Static offline fallback ranges for standard documentation & private networks
STATIC_OFFLINE_RANGES = [
    # TEST-NET-1, TEST-NET-2, TEST-NET-3 (RFC 5737)
    (ipaddress.ip_network("192.0.2.0/24"), "TEST-NET-1", "AS64496", "US"),
    (ipaddress.ip_network("198.51.100.0/24"), "TEST-NET-2", "AS64497", "EU"),
    (ipaddress.ip_network("203.0.113.0/24"), "TEST-NET-3", "AS64498", "AP"),
    # Private / Localhost
    (ipaddress.ip_network("10.0.0.0/8"), "PRIVATE-A", "AS0", "LOCAL"),
    (ipaddress.ip_network("172.16.0.0/12"), "PRIVATE-B", "AS0", "LOCAL"),
    (ipaddress.ip_network("192.168.0.0/16"), "PRIVATE-C", "AS0", "LOCAL"),
    (ipaddress.ip_network("127.0.0.0/8"), "LOOPBACK", "AS0", "LOCAL"),
]

class GeoIPService:
    def __init__(self):
        self.city_db_path = settings.GEOIP_DB_PATH
        self.asn_db_path = settings.GEOIP_ASN_DB_PATH
        self.city_reader = None
        self.asn_reader = None
        self._initialize_readers()

    def _initialize_readers(self):
        """Attempts to initialize MaxMind DB readers if files exist and library is available."""
        try:
            import maxminddb
            if os.path.exists(self.city_db_path):
                self.city_reader = maxminddb.open_database(self.city_db_path)
                logger.info("GeoIP City database initialized from %s", self.city_db_path)
            else:
                logger.info("GeoIP City database not found at %s. Operating in offline fallback mode.", self.city_db_path)

            if os.path.exists(self.asn_db_path):
                self.asn_reader = maxminddb.open_database(self.asn_db_path)
                logger.info("GeoIP ASN database initialized from %s", self.asn_db_path)
            else:
                logger.info("GeoIP ASN database not found at %s. Operating in offline fallback mode.", self.asn_db_path)
        except ImportError:
            logger.info("maxminddb module not installed. Operating in offline fallback resolution mode.")
        except Exception as e:
            logger.warning("Notice during GeoIP initialization: %s. Using fallback resolver.", e)

    def lookup(self, ip_str: str) -> Dict[str, Any]:
        """
        Resolves IP to country, city, ASN, and coordinate metadata.
        Guaranteed not to throw on invalid IP or missing database.
        """
        if not ip_str or not isinstance(ip_str, str):
            return {
                "ip": str(ip_str),
                "valid": False,
                "country": "UNKNOWN",
                "city": "Unknown",
                "asn": "UNKNOWN",
                "asn_org": "Unknown",
                "is_fallback": True,
                "status": "INVALID_IP"
            }

        cleaned_ip = ip_str.strip()
        try:
            ip_obj = ipaddress.ip_address(cleaned_ip)
        except ValueError:
            return {
                "ip": cleaned_ip,
                "valid": False,
                "country": "UNKNOWN",
                "city": "Unknown",
                "asn": "UNKNOWN",
                "asn_org": "Unknown",
                "is_fallback": True,
                "status": "INVALID_SYNTAX"
            }

        # 1. Try MMDB lookup if readers are open
        country = None
        city = None
        asn = None
        asn_org = None

        if self.city_reader:
            try:
                res = self.city_reader.get(cleaned_ip)
                if res and isinstance(res, dict):
                    country_data = res.get("country", {}) or res.get("registered_country", {})
                    country = country_data.get("iso_code")
                    city_data = res.get("city", {})
                    names = city_data.get("names", {})
                    city = names.get("en")
            except Exception:
                pass

        if self.asn_reader:
            try:
                res = self.asn_reader.get(cleaned_ip)
                if res and isinstance(res, dict):
                    num = res.get("autonomous_system_number")
                    if num:
                        asn = f"AS{num}"
                    asn_org = res.get("autonomous_system_organization")
            except Exception:
                pass

        # 2. Check static offline fallback ranges
        if not country or not asn:
            for net, label, static_asn, static_country in STATIC_OFFLINE_RANGES:
                if ip_obj in net:
                    country = country or static_country
                    city = city or label
                    asn = asn or static_asn
                    asn_org = asn_org or label
                    break

        # 3. Default fallback for unmapped public addresses
        return {
            "ip": cleaned_ip,
            "valid": True,
            "country": country or "XX",
            "city": city or "Unknown",
            "asn": asn or "AS0",
            "asn_org": asn_org or "Unknown",
            "is_fallback": (self.city_reader is None and self.asn_reader is None),
            "status": "RESOLVED"
        }

    def is_operational(self) -> bool:
        """Returns True if GeoIP resolution is ready (either via MMDB or offline static fallback)."""
        return True

    def validate_status(self) -> Dict[str, Any]:
        """Provides status diagnostics for system telemetry and offline validation."""
        return {
            "city_db_configured_path": self.city_db_path,
            "city_db_exists": os.path.exists(self.city_db_path),
            "asn_db_configured_path": self.asn_db_path,
            "asn_db_exists": os.path.exists(self.asn_db_path),
            "active_mode": "MMDB" if (self.city_reader or self.asn_reader) else "OFFLINE_FALLBACK",
            "offline_ranges_loaded": len(STATIC_OFFLINE_RANGES),
            "is_operational": True
        }

geoip_service = GeoIPService()
