#!/usr/bin/env python3
"""
Simple Data Generator (SDG) - Python Edition
Migrated from Java (iamhowardtheduck/SDGv2)
Generates configurable random data and indexes it into Elasticsearch.

Field types match the official supported_fields.md from the original Java app.
"""

import argparse
import hashlib
import ipaddress
import logging
import math
import random
import string
import sys
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import yaml
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("sdg")

# ─────────────────────────────────────────────────────────────────────────────
# Static data tables
# ─────────────────────────────────────────────────────────────────────────────
US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
]

US_CITIES = [
    "New York City", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte",
    "Indianapolis", "San Francisco", "Seattle", "Denver", "Nashville",
    "Oklahoma City", "El Paso", "Washington", "Boston", "Memphis",
    "Louisville", "Portland", "Las Vegas", "Baltimore", "Milwaukee",
    "Albuquerque", "Tucson", "Fresno", "Sacramento", "Mesa",
    "Kansas City", "Atlanta", "Omaha", "Colorado Springs", "Raleigh",
    "Long Beach", "Virginia Beach", "Minneapolis", "Tampa", "New Orleans",
    "Honolulu", "Arlington", "Wichita", "Cleveland", "Bakersfield",
]

STREET_NAMES = [
    "Main St", "Oak Ave", "Maple Dr", "Cedar Blvd", "Elm St",
    "Washington Blvd", "Park Ave", "Lake Dr", "Hill Rd", "River Rd",
    "Forest Ln", "Sunset Blvd", "Valley Rd", "Spring St", "Meadow Ln",
    "Lincoln Ave", "Highland Dr", "Willow Way", "Pine St", "Ridge Rd",
]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
    "Linda", "William", "Barbara", "David", "Elizabeth", "Richard",
    "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
    "Christopher", "Lisa", "Daniel", "Nancy", "Matthew", "Betty",
    "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Dorothy", "Paul", "Kimberly", "Andrew", "Emily",
    "Kenneth", "Donna", "George", "Michelle", "Joshua", "Carol",
    "Kevin", "Amanda", "Brian", "Melissa", "Edward", "Deborah",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts",
]

GROUPS = [
    "Engineering", "Sales", "Marketing", "Finance", "HR", "Legal",
    "Operations", "Product", "Design", "Support", "Security", "IT",
    "Research", "Executive", "Procurement", "Logistics", "Data Science",
    "DevOps", "QA", "Business Development",
]

TEAM_NAMES = [
    "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot",
    "Phoenix", "Vanguard", "Titan", "Nexus", "Apex", "Zenith",
    "Hydra", "Atlas", "Orion", "Polaris", "Catalyst", "Horizon",
    "Pinnacle", "Velocity",
]

# Ancient gods — matches Java hostname implementation
HOSTNAMES = [
    "zeus", "hera", "poseidon", "demeter", "athena", "apollo",
    "artemis", "ares", "aphrodite", "hephaestus", "hermes", "dionysus",
    "odin", "thor", "loki", "freya", "tyr", "baldur", "heimdall", "frigg",
    "ra", "osiris", "isis", "horus", "anubis", "thoth", "set", "nut",
    "brahma", "vishnu", "shiva", "indra", "agni", "varuna", "krishna",
]

APP_NAMES = [
    "nginx", "apache", "tomcat", "node", "django", "flask", "rails",
    "spring-boot", "express", "fastapi", "haproxy", "varnish",
    "elasticsearch", "kibana", "logstash", "filebeat", "redis", "kafka",
    "rabbitmq", "postgres", "mysql", "mongodb", "cassandra", "consul",
    "vault", "prometheus", "grafana", "jenkins", "gitlab-ci", "airflow",
]

