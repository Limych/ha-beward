# ha-beward

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE.md)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

[![Community Forum][forum-shield]][forum]

The `beward` implementation allows you to integrate your [Beward devices][beward] in Home Assistant.

![Beward Logo][exampleimg]

There is currently support for the following device types within Home Assistant:
- [Binary Sensor](#binary-sensor)
- [Camera](#camera)
- [Sensor](#sensor)

Currently only doorbells are supported by this integration.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `beward`.
4. Download _all_ the files from the `custom_components/beward/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. Choose:
   - Add `beward:` to your HA configuration.
   - In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Beward"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/beward/.translations/en.json
custom_components/beward/.translations/ru.json
custom_components/beward/__init__.py
custom_components/beward/binary_sensor.py
custom_components/beward/camera.py
custom_components/beward/config_flow.py
custom_components/beward/manifest.json
custom_components/beward/sensor.py
```

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=UAGFL5L6M8RN2&item_name=[beward]+Donation+for+a+big+barrel+of+coffee+:)&currency_code=EUR&source=url"><img alt="Buy Me a Coffe" src="https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/donate-with-paypal.png"></a></p>
<p align="center"><a href="https://www.patreon.com/join/limych?"><img alt="Support my work on Patreon" src="https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/support-with-patreon.jpg"></a></p>

## Configuration

To enable Beward device, add the following to your `configuration.yaml` file:
```yaml
# Example configuration.yaml entry
beward:
  devices:
    - host: my_doorbell_host_ip
      username: my_username
      password: my_password
```

### Configuration variables

**devices**:\
  _(list) (Required)_\
  List of configs to connect to devices.

> **host**:\
>   _(string) (Required)_\
>   The IP-address of your Beward device.
> 
> **username**:\
>   _(string) (Required)_\
>   The username for accessing your Beward device.
> 
> **password**:\
>   _(string) (Required)_\
>   The password for accessing your Beward device.
> 
> **stream**:\
>   _(number) (Optional)_\
>   Video stream from device.\
>   _Default value: 0_
> 
> **name**:\
>   _(string) (Optional)_\
>   Name to use in the frontend.\
>   _Default value: "Beward <device_id>"_

## Camera

Once you have enabled the [Beward component](#configuration), you can start using the camera platform. Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
camera:
  - platform: beward
```

### Configuration variables

**ffmpeg_arguments**:\
  _(string) (Optional)_\
  Extra options to pass to ffmpeg, e.g., image quality or video filter options.\
  _Default value: "-pred 1"_

**Note:** To be able to playback the last capture, it is required to install the `ffmpeg` component. Make sure to follow the steps mentioned at [FFMPEG documentation][ffmpeg-doc].

## Binary Sensor

Once you have enabled the [Beward component](#configuration), you can start using a binary sensor platform. Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
binary_sensor:
  - platform: beward
```

### Configuration variables

**monitored_conditions**:\
  _(list) (Optional)_\
  Conditions to display in the frontend. The following conditions can be monitored. If not specified, all conditions below will be enabled.

> **ding**:\
> Return a boolean value when the doorbell button was pressed.
> 
> **motion**:\
> Return a boolean value when a movement was detected by the camera.

## Sensor

Once you have enabled the [Beward component](#configuration), you can start using a sensor platform. Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: beward
```

### Configuration variables

**monitored_conditions**:\
  _(list) (Optional)_\
  Conditions to display in the frontend. The following conditions can be monitored. If not specified, all conditions below will be enabled.

> **last_activity**:\
> Return the timestamp from the last event captured (ding/motion/on demand) by the Beward device camera.
> 
> **last_ding**:\
> Return the timestamp from the last time the Beward doorbell button was pressed.
> 
> **last_motion**:\
> Return the timestamp from the last motion event captured by the Beward device camera.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[beward]: https://www.beward.ru/
[commits-shield]: https://img.shields.io/github/commit-activity/y/Limych/ha-beward.svg?style=popout
[commits]: https://github.com/Limych/ha-beward/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=popout
[exampleimg]: beward.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/Limych/ha-beward.svg?style=popout
[maintenance-shield]: https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout
[releases-shield]: https://img.shields.io/github/release/Limych/ha-beward.svg?style=popout
[releases]: https://github.com/Limych/ha-beward/releases
[ffmpeg-doc]: https://www.home-assistant.io/components/ffmpeg/
