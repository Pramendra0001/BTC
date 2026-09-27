"""
BTC-SHIELD GeoIP and Network Resolution Service.
Provides offline and local IP-to-Country and IP-to-ASN resolution with strict dual-mode architecture:

1. REAL LOCAL OPEN-SOURCE MMDB RESOLUTION:
   When local DB-IP Lite or MaxMind database files (e.g. DB-IP-Country-Lite.mmdb, DB-IP-ASN-Lite.mmdb)
   are present and the `maxminddb` reader library is available, real binary database lookups are executed.
   Normalized schemas extract ISO country code, English country name, Autonomous System Number (ASN),
   and Autonomous System Organization (AS Org) with full legal attribution.

2. DETERMINISTIC OFFLINE RFC FALLBACK:
   When MMDB database files are unavailable or when resolving RFC 5737 documentation testnets
   and RFC 1918 private subnets, the service resolves deterministically with zero external egress.
"""
import os
import ipaddress
import logging
from typing import Dict, Any, Optional, Tuple, List
from app.core.config import settings

logger = logging.getLogger("btcshield.geoip")

# Static offline fallback ranges for standard documentation & private networks (RFC 5737, RFC 1918, RFC 1122)
STATIC_OFFLINE_RANGES = [
    # TEST-NET-1, TEST-NET-2, TEST-NET-3 (RFC 5737)
    (ipaddress.ip_network("192.0.2.0/24"), "TEST-NET-1", "United States", "AS64496", "US"),
    (ipaddress.ip_network("198.51.100.0/24"), "TEST-NET-2", "European Union", "AS64497", "EU"),
    (ipaddress.ip_network("203.0.113.0/24"), "TEST-NET-3", "Asia Pacific", "AS64498", "AP"),
    # Private / Localhost (RFC 1918 / RFC 1122)
    (ipaddress.ip_network("10.0.0.0/8"), "PRIVATE-A", "Internal Network", "AS0", "LOCAL"),
    (ipaddress.ip_network("172.16.0.0/12"), "PRIVATE-B", "Internal Network", "AS0", "LOCAL"),
    (ipaddress.ip_network("192.168.0.0/16"), "PRIVATE-C", "Internal Network", "AS0", "LOCAL"),
    (ipaddress.ip_network("127.0.0.0/8"), "LOOPBACK", "Localhost", "AS0", "LOCAL"),
]

