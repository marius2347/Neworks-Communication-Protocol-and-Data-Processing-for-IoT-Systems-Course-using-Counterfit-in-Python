# IoT Projects Portfolio — Ciobanu Marius

**Course:** Networks, Communication Protocols and Data Processing for IoT Systems
**Institution:** National University of Science and Technology POLITEHNICA Bucharest

---

## Final Project

### IoT-Based Smart Aquaculture Monitoring and Control System

**Folder:** `project-iot/` | **File:** `aquaculture_monitor.py`
**Submitted:** May 2026

#### Demo


![System Demo](project-iot/demo.gif)

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

The following labs were completed during the course lectures. Each one builds toward the final project concepts.

---

### Lab 1 — Temperature Sensor
**Folders:** `temperature-sensor/` · `temperature-sensor-server/`

Reads temperature and humidity from a virtual DHT11 sensor via CounterFit and publishes telemetry every 10 minutes to an MQTT broker. The server side subscribes, stores readings into a CSV file with timestamps, and includes a Growing Degree Days (GDD) calculator for plant growth monitoring.

| Setup | CounterFit sensor config | Output CSV |
|-------|--------------------------|------------|
| ![Lab 1 image 1](temperature-sensor/L1/1.jpg) | ![Lab 1 image 2](temperature-sensor/L1/2.jpg) | ![Lab 1 image 3](temperature-sensor/L1/3.jpg) |

---

### Lab 2 — Nightlight (MQTT Pub/Sub)
**Folders:** `nightlight/` · `nightlight-server/`

A Grove light sensor reads ambient brightness and publishes it to a public MQTT broker (`test.mosquitto.org`). The server subscribes to the telemetry topic: if light drops below 300, it sends a command to turn an LED on; otherwise it turns it off. Demonstrates the full MQTT publish/subscribe loop between a simulated IoT device and a remote server.

**Lab 3 — Basic sensor + LED wiring:**

| CounterFit setup | Sensor reading in terminal |
|------------------|---------------------------|
| ![L3 image 1](nightlight/L3/1.jpg) | ![L3 image 2](nightlight/L3/2.jpg) |

![L3 overall view](nightlight/L3/image3.jpg)

**Lab 4 — Full MQTT client/server loop:**

| MQTT publish | Command received | LED on | LED off |
|--------------|-----------------|--------|---------|
| ![L4 image 1](nightlight/L4/1.jpg) | ![L4 image 2](nightlight/L4/2.jpg) | ![L4 image 3](nightlight/L4/3.jpg) | ![L4 image 4](nightlight/L4/4.jpg) |

---

### Lab 3 — Soil Moisture Sensor
**Folders:** `soil-moisture-sensor/` · `soil-moisture-sensor-server/` · `soil-moisture-trigger/`

An ADC reads soil moisture values via CounterFit. The device connects to **Azure IoT Hub** using X.509 certificate authentication and sends telemetry every 10 seconds. Direct method calls (`relay_on` / `relay_off`) control a virtual relay. The MQTT server automates watering: if moisture exceeds 450, the relay activates for 5 seconds, waits 20 seconds, then resumes monitoring. An Azure Function (Event Hub trigger) also invokes direct methods from the cloud.

**Lab 6 — Azure IoT Hub connection:**

![L6](soil-moisture-sensor/L6/1.jpg)

**Lab 7 — Sending telemetry + relay control:**

| Sending message | Relay ON | Relay OFF |
|-----------------|----------|-----------|
| ![L7 image 1](soil-moisture-sensor/L7/1.jpg) | ![L7 image 2](soil-moisture-sensor/L7/2.jpg) | ![L7 image 3](soil-moisture-sensor/L7/3.jpg) |

**Lab 8 — X.509 certificate authentication:**

![L8](soil-moisture-sensor/L8/1.jpg)

**Lab 9 — Azure Function trigger:**

