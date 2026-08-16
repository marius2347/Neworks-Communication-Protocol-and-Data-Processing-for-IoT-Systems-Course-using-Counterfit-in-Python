"""
IoT-Based Smart Aquaculture Monitoring and Control System
=========================================================
Uses CounterFit virtual hardware to simulate:
  - 4 Temperature sensors  (Analog pins 0-3)
  - 3 Dissolved Oxygen sensors (Analog pins 4-6)
  - 1 Water Heater relay LED (Digital pin 7)
  - 1 Aeration Pump relay LED (Digital pin 8)

Automation, Gmail alerts with cooldown, and threaded CLI.
"""

import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# ── CounterFit imports ──────────────────────────────────────────────
from counterfit_connection import CounterFitConnection
from counterfit_shims_grove.grove_light_sensor_v1_2 import GroveLightSensor
from counterfit_shims_grove.grove_led import GroveLed

# ── Email configuration (placeholders) ──────────────────────────────
EMAIL_SENDER   = "mariusc0023@gmail.com"
EMAIL_PASSWORD = "YOUR_GMAIL_APP_PASSWORD"        # Gmail App Password (not your login password)
EMAIL_RECEIVER = "mariusc0023@gmail.com"
SMTP_SERVER    = "smtp.gmail.com"
SMTP_PORT      = 587

# ── Threshold constants ─────────────────────────────────────────────
TEMP_LOW       = 20.0   # °C – turn heater ON below this
TEMP_HIGH      = 22.0   # °C – turn heater OFF above this
O2_LOW         = 5.0    # mg/L – turn pump ON below this
O2_HIGH        = 6.0    # mg/L – turn pump OFF above this

LOOP_INTERVAL  = 5      # seconds between sensor reads
ALERT_COOLDOWN = 120    # seconds between consecutive email alerts


# ═══════════════════════════════════════════════════════════════════
#  Gmail alert helper
# ═══════════════════════════════════════════════════════════════════
def send_email_alert(subject: str, body: str) -> bool:
    """
    Send an email alert via Gmail SMTP.
    Returns True on success, False on failure.
    """
    msg = MIMEMultipart()
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"  [EMAIL] Alert sent to {EMAIL_RECEIVER}")
        return True
    except Exception as exc:
        print(f"  [EMAIL] Failed to send alert: {exc}")
        return False