PRODUCT_NAMES = [
    "Widget Pro", "DataSync", "CloudVault", "NetShield", "FlowTracker",
    "LogMaster", "SecureKey", "MetricsPulse", "StreamLine", "CacheBoost",
    "QueryOptimizer", "EventBridge", "TokenGate", "AuditTrail", "PipeRunner",
    "AlertNow", "SnapIndex", "ReplicaSync", "JobQueue", "PolicyEngine",
]

OCCUPATIONS = [
    "Software Engineer", "Data Scientist", "DevOps Engineer", "Product Manager",
    "UX Designer", "Security Analyst", "Network Engineer", "Database Administrator",
    "Systems Architect", "QA Engineer", "Technical Writer", "Scrum Master",
    "Business Analyst", "Cloud Architect", "ML Engineer", "Site Reliability Engineer",
    "IT Manager", "Solutions Architect", "Frontend Developer", "Backend Developer",
]

GOT_CHARACTERS = [
    "Jon Snow", "Daenerys Targaryen", "Tyrion Lannister", "Cersei Lannister",
    "Jaime Lannister", "Arya Stark", "Sansa Stark", "Bran Stark",
    "Ned Stark", "Robert Baratheon", "Joffrey Baratheon", "Stannis Baratheon",
    "Melisandre", "Davos Seaworth", "Samwell Tarly", "Brienne of Tarth",
    "Sandor Clegane", "Gregor Clegane", "Petyr Baelish", "Varys",
    "Theon Greyjoy", "Yara Greyjoy", "Margaery Tyrell", "Olenna Tyrell",
    "Oberyn Martell", "Missandei", "Grey Worm", "Jorah Mormont",
]

CN_FACTS = [
    "Chuck Norris can divide by zero.",
    "Chuck Norris counted to infinity. Twice.",
    "Chuck Norris can slam a revolving door.",
    "Chuck Norris doesn't push the elevator button, the elevator button pushes itself.",
    "Chuck Norris's keyboard has no Ctrl key because Chuck Norris is always in control.",
    "Chuck Norris doesn't need garbage collection because he doesn't call, he collects.",
    "Chuck Norris can write infinite loops and exit them.",
    "Chuck Norris's programs don't have bugs, they have features.",
    "Chuck Norris can make a class that is both abstract and final.",
    "Chuck Norris solved the halting problem. Twice.",
]

TIMEZONES = [
    "UTC", "America/New_York", "America/Chicago", "America/Denver",
    "America/Los_Angeles", "America/Anchorage", "Pacific/Honolulu",
    "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Moscow",
    "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata", "Asia/Dubai",
    "Australia/Sydney", "Pacific/Auckland", "America/Sao_Paulo",
    "America/Toronto", "America/Vancouver",
]

DOMAINS = [
    "example.com", "acme.org", "techcorp.io", "globalnet.co",
    "infosys.net", "datahub.io", "cloudbase.tech", "webworks.com",
    "apexdata.net", "streamline.co", "nexuslab.org", "pivotal.io",
]

PATHS = [
    "/var/log/app.log", "/etc/nginx/nginx.conf", "/usr/local/bin/app",
    "/home/user/documents/report.pdf", "/tmp/session_cache",
    "/opt/services/config.yaml", "/data/exports/output.csv",
    "/var/lib/elasticsearch/data", "/etc/ssl/certs/ca.pem",
    "/srv/www/html/index.html", "/proc/sys/kernel/hostname",
    "/run/app/app.pid",
]

URL_PATHS = [
    "/", "/index.html", "/api/v1/users", "/api/v1/orders", "/api/v2/products",
    "/search", "/login", "/logout", "/dashboard", "/admin",
    "/static/css/main.css", "/static/js/app.js", "/favicon.ico",
    "/api/health", "/api/metrics",
]

