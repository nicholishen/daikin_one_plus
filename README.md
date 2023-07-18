# Daikin One Plus Home Assistant Integration

This integration allows you to control your Daikin One Plus Thermostat via Home Assistant. 
You can adjust the temperature, change the HVAC mode, alter the fan mode, and set the scheduling mode.

## Installation

1. Copy the contents of `daikin_one_plus/` to `<your_config_dir>/custom_components/daikin_one_plus/`.
2. Restart Home Assistant to pick up the new integration.

## Configuration

Configuration is done through the Home Assistant UI.

Navigate to `Integrations` in the configuration menu and press on `ADD INTEGRATION`. Find `Daikin One Plus Thermostat` in the list and press on it. You will now be asked to enter your email, API key, and integrator token. If you want to control a specific location, you can provide the name of the location; otherwise, the first location will be used.

### How to Obtain API Key and Integrator Token

To obtain the API key and integrator token an owner and a developer are required. The owner is the entity who will be utilizing the integration to control the system. The developer is the entity who will be performing the integration with the Open API. For development purposes, these may be the same entity.

1. **Owner Responsibilities:**
  - The owner should download the Daikin One Home App or Amana Home App and create an account. Then they will need to follow app instructions to add thermostats.
  - The owner needs to request the Integrator Token by navigating to “cloud services” -> “home integration” -> “get integration token”. After agreeing to the Integration Token Terms, they will be asked to enter their password to finalize the request.

2. **Developer Responsibilities:**
  - The developer needs an API Key to begin development. Upon downloading the homeowner app and creating an account, the developer should enable the developer menu. 
    - For iOS: Go to the Settings app -> Navigate to the Daikin One Home or Amana Home App and turn on the developer menu option.
    - For Android: Within the Home App, navigate to "cloud services" -> "home integration" and click on the page description 5 times to enable the developer menu.

  - Once enabled, navigate to "cloud services" -> "home integration" -> "developer". Agree to the Daikin B2B Terms and Daikin One Open API License Terms, enter the name of the application to be integrated with the Daikin One Open API, and follow the instructions on the screen to submit the request.

## Services

The following services are made available:

- `daikin_one_plus.set_hvac_mode`
- `daikin_one_plus.set_temperature`
- `daikin_one_plus.set_fan_mode`
- `daikin_one_plus.set_schedule`

## Troubleshooting

If you encounter issues with the integration, check the Home Assistant logs for errors. First, check if your Daikin One Plus Thermostat is accessible and functioning as expected through the Daikin One Home App.

Please report bugs on the [github repo](https://github.com/nicholishen/daikin_oneplus/issues).

## Disclaimer

This project is not affiliated with or endorsed by Daikin. Use at your own risk.

## Links

- Daikin Open API specs: https://www.daikinone.com/openapi/documentation/index.html
- GitHub: https://github.com/nicholishen/daikin_oneplus

## License

Daikin One Plus Home Assistant Integration is released under the MIT License.