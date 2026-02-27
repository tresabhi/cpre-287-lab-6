from node_config import num_zones, zone_k, zone_names
import time
from utils import c_to_f
from actuation import set_damper as _set_damper
from math import sin, pi

# define some values?

SIM_SPEED = 1

TEMP_RANGE = 10
TEMP_AVG = 5

# k is the volume of the room divided by the surface area exposed to the outside
# so we need to divide it by some constant to get a reasonable coefficient
# for the derivative of the temperatures respect to time
TARGET_TEMP = 25
START_TEMP = TARGET_TEMP - 20

# The Simulation(R)
_sim = None


# We only want ONE Simulation object, and we want to share it between all of the modules. We can accomplish this
# using the singleton design pattern. This function is a key part of that pattern. It returns the singleton instance.
# Call "simulation.get_instance()" to get a Simulation, instead of instantiating a Simulation directly.
def get_instance():
    global _sim
    if _sim is None:
        _sim = Simulation(num_zones)
    return _sim


# A class that simulates the physical environment for the system.
class Simulation:
    initial_time = time.monotonic()
    zone_temps = {}
    outside_temp = 0
    cooling_dampers = [0] * num_zones
    heating_dampers = [0] * num_zones

    # Initializes the simulation.
    def __init__(self, num_zones):
        # initialize additional class variables. These are probably variables that represent the state of the physical system.

        for id in range(num_zones):
            self.zone_temps[id] = START_TEMP

        self.heating = False
        self.cooling = False

    # Returns the current temperature in the zone specified by zone_id
    def get_temperature_f(self, zone_id):
        # implement
        return c_to_f(self.zone_temps[zone_id])

    # Sets the damper(s) for the zone specified by zone_id to the percentage
    # specified by percent. 0 is closed, 100 is fully open.
    def set_damper(self, type, zone_id, percent):
        # implement

        if type == "cooling":
            self.cooling_dampers[zone_id] = percent
        elif type == "heating":
            self.heating_dampers[zone_id] = percent
        else:
            raise Exception(f"Invalid damper type: {type}")

    # Update the temperatures of the zones, given that elapsed_time_ms milliseconds
    # have elapsed since this was previously called.
    last_t = 0

    def _update_temps(self, t):
        dt = t - self.last_t
        t_days = t / 60 / 60 / 24 + 0.5

        if self.last_t == t:
            return

        self.last_t = t
        self.outside_temp = TEMP_RANGE * sin(2 * pi * (t_days - 0.25)) + TEMP_AVG

        # Update all temps
        for id in range(num_zones):
            T = self.zone_temps[id]
            k = zone_k[id]

            heating_speed = 1.5
            cooling_speed = -1
            cooling_damper = self.cooling_dampers[id] / 100
            heating_damper = self.heating_dampers[id] / 100
            # units for dT/dt = (1 / s) * kelvin = kelvin / s
            dT_dt = (
                -k * (T - self.outside_temp)
                + (heating_damper * heating_speed)
                + (cooling_damper * cooling_speed)
            )
            # units for dT = kelvin / s * s = kelvin
            # yay! units work out cleanly
            dT = dT_dt * dt

            self.zone_temps[id] += dT

    def _update_dampers(self):
        for zone in range(num_zones):
            zone_temp = self.zone_temps[zone]
            cooling = min(1, max(0, zone_temp - TARGET_TEMP)) * 100
            heating = min(1, max(0, TARGET_TEMP - zone_temp)) * 100

            self.set_damper("cooling", zone, cooling)
            self.set_damper("heating", zone, heating)

    # Runs periodic simulation actions.
    def loop(self):
        # Calculate the amount of time elapsed since this last time this function was run. See CircuitPython's time module documentation
        # at http://docs.circuitpython.org/en/latest/shared-bindings/time/index.html. We recommend time.monotonic_ns(). Also note that
        # temperature_measurement_node.py has an elapsed time calculation, and you may be able to use a similar approach here.

        # pass in the actual elapsed time.
        self._update_dampers()
        self._update_temps(SIM_SPEED * (time.monotonic() - self.initial_time))


# Used for testing the simulation.
if __name__ == "__main__":
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