class GeoIPService:
    def __init__(self):
        self.city_db_path = settings.GEOIP_DB_PATH
        self.asn_db_path = settings.GEOIP_ASN_DB_PATH
        self.resolved_city_path: Optional[str] = None
        self.resolved_asn_path: Optional[str] = None
        self.city_reader = None
        self.asn_reader = None
        self.geoip_source: str = "OFFLINE_FALLBACK"
        self.attribution: str = "Deterministic RFC 5737 / RFC 1918 local offline resolution"
        self._initialize_readers()

    def _find_file(self, candidate_paths: List[str]) -> Optional[str]:
        for p in candidate_paths:
            if not p:
                continue
            # Try absolute or relative to repo root / working directory
            if os.path.isabs(p) and os.path.exists(p):
                return p
            if os.path.exists(p):
                return p
            # Also check relative to workspace
            alt_path = os.path.join(os.getcwd(), p)
            if os.path.exists(alt_path):
                return alt_path
        return None

    def _initialize_readers(self):
        """Attempts to discover and initialize local MMDB readers."""
        country_candidates = [
            self.city_db_path,
            "offline/geoip/DB-IP-Country-Lite.mmdb",
            "data/geoip/DB-IP-Country-Lite.mmdb",
            "offline/geoip/GeoLite2-City.mmdb",
            "offline/geoip/GeoLite2-Country.mmdb",
            "data/geoip/GeoLite2-City.mmdb",
            "data/geoip/GeoLite2-Country.mmdb",
        ]

        asn_candidates = [
            self.asn_db_path,
            "offline/geoip/DB-IP-ASN-Lite.mmdb",
            "data/geoip/DB-IP-ASN-Lite.mmdb",
            "offline/geoip/GeoLite2-ASN.mmdb",
            "data/geoip/GeoLite2-ASN.mmdb",
        ]

        self.resolved_city_path = self._find_file(country_candidates)
        self.resolved_asn_path = self._find_file(asn_candidates)

        try:
            import maxminddb
            if self.resolved_city_path:
                self.city_reader = maxminddb.open_database(self.resolved_city_path)
                logger.info("GeoIP Country/City database initialized from %s", self.resolved_city_path)

            if self.resolved_asn_path:
                self.asn_reader = maxminddb.open_database(self.resolved_asn_path)
                logger.info("GeoIP ASN database initialized from %s", self.resolved_asn_path)

            if self.city_reader or self.asn_reader:
                # Determine source and attribution
                path_str = f"{self.resolved_city_path or ''} {self.resolved_asn_path or ''}".lower()
                if "db-ip" in path_str:
                    self.geoip_source = "DB-IP-Lite"
                    self.attribution = "IP geolocation data provided by DB-IP.com"
                elif "geolite" in path_str or "maxmind" in path_str:
                    self.geoip_source = "GeoLite2"
                    self.attribution = "This product includes GeoLite2 data created by MaxMind, available from maxmind.com"
                else:
                    self.geoip_source = "LOCAL_MMDB"
                    self.attribution = "IP geolocation data provided by local MMDB database"
            else:
                self.geoip_source = "OFFLINE_FALLBACK"
                self.attribution = "Deterministic RFC 5737 / RFC 1918 testnet & private mappings"

        except ImportError:
            logger.info("maxminddb module not installed. Operating in offline fallback resolution mode.")
            self.geoip_source = "OFFLINE_FALLBACK"
            self.attribution = "Deterministic RFC 5737 / RFC 1918 testnet & private mappings"
        except Exception as e:
            logger.warning("Notice during GeoIP initialization: %s. Using fallback resolver.", e)
            self.geoip_source = "OFFLINE_FALLBACK"
            self.attribution = "Deterministic RFC 5737 / RFC 1918 testnet & private mappings"

    def lookup(self, ip_str: str) -> Dict[str, Any]:
        """
        Resolves IP to country, country_name, city, ASN, and AS organization metadata.
        Guaranteed not to throw on invalid IP or missing database.
        """
        if not ip_str or not isinstance(ip_str, str):
            return {
                "ip": str(ip_str),
                "valid": False,
                "country": "UNKNOWN",
                "country_name": "Unknown",
                "city": "Unknown",
                "asn": "UNKNOWN",
                "asn_org": "Unknown",
                "is_fallback": True,
                "mode": "OFFLINE_FALLBACK",
                "source": self.geoip_source,
                "attribution": self.attribution,
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
                "country_name": "Unknown",
                "city": "Unknown",
                "asn": "UNKNOWN",
                "asn_org": "Unknown",
                "is_fallback": True,
                "mode": "OFFLINE_FALLBACK",
                "source": self.geoip_source,
                "attribution": self.attribution,
                "status": "INVALID_SYNTAX"
            }

        # 1. Try MMDB lookup if readers are open
        country = None
        country_name = None
        city = None
        asn = None
        asn_org = None
        mmdb_hit = False

        if self.city_reader:
            try:
                res = self.city_reader.get(cleaned_ip)
                if res and isinstance(res, dict):
                    mmdb_hit = True
                    # Normalized extraction supporting DB-IP Lite and MaxMind schemas
                    country_data = res.get("country") or res.get("registered_country") or {}
                    if isinstance(country_data, dict):
                        country = country_data.get("iso_code")
                        names = country_data.get("names", {})
                        if isinstance(names, dict):
                            country_name = names.get("en")
                    elif isinstance(country_data, str):
                        country = country_data

                    if not country and "continent" in res:
                        continent_data = res.get("continent") or {}
                        if isinstance(continent_data, dict):
                            country = continent_data.get("code")
                            names = continent_data.get("names", {})
                            if isinstance(names, dict):
                                country_name = names.get("en")

                    city_data = res.get("city") or {}
                    if isinstance(city_data, dict):
                        city_names = city_data.get("names", {})
                        if isinstance(city_names, dict):
                            city = city_names.get("en")
                    elif isinstance(city_data, str):
                        city = city_data
            except Exception:
                pass

        if self.asn_reader:
            try:
                res = self.asn_reader.get(cleaned_ip)
                if res and isinstance(res, dict):
                    mmdb_hit = True
                    num = res.get("autonomous_system_number") or res.get("asn")
                    if num:
                        asn = f"AS{num}"
                    asn_org = res.get("autonomous_system_organization") or res.get("as_org") or res.get("organization")
            except Exception:
                pass

        # 2. Check static offline fallback ranges (e.g. for RFC 5737 / RFC 1918)
        if not country or not asn:
            for net, label, static_country_name, static_asn, static_country in STATIC_OFFLINE_RANGES:
                if ip_obj in net:
                    country = country or static_country
                    country_name = country_name or static_country_name
                    city = city or label
                    asn = asn or static_asn
                    asn_org = asn_org or label
                    break

        is_fallback = not mmdb_hit
        active_mode = "LOCAL_MMDB" if mmdb_hit else "OFFLINE_FALLBACK"

        # 3. Default fallback for unmapped public addresses
        return {
            "ip": cleaned_ip,
            "valid": True,
            "country": country or "XX",
            "country_name": country_name or "Unknown",
            "city": city or "Unknown",
            "asn": asn or "AS0",
            "asn_org": asn_org or "Unknown",
            "is_fallback": is_fallback,
            "mode": active_mode,
            "source": self.geoip_source if mmdb_hit else "DETERMINISTIC_OFFLINE_RFC",
            "attribution": self.attribution,
            "status": "RESOLVED"
        }

    def is_operational(self) -> bool:
        """Returns True if GeoIP resolution is ready (either via MMDB or offline static fallback)."""
        return True

    def validate_status(self) -> Dict[str, Any]:
        """Provides status diagnostics for system telemetry and offline validation."""
        is_mmdb = bool(self.city_reader or self.asn_reader)
        return {
            "city_db_configured_path": self.city_db_path,
            "city_db_exists": os.path.exists(self.city_db_path) if self.city_db_path else False,
            "city_db_resolved_path": self.resolved_city_path,
            "asn_db_configured_path": self.asn_db_path,
            "asn_db_exists": os.path.exists(self.asn_db_path) if self.asn_db_path else False,
            "asn_db_resolved_path": self.resolved_asn_path,
            "active_mode": "MMDB" if is_mmdb else "OFFLINE_FALLBACK",
            "geoip_mode": "LOCAL_MMDB" if is_mmdb else "OFFLINE_FALLBACK",
            "geoip_source": self.geoip_source,
            "attribution": self.attribution,
            "offline_ranges_loaded": len(STATIC_OFFLINE_RANGES),
            "status": "LOCAL_MMDB" if is_mmdb else "OFFLINE_FALLBACK",
            "is_operational": True
        }

geoip_service = GeoIPService()