WORDS = [
    "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing",
    "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore",
    "et", "dolore", "magna", "aliqua", "enim", "ad", "minim", "veniam",
    "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi",
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_range(range_str: Optional[str], default_min=0, default_max=1_000_000):
    if not range_str:
        return default_min, default_max
    parts = str(range_str).split(",")
    if len(parts) == 2:
        return float(parts[0].strip()), float(parts[1].strip())
    return default_min, default_max


def _parse_custom_list(field: Dict) -> List[str]:
    raw = field.get("custom_list", "")
    if isinstance(raw, list):
        return [str(v) for v in raw]
    return [v.strip() for v in str(raw).split(",") if v.strip()]


# ─────────────────────────────────────────────────────────────────────────────
# Official field generators  (supported_fields.md)
# ─────────────────────────────────────────────────────────────────────────────

# Primitives
def gen_int(field: Dict) -> int:
    lo, hi = _parse_range(field.get("range"), 0, 1_000_000)
    return random.randint(int(lo), int(hi))

def gen_float(field: Dict) -> float:
    lo, hi = _parse_range(field.get("range"), 0.0, 1_000_000.0)
    return round(random.uniform(lo, hi), 2)

def gen_boolean(_field: Dict) -> bool:
    return random.choice([True, False])

# Names
def gen_full_name(_field: Dict) -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def gen_first_name(_field: Dict) -> str:
    return random.choice(FIRST_NAMES)

def gen_last_name(_field: Dict) -> str:
    return random.choice(LAST_NAMES)

def gen_group(_field: Dict) -> str:
    return random.choice(GROUPS)

def gen_team_name(_field: Dict) -> str:
    return random.choice(TEAM_NAMES)

# Addresses
def gen_full_address(_field: Dict) -> str:
    num    = random.randint(1, 9999)
    street = random.choice(STREET_NAMES)
    city   = random.choice(US_CITIES)
    state  = random.choice(US_STATES)
    zc     = f"{random.randint(10000, 99999):05d}"
    return f"{num} {street}, {city}, {state} {zc}"

def gen_street_address(_field: Dict) -> str:
    return f"{random.randint(1, 9999)} {random.choice(STREET_NAMES)}"

def gen_city(_field: Dict) -> str:
    return random.choice(US_CITIES)

def gen_state(_field: Dict) -> str:
    return random.choice(US_STATES)

def gen_zipcode(_field: Dict) -> str:
    return f"{random.randint(10000, 99999):05d}"

# Special numbers
def gen_credit_card_number(_field: Dict) -> str:
    """Luhn-valid 16-digit Visa test card number."""
    prefix = [int(d) for d in random.choice(["4111", "4222", "4532", "4716"])]
    digits = prefix[:]
    while len(digits) < 15:
        digits.append(random.randint(0, 9))
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    digits.append((10 - (total % 10)) % 10)
    return "".join(str(d) for d in digits)

def gen_phone_number(_field: Dict) -> str:
    return (f"+1-{random.randint(200,999):03d}-"
            f"{random.randint(100,999):03d}-"
            f"{random.randint(1000,9999):04d}")

def gen_ssn(_field: Dict) -> str:
    return (f"{random.randint(100,999):03d}-"
            f"{random.randint(10,99):02d}-"
            f"{random.randint(1000,9999):04d}")

def gen_uuid(_field: Dict) -> str:
    return str(uuid.uuid4())

def gen_product_name(_field: Dict) -> str:
    return random.choice(PRODUCT_NAMES)

def gen_hash(_field: Dict) -> str:
    return hashlib.md5(str(random.random()).encode()).hexdigest()

# Random from lists
def gen_random_string_from_list(field: Dict) -> str:
    items = _parse_custom_list(field)
    return random.choice(items) if items else ""

def gen_random_integer_from_list(field: Dict) -> int:
    items = _parse_custom_list(field)
    return int(random.choice(items)) if items else 0

def gen_random_float_from_list(field: Dict) -> float:
    items = _parse_custom_list(field)
    return float(random.choice(items)) if items else 0.0

def gen_random_long_from_list(field: Dict) -> int:
    items = _parse_custom_list(field)
    return int(random.choice(items)) if items else 0

# Misc
def gen_ipv4(_field: Dict) -> str:
    while True:
        parts = [random.randint(1, 254) for _ in range(4)]
        if parts[0] not in (10, 127, 172, 192):
            return ".".join(str(p) for p in parts)

def gen_random_cn_fact(_field: Dict) -> str:
    return random.choice(CN_FACTS)

def gen_random_got_character(_field: Dict) -> str:
    return random.choice(GOT_CHARACTERS)

def gen_random_occupation(_field: Dict) -> str:
    return random.choice(OCCUPATIONS)

def gen_empty(_field: Dict) -> str:
    return ""

def gen_path(_field: Dict) -> str:
    return random.choice(PATHS)

def gen_hostname(_field: Dict) -> str:
    suffix = random.choice(["",
                             f"-{random.randint(1, 99):02d}",
                             f".{random.choice(['internal', 'local', 'corp'])}"])
    return random.choice(HOSTNAMES) + suffix

def gen_appname(_field: Dict) -> str:
    return random.choice(APP_NAMES)

def gen_url(_field: Dict) -> str:
    scheme = random.choice(["http", "https"])
    tld    = random.choice(["com", "org", "net", "io", "co"])
    name   = "".join(random.choices(WORDS, k=2))
    path   = random.choice(URL_PATHS)
    return f"{scheme}://{name}.{tld}{path}"

def gen_mac_address(_field: Dict) -> str:
    return ":".join(f"{random.randint(0,255):02x}" for _ in range(6))

def gen_email(_field: Dict) -> str:
    first   = random.choice(FIRST_NAMES).lower()
    last    = random.choice(LAST_NAMES).lower()
    domains = ["gmail.com", "yahoo.com", "hotmail.com",
               "company.com", "example.org", "outlook.com"]
    return f"{first}.{last}{random.randint(1,999)}@{random.choice(domains)}"

def gen_domain(_field: Dict) -> str:
    return random.choice(DOMAINS)

def gen_date(field: Dict) -> str:
    lo, hi    = _parse_range(field.get("range"), 0, 365 * 2)
    days_back = random.randint(int(lo), int(hi))
    dt        = datetime.now() - timedelta(days=days_back)
    return dt.strftime("%Y-%m-%d")

def gen_timezone(_field: Dict) -> str:
    return random.choice(TIMEZONES)

def gen_constant(field: Dict) -> Any:
    return field.get("value", "")


# ─────────────────────────────────────────────────────────────────────────────
# Extra types (not in official doc but useful; kept as aliases)
# ─────────────────────────────────────────────────────────────────────────────

def gen_long(field: Dict) -> int:
    lo, hi = _parse_range(field.get("range"), 0, 9_999_999_999)
    return random.randint(int(lo), int(hi))

def gen_double(field: Dict) -> float:
    lo, hi = _parse_range(field.get("range"), 0.0, 1_000_000.0)
    return round(random.uniform(lo, hi), 6)

def gen_timestamp(field: Dict) -> str:
    """ISO-8601 UTC timestamp. range = minutes back from now."""
    lo, hi       = _parse_range(field.get("range"), 0, 60 * 24 * 7)
    minutes_back = random.uniform(lo, hi)
    dt           = datetime.now(timezone.utc) - timedelta(minutes=minutes_back)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def gen_ipv6(_field: Dict) -> str:
    return str(ipaddress.IPv6Address(random.randint(0, 2**128 - 1)))

def gen_geo_point(_field: Dict) -> Dict:
    return {
        "lat": round(random.uniform(-90.0, 90.0), 6),
        "lon": round(random.uniform(-180.0, 180.0), 6),
    }

def gen_sequence(field: Dict, state: Dict) -> int:
    key   = field["name"]
    start = int(field.get("start", 1))
    step  = int(field.get("step", 1))
    if key not in state:
        state[key] = start
    val         = state[key]
    state[key] += step
    return val


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher
# Official names from supported_fields.md appear first.
# Aliases / extras follow so existing configs keep working.
# ─────────────────────────────────────────────────────────────────────────────

GENERATORS: Dict[str, Any] = {
    # ── Official types (supported_fields.md) ──────────────────────────────
    "int":                      gen_int,
    "float":                    gen_float,
    "boolean":                  gen_boolean,
    "full_name":                gen_full_name,
    "first_name":               gen_first_name,
    "last_name":                gen_last_name,
    "group":                    gen_group,
    "team_name":                gen_team_name,
    "full_address":             gen_full_address,
    "street_address":           gen_street_address,
    "city":                     gen_city,
    "state":                    gen_state,
    "zipcode":                  gen_zipcode,
    "credit_card_number":       gen_credit_card_number,
    "phone_number":             gen_phone_number,
    "ssn":                      gen_ssn,
    "uuid":                     gen_uuid,
    "product_name":             gen_product_name,
    "hash":                     gen_hash,
    "random_string_from_list":  gen_random_string_from_list,
    "random_integer_from_list": gen_random_integer_from_list,
    "random_float_from_list":   gen_random_float_from_list,
    "random_long_from_list":    gen_random_long_from_list,
    "ipv4":                     gen_ipv4,
    "random_cn_fact":           gen_random_cn_fact,
    "random_got_character":     gen_random_got_character,
    "random_occupation":        gen_random_occupation,
    "empty":                    gen_empty,
    "path":                     gen_path,
    "hostname":                 gen_hostname,
    "appname":                  gen_appname,
    "url":                      gen_url,
    "mac_address":              gen_mac_address,
    "email":                    gen_email,
    "domain":                   gen_domain,
    "date":                     gen_date,
    "timezone":                 gen_timezone,

    # ── Aliases / extras ──────────────────────────────────────────────────
    "integer":                  gen_int,
    "long":                     gen_long,
    "double":                   gen_double,
    "bool":                     gen_boolean,
    "timestamp":                gen_timestamp,
    "ip":                       gen_ipv4,
    "ipv6":                     gen_ipv6,
    "mac":                      gen_mac_address,
    "guid":                     gen_uuid,
    "phone":                    gen_phone_number,
    "zip":                      gen_zipcode,
    "zip_code":                 gen_zipcode,
    "geo_point":                gen_geo_point,
    "geoPoint":                 gen_geo_point,
    "location":                 gen_geo_point,
    "firstName":                gen_first_name,
    "lastName":                 gen_last_name,
    "fullName":                 gen_full_name,
    "name":                     gen_full_name,
    "host":                     gen_hostname,
    "constant":                 gen_constant,
    "static":                   gen_constant,
}


def generate_value(field: Dict, state: Optional[Dict] = None) -> Any:
    # Constants: 'value' key present, no 'type' key (as per supported_fields.md)
    if "value" in field and "type" not in field:
        return field["value"]

    field_type = field.get("type", "")
    if field_type == "sequence":
        if state is None:
            state = {}
        return gen_sequence(field, state)

    generator = GENERATORS.get(field_type)
    if generator is None:
        log.warning("Unknown field type '%s' for field '%s' — returning empty string",
                    field_type, field.get("name", "?"))
        return ""

    return generator(field)


def build_document(fields: List[Dict], seq_state: Dict) -> Dict:
    doc: Dict = {}
    for field in fields:
        key   = field["name"]
        value = generate_value(field, seq_state)
        # Dot-notation → nested dict  e.g. "name.first" → {"name": {"first": ...}}
        if "." in key:
            parts     = key.split(".")
            container = doc
            for part in parts[:-1]:
                container = container.setdefault(part, {})
            container[parts[-1]] = value
        else:
            doc[key] = value
    return doc


# ─────────────────────────────────────────────────────────────────────────────
# Peak-time pacing  (uses local host time, matching the Java app)
# ─────────────────────────────────────────────────────────────────────────────

def _peak_multiplier(peak_time_str: Optional[str]) -> float:
    """
    Sine-wave sleep multiplier based on distance from peakTime.
    Near peak → ~0.5 (faster).  Far from peak → ~2.0 (slower).
    Uses local host time — identical to the Java implementation.
    """
    if not peak_time_str:
        return 1.0
    try:
        peak_h, peak_m, peak_s = map(int, str(peak_time_str).split(":"))
        now          = datetime.now()
        peak_sec     = peak_h * 3600 + peak_m * 60 + peak_s
        now_sec      = now.hour * 3600 + now.minute * 60 + now.second
        diff         = abs(now_sec - peak_sec)
        diff         = min(diff, 86400 - diff)
        fraction     = diff / 43200.0
        return 0.5 + 1.5 * math.sin(fraction * math.pi / 2) ** 2
    except Exception:
        return 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Elasticsearch helpers
# ─────────────────────────────────────────────────────────────────────────────

def build_es_client(cfg: Dict) -> Elasticsearch:
    scheme   = cfg.get("elasticsearchScheme", "https")
    host     = cfg.get("elasticsearchHost", "localhost")
    port     = int(cfg.get("elasticsearchPort", 9200))
    user     = cfg.get("elasticsearchUser", "elastic")
    password = cfg.get("elasticsearchPassword", "")
    api_key_enabled = cfg.get("elasticsearchApiKeyEnabled", False)
    api_key_id      = cfg.get("elasticsearchApiKeyId", "")
    api_key_secret  = cfg.get("elasticsearchApiKeySecret", "")

    hosts = [{"host": host, "port": port, "scheme": scheme}]

    if api_key_enabled and api_key_id and api_key_secret:
        return Elasticsearch(
            hosts,
            api_key=(api_key_id, api_key_secret),
            verify_certs=cfg.get("verifyCerts", True),
            ssl_show_warn=False,
        )
    return Elasticsearch(
        hosts,
        http_auth=(user, password),
        verify_certs=cfg.get("verifyCerts", True),
        ssl_show_warn=False,
    )


def ensure_index(client: Elasticsearch, workload: Dict) -> None:
    index_name     = workload["indexName"]
    primary_shards = workload.get("primaryShardCount", 1)
    replica_shards = workload.get("replicaShardCount", 1)
    purge          = workload.get("purgeOnStart", False)
    data_stream    = workload.get("dataStream", False)

    if purge:
        try:
            if data_stream:
                client.indices.delete_data_stream(name=index_name,
                                                  ignore_unavailable=True)
            else:
                client.indices.delete(index=index_name, ignore_unavailable=True)
            log.info("Purged: %s", index_name)
        except Exception as ex:
            log.warning("Could not purge %s: %s", index_name, ex)

    if data_stream:
        return

    try:
        if not client.indices.exists(index=index_name):
            client.indices.create(index=index_name, body={
                "settings": {
                    "number_of_shards":   primary_shards,
                    "number_of_replicas": replica_shards,
                }
            })
            log.info("Created index: %s (shards=%d, replicas=%d)",
                     index_name, primary_shards, replica_shards)
    except Exception as ex:
        log.warning("Could not ensure index %s: %s", index_name, ex)


# ─────────────────────────────────────────────────────────────────────────────
# Worker thread
# ─────────────────────────────────────────────────────────────────────────────

class WorkloadWorker(threading.Thread):
    def __init__(self, workload: Dict, client: Elasticsearch,
                 thread_idx: int, stop_event: threading.Event):
        name = f"{workload.get('workloadName', 'workload')}-t{thread_idx}"
        super().__init__(name=name, daemon=True)
        self.workload     = workload
        self.client       = client
        self.stop_event   = stop_event
        self.seq_state: Dict = {}
        self.docs_indexed = 0
        self.errors       = 0

    def run(self):
        wl         = self.workload
        index_name = wl["indexName"]
        sleep_ms   = int(wl.get("workloadSleep", 1000))
        bulk_depth = int(wl.get("elasticsearchBulkQueueDepth", 0))
        peak_time  = wl.get("peakTime")
        fields     = wl.get("fields", [])
        data_stream = wl.get("dataStream", False)

        log.info("[%s] Starting — index=%s sleep=%dms bulk=%d",
                 self.name, index_name, sleep_ms, bulk_depth)

        while not self.stop_event.is_set():
            try:
                if bulk_depth > 0:
                    self._send_bulk(index_name, fields, bulk_depth, data_stream)
                else:
                    self._send_single(index_name, fields, data_stream)

                sleep_sec = (sleep_ms * _peak_multiplier(peak_time)) / 1000.0
                self.stop_event.wait(timeout=sleep_sec)

            except ConnectionError as ex:
                log.error("[%s] Connection error: %s — retrying in 5s", self.name, ex)
                self.errors += 1
                self.stop_event.wait(timeout=5)
            except Exception as ex:
                log.error("[%s] Error: %s", self.name, ex)
                self.errors += 1
                self.stop_event.wait(timeout=2)

        log.info("[%s] Stopped. docs=%d errors=%d",
                 self.name, self.docs_indexed, self.errors)

    def _send_single(self, index_name, fields, data_stream):
        doc = build_document(fields, self.seq_state)
        if "@timestamp" not in doc:
            doc["@timestamp"] = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        self.client.index(index=index_name, body=doc)
        self.docs_indexed += 1

    def _send_bulk(self, index_name, fields, bulk_depth, data_stream):
        actions = []
        for _ in range(bulk_depth):
            doc = build_document(fields, self.seq_state)
            if "@timestamp" not in doc:
                doc["@timestamp"] = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            op = "create" if data_stream else "index"
            actions.append({"_op_type": op, "_index": index_name, "_source": doc})

        success, failed = helpers.bulk(self.client, actions, raise_on_error=False)
        self.docs_indexed += success
        if failed:
            self.errors += len(failed)
            log.warning("[%s] Bulk errors: %d", self.name, len(failed))


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Simple Data Generator (Python) — streams random data to Elasticsearch"
    )
    parser.add_argument("config", help="Path to YAML config file")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.getLogger().setLevel(getattr(logging, args.log_level))

    with open(args.config) as fh:
        cfg = yaml.safe_load(fh)

    log.info("Target: %s://%s:%s",
             cfg.get("elasticsearchScheme", "https"),
             cfg.get("elasticsearchHost", "localhost"),
             cfg.get("elasticsearchPort", 9200))

    client = build_es_client(cfg)
    try:
        info = client.info()
        log.info("Connected to Elasticsearch %s", info["version"]["number"])
    except Exception as ex:
        log.error("Cannot connect to Elasticsearch: %s", ex)
        sys.exit(1)

    workloads = cfg.get("workloads", [])
    if not workloads:
        log.error("No workloads defined in config.")
        sys.exit(1)

    stop_event = threading.Event()
    workers: List[WorkloadWorker] = []

    for workload in workloads:
        ensure_index(client, workload)
        for i in range(int(workload.get("workloadThreads", 1))):
            w = WorkloadWorker(workload, client, i, stop_event)
            workers.append(w)
            w.start()

    log.info("Started %d worker thread(s). Press Ctrl+C to stop.", len(workers))

    try:
        while True:
            time.sleep(10)
            log.info("Stats: docs=%d errors=%d threads=%d",
                     sum(w.docs_indexed for w in workers),
                     sum(w.errors for w in workers),
                     sum(1 for w in workers if w.is_alive()))
    except KeyboardInterrupt:
        log.info("Shutting down…")
        stop_event.set()
        for w in workers:
            w.join(timeout=10)
        log.info("Final: docs=%d errors=%d",
                 sum(w.docs_indexed for w in workers),
                 sum(w.errors for w in workers))


if __name__ == "__main__":
    main()
