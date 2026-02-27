from node_config import *
import networking
import time
from sensing import *

# Set up networking.
networking.connect_to_network()
# networking.mqtt_initialize()
# networking.mqtt_connect()

# The previously reported temperature values.
# prev_temps = [None] * num_zones

# Timing variables.
# LOOP_INTERVAL_NS = 1000000000 / 1000
# _prev_time = time.monotonic_ns()

# TEMPERATURE_LOG_THRESHOLD = 0
# last_temps = {}


# Runs periodic node tasks.
def loop():
    sim = get_instance()

    while True:
        sim.loop()
        time.sleep(0)

        values = [
            f"t = {sim.last_t:.2f}s\t",
            f"Outside: {c_to_f(sim.outside_temp):.2f}°f",
        ]

        for zone in range(num_zones):
            values.append(f"{zone_names[zone]}: {sim.get_temperature_f(zone):.2f}°f")

        print("\t".join(values))
