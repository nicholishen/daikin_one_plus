# Key for the integration domain
DOMAIN = "daikin_one_plus"

# Keys for the configuration data
CONF_EMAIL = "email"
CONF_API_KEY = "api_key"
CONF_INTEGRATOR_TOKEN = "integrator_token"
CONF_LOCATION_NAME = "location_name"

# Default name for thermostat entity
DEFAULT_NAME = "Daikin One+ Thermostat"

# HVAC Modes
HVAC_MODE_OFF_STR = "off"
HVAC_MODE_AUTO_STR = "auto"
HVAC_MODE_HEAT_STR = "heat"
HVAC_MODE_COOL_STR = "cool"

# API endpoints
API_BASE_URL = "https://integrator-api.daikinskyport.com"
API_TOKEN_URL = f"{API_BASE_URL}/v1/token"
API_DEVICES_URL = f"{API_BASE_URL}/v1/devices"
API_DEVICE_INFO_URL = f"{API_BASE_URL}/v1/devices/{{}}"
API_DEVICE_UPDATE_MODE_SETPOINT_URL = f"{API_BASE_URL}/v1/devices/{{}}/msp"
API_DEVICE_UPDATE_SCHEDULE_URL = f"{API_BASE_URL}/v1/devices/{{}}/schedule"
API_DEVICE_UPDATE_FAN_SETTINGS_URL = f"{API_BASE_URL}/v1/devices/{{}}/fan"

# The Temperatures' Settings
TEMP_FAHRENHEIT = 'fahrenheit'
TEMP_CELSIUS = 'celsius'

# Device Type
DEVICE_TYPE_THERMOSTAT = "Thermostat"

# Time Intervals in seconds
COOLDOWN_INTERVAL = 15

# Event constants
EVENT_DAIKIN_ONEPLUS_HVAC_MODE_CHANGE = "daikin_oneplus_hvac_mode_change"
EVENT_DAIKIN_ONEPLUS_FAN_MODE_CHANGE = "daikin_oneplus_fan_mode_change"
EVENT_DAIKIN_ONEPLUS_TARGET_TEMP_CHANGE = "daikin_oneplus_target_temp_change"
EVENT_DAIKIN_ONEPLUS_SCHEDULE_MODE_CHANGE = "daikin_oneplus_schedule_mode_change"