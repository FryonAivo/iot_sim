### IoT simulation for the TU-Sofia course "Network Security in IoT- and Edge-based networks"

This project is made after the curriculum of the course and is designed to demonstrate the operation of virtual sensor devices and their operation inside a network with limited access, data processing and policy enforcement through Node-RED, attack detection via Suricata IDS and a Node-RED rule-based IDS, and security monitoring through Prometheus and Grafana.

The project is split across 5 stages, each adding a new layer of security on top of the previous one.

---

### Stages

**Stage 1 — EDGE platform and pipeline**
Basic IoT communication pipeline. Python sensor publishes telemetry to Mosquitto, Node-RED validates the payload and generates temperature alerts.

**Stage 2 — Connectivity and segmentation**
Network segmentation via Docker networks (`iot_net` for IoT devices, `edge_net` for edge services). Mosquitto authentication with username/password and ACL-based topic access control.

**Stage 3 — Attack detection**
Python attacker scripts for MQTT flood and brute force authentication attacks. Suricata IDS monitors the Docker network interface for flood and brute force patterns. Node-RED rate-based IDS detects floods at the application level.

**Stage 4 — Policy management**
Node-RED enforces a device policy (defined in `nodered_conf/policy.json`) — unknown devices are dropped, topic violations and rate limit breaches generate alerts on `alerts/#`.

**Stage 5 — Security monitoring**
Prometheus scrapes metrics from a Node-RED `/metrics` endpoint. Grafana visualises message rate, total alerts and blocked messages with threshold-based colour coding.

---

### Stack

| Component | Role |
|---|---|
| Docker + Docker Compose | Containerisation of all components |
| Mosquitto (MQTT broker) | IoT transport layer — pub/sub with auth and ACL |
| Node-RED | Edge logic — validation, IDS, policy enforcement, metrics |
| Python | Sensor simulator + attacker scripts |
| Suricata | Network-level IDS (Linux only) |
| Prometheus | Metrics collection |
| Grafana | Security dashboard and alerting |

---

### Running the simulation

Requires Docker and Docker Compose.

```bash
docker compose up -d
```

| Service | URL |
|---|---|
| Node-RED | http://localhost:1880 |
| Grafana | http://localhost:3000 (admin / admin) |
| Prometheus | http://localhost:9090 |
| MQTT broker | localhost:1883 |

---

### Running the attacker

**Flood attack:**
```bash
docker compose run --rm attacker python attacker.py mosquitto flood \
  --username sensor --password sensor \
  --device-id sensor_01 \
  --rate 100 --duration 30
```

**Brute force (wordlist):**
```bash
docker compose run --rm -v /path/to/wordlist.txt:/wordlist.txt \
  attacker python attacker.py mosquitto brute-wordlist --wordlist /wordlist.txt
```

**Brute force (charset):**
```bash
docker compose run --rm attacker python attacker.py mosquitto brute-charset \
  --username sensor --max-len 4
```

To monitor alerts while attacking:
```bash
docker compose exec mosquitto sh -c 'mosquitto_sub -u nodered -P nodered -t alerts/# -v'
```
