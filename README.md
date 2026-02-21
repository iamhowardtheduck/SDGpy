# SDGpy
YAML-based configuration for a Python-based SDG, forgive me Pahlsoft.

# Simple Data Generator — Python Edition

A complete Python migration of [iamhowardtheduck/SDGv2](https://github.com/iamhowardtheduck/SDGv2), minus APM functionality.

Streams configurable random data into Elasticsearch. Fully YAML-driven, multi-threaded, and compatible with the original Java app's config format.

---

## Requirements

- Python 3.9+
- Elasticsearch 7.x / 8.x  / 9.x cluster

## Installation

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python3 sdg.py your_config.yml
```

With debug logging:
```bash
python3 sdg.py your_config.yml --log-level DEBUG
```

---

## Config Format

The YAML config is fully compatible with the original Java SDGv2.

### Connection Settings

```yaml
elasticsearchScheme: https
elasticsearchHost: your-cluster.elastic.cloud
elasticsearchPort: 9243
elasticsearchUser: elastic
elasticsearchPassword: your-password

# API Key auth (alternative to user/password)
elasticsearchApiKeyEnabled: true
elasticsearchApiKeyId: your-key-id
elasticsearchApiKeySecret: your-key-secret

# SSL verification (default: true)
verifyCerts: true
```

### Workload Settings

```yaml
workloads:
  - workloadName: my_workload       # descriptive name
    indexName: my-index             # Elasticsearch index to write to
    workloadThreads: 2              # parallel threads for this workload
    workloadSleep: 500              # milliseconds between docs per thread
    primaryShardCount: 1            # shards for new index creation
    replicaShardCount: 0            # replicas for new index creation
    purgeOnStart: false             # delete + recreate index on startup
    peakTime: "17:00:00"            # optional sine-wave load pacing
    elasticsearchBulkQueueDepth: 0  # 0=single-doc; >0=bulk batch size
    dataStream: false               # true to write to a data stream
    fields:
      - name: my_field
        type: int
```

---

## Supported Field Types

### Numbers

| type | description | options |
|------|-------------|---------|
| `int` / `integer` | Random integer | `range: min,max` |
| `long` | Random long integer | `range: min,max` |
| `float` | Random float (2 decimals) | `range: min,max` |
| `double` | Random double (6 decimals) | `range: min,max` |

### Text

| type | description | options |
|------|-------------|---------|
| `string` | Random alphanumeric string | `length: N`, `chars: "abc..."` |
| `words` / `text` | Lorem ipsum–style words | `count: N` |

### Identity / People

| type | description |
|------|-------------|
| `firstName` / `first_name` | Random first name |
| `lastName` / `last_name` | Random last name |
| `fullName` / `name` | Full name |
| `email` | Email address |
| `phone` / `phoneNumber` | US phone number |
| `ssn` | SSN (###-##-####) |
| `uuid` / `guid` | UUID v4 |

### Geographic

| type | description |
|------|-------------|
| `state` | US state name |
| `city` | US city name |
| `country` | Country name |
| `zip` / `zipCode` | US zip code |
| `geo_point` / `geoPoint` / `location` | `{lat, lon}` object |

### Network

| type | description |
|------|-------------|
| `ip` / `ipv4` | IPv4 address (public range) |
| `ipv6` | IPv6 address |
| `mac` / `macAddress` | MAC address |
| `url` / `uri` | Random URL |
| `hostname` / `host` | Hostname |
| `port` | Common or random port number |

### Web / Logs

| type | description |
|------|-------------|
| `httpMethod` | GET, POST, PUT, DELETE… |
| `httpStatus` | HTTP status code (200-weighted) |
| `logLevel` | DEBUG, INFO, WARN, ERROR… |
| `userAgent` | Browser/tool user-agent string |
| `mimeType` | MIME content type |
| `bytes` | Byte count | `range: min,max` |
| `duration` / `duration_ms` | Duration in ms | `range: min,max` |

### Date / Time

| type | description | options |
|------|-------------|---------|
| `timestamp` | ISO-8601 UTC timestamp | `range: min_min,max_min` (minutes back from now) |
| `date` | Date string (YYYY-MM-DD) | `range: min_days,max_days` (days back) |
| `time` | Time string (HH:MM:SS) | — |

### Boolean

| type | description |
|------|-------------|
| `bool` / `boolean` | `true` or `false` |

### Structured

| type | description | options |
|------|-------------|---------|
| `enum` | Pick from a list | `values: [a, b, c]` |
| `weightedEnum` | Weighted pick | `values: [{value: x, weight: 3}, ...]` |
| `constant` / `static` | Fixed value | `value: anything` |
| `sequence` | Auto-incrementing integer | `start: N`, `step: N` |
| `object` / `nested` | Nested object | `fields: [...]` |
| `array` / `list` | Array of values | `itemType: <type>`, `count: N` |
| `os` / `operatingSystem` | OS name string | — |
| `correlationId` | `corr-<hex>` string | — |

### Dot-notation field names

Fields can use dot notation to create nested objects:

```yaml
fields:
  - name: host.ip
    type: ip
  - name: host.name
    type: hostname
```

This produces: `{"host": {"ip": "...", "name": "..."}}`

---

## Examples

### Enum with weights
```yaml
- name: severity
  type: weightedEnum
  values:
    - value: low
      weight: 60
    - value: medium
      weight: 30
    - value: high
      weight: 9
    - value: critical
      weight: 1
```

### Bulk indexing (50 docs per request)
```yaml
workloadThreads: 4
workloadSleep: 100
elasticsearchBulkQueueDepth: 50
```

### Nested object
```yaml
- name: source
  type: object
  fields:
    - name: ip
      type: ip
    - name: port
      type: port
    - name: country
      type: country
```

### Sequence counter
```yaml
- name: event_id
  type: sequence
  start: 1
  step: 1
```

---

## What's not included vs. the Java version

- **APM tracing** — the `apm_lib` / `runme_apm.bash` functionality is intentionally omitted
- **Keystore / JKS SSL** — Python uses the system CA bundle or `verifyCerts: false`; no `.jks` file needed
- **Gradle build** — replaced by `pip install -r requirements.txt`