# ═══════════════════════════════════════════════════════════════════
#  Aquaculture Monitor class
# ═══════════════════════════════════════════════════════════════════
class AquacultureMonitor:
    """Encapsulates all sensors, actuators, state, and control logic."""

    def __init__(self):
        # ── Sensor arrays ────────────────────────────────────────
        # 4 temperature sensors on analog pins 0-3
        self.temp_sensors = [GroveLightSensor(pin) for pin in (0, 1, 2, 3)]
        # 3 dissolved-oxygen sensors on analog pins 4-6
        self.o2_sensors   = [GroveLightSensor(pin) for pin in (4, 5, 6)]

        # ── Actuators ────────────────────────────────────────────
        self.heater_led = GroveLed(7)   # Water Heater relay
        self.pump_led   = GroveLed(8)   # Aeration Pump relay

        # ── Runtime state ────────────────────────────────────────
        self.avg_temp: float       = 0.0
        self.avg_o2: float         = 0.0
        self.heater_on: bool       = False
        self.pump_on: bool         = False
        self.alert_mode: bool      = True
        self._last_alert_time: datetime = datetime.min  # allows first alert immediately
        self._lock = threading.Lock()   # guards shared state
        self._running = threading.Event()
        self._running.set()             # starts in "running" state

    # ── Sensor reading ───────────────────────────────────────────
    def read_sensors(self):
        """Read all sensors and compute averages (thread-safe)."""
        temps = [s.light for s in self.temp_sensors]
        o2s   = [s.light for s in self.o2_sensors]

        with self._lock:
            self.avg_temp = sum(temps) / len(temps)
            self.avg_o2   = sum(o2s)   / len(o2s)

        return self.avg_temp, self.avg_o2

    # ── Actuator control ─────────────────────────────────────────
    def _control_actuators(self, avg_temp: float, avg_o2: float):
        """
        Apply hysteresis-based control:
          Heater ON  when temp < TEMP_LOW,  OFF when temp > TEMP_HIGH
          Pump   ON  when O₂   < O2_LOW,   OFF when O₂   > O2_HIGH
        """
        # --- Water heater ---
        if avg_temp < TEMP_LOW and not self.heater_on:
            self.heater_led.on()
            self.heater_on = True
            print(f"  [HEATER] ON  – avg temp {avg_temp:.1f} °C < {TEMP_LOW}")
        elif avg_temp > TEMP_HIGH and self.heater_on:
            self.heater_led.off()
            self.heater_on = False
            print(f"  [HEATER] OFF – avg temp {avg_temp:.1f} °C > {TEMP_HIGH}")

        # --- Aeration pump ---
        if avg_o2 < O2_LOW and not self.pump_on:
            self.pump_led.on()
            self.pump_on = True
            print(f"  [PUMP]   ON  – avg O₂ {avg_o2:.2f} mg/L < {O2_LOW}")
        elif avg_o2 > O2_HIGH and self.pump_on:
            self.pump_led.off()
            self.pump_on = False
            print(f"  [PUMP]   OFF – avg O₂ {avg_o2:.2f} mg/L > {O2_HIGH}")

    # ── Alert logic with cooldown ────────────────────────────────
    def _check_alerts(self, avg_temp: float, avg_o2: float):
        """Send an email alert if thresholds are crossed, respecting cooldown."""
        if not self.alert_mode:
            return

        alerts = []
        if avg_temp < TEMP_LOW:
            alerts.append(f"Low Temperature: {avg_temp:.1f} °C (threshold {TEMP_LOW})")
        if avg_o2 < O2_LOW:
            alerts.append(f"Low Dissolved Oxygen: {avg_o2:.2f} mg/L (threshold {O2_LOW})")

        if not alerts:
            return

        now = datetime.now()
        if (now - self._last_alert_time).total_seconds() < ALERT_COOLDOWN:
            remaining = ALERT_COOLDOWN - (now - self._last_alert_time).total_seconds()
            print(f"  [ALERT] Cooldown active – next alert in {remaining:.0f}s")
            return

        subject = "⚠ Aquaculture Alert"
        body = (
            f"Aquaculture Monitoring Alert – {now:%Y-%m-%d %H:%M:%S}\n\n"
            + "\n".join(f"  • {a}" for a in alerts)
            + f"\n\nHeater: {'ON' if self.heater_on else 'OFF'}"
            + f"\nPump:   {'ON' if self.pump_on else 'OFF'}"
        )
        if send_email_alert(subject, body):
            self._last_alert_time = now

    # ── Main monitoring loop (runs in its own thread) ────────────
    def monitoring_loop(self):
        """Continuously read sensors, control actuators, and check alerts."""
        print("[MONITOR] Monitoring thread started.")
        while self._running.is_set():
            avg_temp, avg_o2 = self.read_sensors()
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Avg Temp: {avg_temp:.1f} °C | Avg O₂: {avg_o2:.2f} mg/L")

            self._control_actuators(avg_temp, avg_o2)
            self._check_alerts(avg_temp, avg_o2)

            # Sleep in small increments so shutdown is responsive
            for _ in range(LOOP_INTERVAL * 10):
                if not self._running.is_set():
                    break
                time.sleep(0.1)

        print("[MONITOR] Monitoring thread stopped.")

    # ── Status snapshot (called from CLI thread) ─────────────────
    def print_status(self):
        """Print the latest readings and actuator states."""
        with self._lock:
            print(
                f"\n{'─' * 48}\n"
                f"  Avg Temperature : {self.avg_temp:.1f} °C\n"
                f"  Avg Dissolved O₂: {self.avg_o2:.2f} mg/L\n"
                f"  Water Heater    : {'ON' if self.heater_on else 'OFF'}\n"
                f"  Aeration Pump   : {'ON' if self.pump_on else 'OFF'}\n"
                f"  Alert Mode      : {'ENABLED' if self.alert_mode else 'DISABLED'}\n"
                f"{'─' * 48}"
            )

    # ── Graceful shutdown ────────────────────────────────────────
    def stop(self):
        """Signal the monitoring thread to stop and turn off actuators."""
        self._running.clear()
        # Ensure relays are off on exit
        self.heater_led.off()
        self.pump_led.off()


# ═══════════════════════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════════════════════
def main():
    # ── 1. Connect to CounterFit ─────────────────────────────────
    print("[INIT] Connecting to CounterFit at 127.0.0.1:5000 …")
    CounterFitConnection.init("127.0.0.1", 5000)
    print("[INIT] Connected.\n")

    # ── 2. Create monitor instance ───────────────────────────────
    monitor = AquacultureMonitor()

    # ── 3. Launch monitoring in a daemon thread ──────────────────
    monitor_thread = threading.Thread(
        target=monitor.monitoring_loop,
        name="MonitorThread",
        daemon=True,
    )
    monitor_thread.start()

    # ── 4. CLI loop (main thread) ────────────────────────────────
    print("Commands:  status | toggle alerts | exit\n")
    try:
        while True:
            cmd = input(">>> ").strip().lower()

            if cmd == "status":
                monitor.print_status()

            elif cmd == "toggle alerts":
                monitor.alert_mode = not monitor.alert_mode
                state = "ENABLED" if monitor.alert_mode else "DISABLED"
                print(f"  Alert mode is now {state}.")

            elif cmd == "exit":
                print("[EXIT] Shutting down …")
                monitor.stop()
                monitor_thread.join(timeout=LOOP_INTERVAL + 2)
                print("[EXIT] Goodbye.")
                break

            elif cmd:
                print("  Unknown command. Try: status | toggle alerts | exit")

    except (KeyboardInterrupt, EOFError):
        print("\n[EXIT] Interrupted – shutting down …")
        monitor.stop()
        monitor_thread.join(timeout=LOOP_INTERVAL + 2)
        print("[EXIT] Goodbye.")


if __name__ == "__main__":
    main()
