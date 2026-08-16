# IoT Projects Portfolio — Ciobanu Marius

**Course:** Networks, Communication Protocols and Data Processing for IoT Systems
**Institution:** National University of Science and Technology POLITEHNICA Bucharest

---

## Final Project

### IoT-Based Smart Aquaculture Monitoring and Control System

**Folder:** `project-iot/` | **File:** `aquaculture_monitor.py`
**Submitted:** May 2026

#### Overview

A fully automated, edge-computing IoT system that monitors and controls water quality parameters in an aquaculture environment. Built using Python with CounterFit virtual hardware simulation, the system implements a complete feedback loop: sensor data acquisition → automated actuation → cloud alerting → interactive CLI control.

The system simulates a real-world three-tier IoT architecture:
- **Perception Layer** — 7 virtual sensors (4 temperature + 3 dissolved oxygen)
- **Edge Processing Layer** — local Python gateway with hysteresis control and data aggregation
- **Application/Cloud Layer** — Gmail SMTP alerts for remote emergency notifications

#### Hardware Simulation (CounterFit)

Since physical probes (especially dissolved oxygen sensors) are fragile and expensive, the project uses **CounterFit** — an open-source hardware simulator that exposes a local web server mimicking GPIO pins and ADCs. The Python script interacts with it exactly as it would with a physical Raspberry Pi, making the code fully portable to real hardware without any core changes.

| Pin | Type | Mapped To |
|-----|------|-----------|
| 0, 1, 2, 3 | Analog (ADC) | Water temperature sensors (°C) |
| 4, 5, 6 | Analog (ADC) | Dissolved oxygen sensors (mg/L) |
| 7 | Digital (LED) | Water heater relay |
| 8 | Digital (LED) | Aeration pump relay |

#### Sensing and Data Aggregation

- **Temperature:** 4 sensors distributed across the tank to capture spatial variation. Their readings are averaged every 5 seconds to produce a fault-tolerant thermal profile.
- **Dissolved Oxygen (DO):** 3 sensors on analog pins 4–6, scaled in software from raw ADC values to mg/L (0–10 range). Single-sensor failure is neutralized by the array average.
- Averaging across all sensor arrays eliminates transient noise and isolated hardware faults, preventing erratic actuator behavior.

#### Hysteresis Control (Anti-Chattering)

Instead of a simple on/off threshold (which would cause rapid relay switching and hardware damage), the system uses **hysteresis control** with a deadband between activation and deactivation points:

| Parameter | Activate | Deactivate | Deadband |
|-----------|----------|------------|----------|
| Temperature (heater) | < 20.0 °C | > 22.0 °C | 2.0 °C |
| Dissolved O₂ (pump) | < 5.0 mg/L | > 6.0 mg/L | 1.0 mg/L |

When a parameter enters the deadband, the relay holds its current state — it will not toggle until the opposing threshold is crossed. This protects relay contacts from rapid switching and ensures energy-efficient, stable operation.

#### Internet Alerting System

The edge gateway connects to **Google SMTP servers** (`smtp.gmail.com:587`) using TLS encryption and a Gmail App Password. When a critical threshold is breached:

1. An email alert is composed with a timestamp and the specific anomaly detected.
2. It is sent immediately to the system administrator.
3. A **120-second cooldown timer** prevents alert spam — if the condition persists, subsequent emails are suppressed until the cooldown expires.
4. An `alert_mode` boolean flag allows operators to disable all cloud alerts during maintenance without stopping local control.

#### Multithreading Architecture

To avoid blocking the monitoring loop while waiting for user input:

- The **monitoring loop** runs as a background **daemon thread** — polling sensors, evaluating hysteresis, and dispatching alerts on a strict 5-second cycle.
- The **main thread** runs an interactive **CLI**, allowing real-time commands without interfering with background monitoring.

Available CLI commands:

| Command | Action |
|---------|--------|
| `status` | Print current average temperature and dissolved oxygen |
| `toggle alerts` | Enable or disable cloud email alerts dynamically |
| `exit` | Graceful shutdown — turns off both relays before exiting |

#### Graceful Shutdown

On exit, the system sends `off()` commands to both relays (pins 7 and 8) before terminating, ensuring the physical environment is returned to a safe, unpowered state regardless of what was running.

#### Validation Results

- **Hysteresis test:** Temperature forced to 18 °C → heater activated. Raised to 21 °C (deadband) → heater stayed ON. Raised to 23 °C → heater turned OFF. ✓
- **DO test:** DO dropped to 4.0 mg/L → pump activated + alert email sent. Subsequent polls correctly suppressed further emails during cooldown. ✓
- **CLI test:** `status` command responded instantly while relays were switching in the background, with no disruption to the 5-second monitoring cycle. ✓

#### Future Work

- **Physical hardware deployment** on a Raspberry Pi with real industrial probes and relays
- **Time-series database** (InfluxDB) + **dashboard** (Grafana) for historical trend analysis
- **Machine learning** at the edge to predict hypoxic events hours before they occur

---

## Course Lab Exercises

The following folders contain lab work completed during the course lectures. Each lab builds up toward the final project concepts.

| Folder | Topic |
|--------|-------|
| `temperature-sensor/` | DHT11 sensor reading via CounterFit, MQTT telemetry publishing |
| `temperature-sensor-server/` | MQTT subscriber, CSV logging, Growing Degree Days (GDD) calculator |
| `nightlight/` | Grove light sensor + LED control via MQTT pub/sub |
| `nightlight-server/` | MQTT server that commands LED based on light threshold |
| `soil-moisture-sensor/` | Azure IoT Hub (X.509 auth), ADC soil moisture, relay direct methods |
| `soil-moisture-sensor-server/` | MQTT server with relay automation logic |
| `soil-moisture-trigger/` | Azure Function (Event Hub trigger) invoking IoT Hub direct methods |
| `gps-sensor/` | NMEA GPS parsing, lat/lon extraction, Azure IoT Hub telemetry |
| `gps-trigger/` | Azure Function storing GPS data as JSON blobs in Azure Blob Storage |
| `smart-timer/` | Azure Cognitive Services Speech SDK, continuous speech recognition |
| `fruit-quality-detector/` | Pi camera + Azure Custom Vision, VL53L0X distance sensor, Docker/TFLite edge deployment |
| `stock-counter/` | Azure Custom Vision object detection + PIL bounding box drawing |

---

## Technologies Used

- Python 3
- CounterFit (virtual IoT hardware simulation)
- Azure IoT Hub
- Azure Functions (Event Hub triggers)
- Azure Blob Storage
- Azure Cognitive Services (Speech, Custom Vision)
- MQTT (Paho client, Mosquitto broker)
- Gmail SMTP / smtplib (TLS)
- TensorFlow Lite
- Docker / Azure ML edge deployment
- threading, smtplib, pynmea2, paho-mqtt, azure-iot-device

---

## Contact

**Ciobanu Marius**
mariusc0023@gmail.com