| Function trigger firing | Cloud direct method invoked |
|-------------------------|-----------------------------|
| ![L9 image 1](soil-moisture-trigger/L9/1.jpg) | ![L9 image 2](soil-moisture-trigger/L9/2.jpg) |

**Lab 10 — End-to-end automated watering:**

![L10](soil-moisture-sensor/L10/1.jpg)

---

### Lab 4 — GPS Sensor
**Folders:** `gps-sensor/` · `gps-trigger/`

Reads NMEA sentences from a virtual serial port via CounterFit. GGA sentences are parsed with `pynmea2` to extract latitude and longitude, which are sent as JSON telemetry to **Azure IoT Hub** every 60 seconds. An Azure Function stores each GPS event as a timestamped JSON blob in **Azure Blob Storage**, organized by device ID.

**Lab 11 — GPS parsing + IoT Hub:**

| GPS telemetry sent | IoT Hub message received |
|--------------------|--------------------------|
| ![L11 image 1](gps-sensor/L11/1.jpg) | ![L11 image 2](gps-sensor/L11/2.jpg) |

**Lab 12 — Azure Function + Blob Storage:**

| Function trigger | Blob stored |
|------------------|-------------|
| ![L12 image 1](gps-sensor/L12/1.jpg) | ![L12 image 2](gps-sensor/L12/2.jpg) |

---

### Lab 5 — Smart Timer (Speech Recognition)
**Folder:** `smart-timer/`

Uses the **Azure Cognitive Services Speech SDK** to perform continuous speech recognition in English (GB), Sweden Central region. Recognized speech is printed to the console in real time using an event-driven callback model.

![Smart Timer](smart-timer/1.jpg)

---

### Lab 6 — Fruit Quality Detector
**Folder:** `fruit-quality-detector/`

Captures a JPEG image from a virtual Pi camera via CounterFit and sends it to an **Azure Custom Vision** image classification endpoint. The model returns confidence percentages for `ripe` vs `unripe` labels. Also includes a VL53L0X time-of-flight distance sensor to measure how far a fruit is from the camera before triggering the capture.

The `Lab15images/` folder contains the full training and testing dataset — 25 ripe and 29 unripe banana images used to train the Custom Vision model.

**Training dataset samples:**

| Ripe | Unripe |
|------|--------|
| ![Ripe banana](fruit-quality-detector/Lab15images/images/training/ripe/banana-ripe-1.png) | ![Unripe banana](fruit-quality-detector/Lab15images/images/training/unripe/banana-unripe-1.png) |

**Testing dataset samples:**

| Ripe test | Unripe test |
|-----------|-------------|
| ![Ripe test 1](fruit-quality-detector/Lab15images/images/testing/ripe/banana-ripe-1.png) | ![Unripe test 1](fruit-quality-detector/Lab15images/images/testing/unripe/banana-unripe-1.png) |

**Captured inference image:**

![Captured image for prediction](fruit-quality-detector/image.jpg)

**Lab 16 — Custom Vision model training:**

![Lab 16](fruit-quality-detector/Lab16/1.jpg)

**Lab 17 — Running predictions:**

![Lab 17](fruit-quality-detector/Lab17/1.jpg)

**Lab 18 — Edge deployment (Docker / TFLite):**

![Lab 18](fruit-quality-detector/Lab18/1.jpg)

---

### Lab 7 — Stock Counter
**Folder:** `stock-counter/`

Captures an image with a virtual Pi camera and sends it to an **Azure Custom Vision** object detection model. Predictions above 30% confidence are displayed and annotated on the image using PIL bounding boxes. Uses IoU (intersection-over-union) overlap filtering via `shapely` to remove duplicate detections.

| Detection result | Annotated bounding boxes |
|-----------------|--------------------------|
| ![Stock counter 1](stock-counter/1.jpg) | ![Stock counter 2](stock-counter/2.jpg) |

**Captured inference image:**

![Stock counter captured image](stock-counter/image.jpg)

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
