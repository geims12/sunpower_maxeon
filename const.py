"""Constants for the SunPower Maxeon integration."""
from typing import Optional, Final
DOMAIN = "sunpower_maxeon"

OAUTH2_AUTHORIZE = "https://api.sunpowerglobal.com/v1/authorize"
OAUTH2_TOKEN = "https://api.sunpowerglobal.com/v1/token"

SYSTEMS = {
    "systems": [
        {
            "system_sn": "default",
            "active_at": 1718612017,
            "installed_pv_power": 7.2,
            "inverter_model": "RESERVE-INV-1-P5-L1-INT",
            "inverter_rated_power": 5,
            "battery_model": "RESERVE-BAT-1-DC-10.1-INT",
            "battery_capacity": 10.08,
            "battery_usable_capacity": 9.752,
            "meter_type": "CT",
            "feedin_threshold": 90,
            "inv_version": "01000.165",
            "ems_version": "V0.11.04",
            "bms_version": "V1.53",
            "status": "dummy_data"
        }
    ]
}

SYSTEM_DETAILS = {
    "default": {
        "system_sn": "default",
        "active_at": 1718612017,
        "installed_pv_power": 7.2,
        "inverter_model": "RESERVE-INV-1-P5-L1-INT",
        "inverter_rated_power": 5,
        "battery_model": "RESERVE-BAT-1-DC-10.1-INT",
        "battery_capacity": 10.08,
        "battery_usable_capacity": 9.752,
        "meter_type": "CT",
        "feedin_threshold": 90,
        "inv_version": "01000.165",
        "ems_version": "V0.11.04",
        "bms_version": "V1.53",
        "status": "dummy_data"
    }
}

ENERGY_METER = {
  "system_sn": "default",
  "timestamp": 1680334973,
  "e_pv_generation": None,
  "e_storage_charge": None,
  "e_storage_discharge": None,
  "e_grid_import": None,
  "e_grid_export": None,
  "e_consumption": None,
  "status": "dummy_data",
  "p_max_charge": None,
  "p_max_discharge": None
}

POWER_METER = {
  "system_sn": "default",
  "timestamp": 1680334973,
  "p_pv": None,
  "p_grid": None,
  "p_storage": None,
  "soc": None,
  "p_consumption": None,
  "status": "dummy_data"
}

CHARGING_SCHEDULE = {
    "enable": True,
    "start_time_1": "14:00",
    "end_time_1": "16:00",
    "start_time_2": "14:00",
    "end_time_2": "16:00",
    "max_soc": 95
}

DISCHARGING_SCHEDULE = {
    "enable": True,
    "start_time_1": "14:00",
    "end_time_1": "16:00",
    "start_time_2": "14:00",
    "end_time_2": "16:00",
    "min_soc": 20
}

EXPORT_LIMIT = {
  
  "export_rate": 80
}

shared_data = {
    "system_sn": None,
    "system": {},
    "details": {},
    "power": {},
    "energy": {},
    "battery_ups": {},
    "charging_schedule": {},
    "discharging_schedule": {},
    "export_limit": {},
}

ENERGY_SENSOR_KEYS: Final[list[str]] = [
    "e_pv_generation",
    "e_storage_charge",
    "e_storage_discharge",
    "e_grid_import",
    "e_grid_export",
    "e_consumption",
]