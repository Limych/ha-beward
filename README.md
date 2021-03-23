*Please :star: this repo if you find it useful*

# ha-beward

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

[![Community Forum][forum-shield]][forum]

_This implementation allows you to integrate your [Beward surveillance devices][beward] to Home Assistant._

![Beward Logo][exampleimg]

There is currently support for the following device types within Home Assistant:
- [Binary Sensor](#binary-sensor)
- [Camera](#camera)
- [Sensor](#sensor)

Currently only doorbells are supported by this integration.

I also suggest you [visit the support topic][forum] on the community forum.

## Installation

### Install from HACS (recommended)

1. Have [HACS][hacs] installed, this will allow you to easily manage and track updates.
1. Search for "Beward".
1. Click Install below the found integration.
1. _If you want to configure component via Home Assistant UI..._\
    in the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Beward".
1. _If you want to configure component via `configuration.yaml`..._\
    follow instructions below, then restart Home Assistant.

### Manual installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `beward`.
1. Download file `beward.zip` from the [latest release section][releases-latest] in this repository.
1. Extract _all_ files from this archive you downloaded in the directory (folder) you created.
1. Restart Home Assistant
1. _If you want to configure component via Home Assistant UI..._\
    in the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Beward".
1. _If you want to configure component via `configuration.yaml`..._\
    follow instructions below, then restart Home Assistant.

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/a/mjz640g" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

## Configuration

To integrate Beward device, add the following to your `configuration.yaml` file:
```yaml
# Example configuration.yaml entry
beward:
  - host: HOST_ADDRESS_CAMERA
    username: YOUR_USERNAME
    password: YOUR_PASSWORD
```

### Configuration variables

**host**:\
  _(string) (Required)_\
  The IP address or hostname of your Beward device. If using a hostname, make sure the DNS works as expected.

**username**:\
  _(string) (Required)_\
  The username for accessing your Beward device.

**password**:\
  _(string) (Required)_\
  The password for accessing your Beward device.

**name**:\
  _(string) (Optional) (Default value: "Beward <device_id>")_\
  This parameter allows you to override the name of your Beward device in the frontend.

**port**:\
  _(integer) (Optional) (Default value: 80)_\
  The port that the Beward device is running on.

**rtsp_port**:\
  _(integer) (Optional) (Default value: Autodetect from the device)_\
  The RTSP port that the Beward camera is running on.

**stream**:\
  _(integer) (Optional) (Default value: 0)_\
  Number of video stream from Beward device.

**ffmpeg_arguments**:\
  _(string) (Optional) (Default value: "-pred 1")_\
  Extra options to pass to ffmpeg, e.g., image quality or video filter options.

**Note:** To be able to playback the live stream, it is required to install the `ffmpeg` component. Make sure to follow the steps mentioned at [FFMPEG documentation][ffmpeg-doc].

**cameras**:\
  _(list) (Optional) (Default value: all cameras below)_\
  Camera types to display in the frontend. The following cameras can be added:

> **live**:\
> Live view camera.
>
> **last_motion**:\
> Camera which store photo of last motion.
>
> **last_ding**:\
> Camera which store photo of last visitor.

**binary_sensors**:\
  _(list) (Optional) (Default value: None)_\
  Conditions to display in the frontend. The following conditions can be monitored:

> **online**:\
> Return `on` when camera is available (i.e., responding to commands), `off` when not.
>
> **motion**:\
> Return `on` when a motion is detected, `off` when not.
>
> **ding**:\
> Return `on` when a doorbell button is pressed, `off` when not.

**sensors**:\
  _(list) (Optional) (Default value: None)_\
  Conditions to display in the frontend. The following conditions can be monitored:

> **last_activity**:\
> Return the timestamp from the last event captured (ding/motion/on demand) by the Beward device camera.
>
> **last_motion**:\
> Return the timestamp from the last motion event captured by the Beward device camera.
>
> **last_ding**:\
> Return the timestamp from the last time the Beward doorbell button was pressed.

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/a/mjz640g" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

## Advanced Configuration

You can also use this more advanced configuration example:

```yaml
# Example configuration.yaml entry
beward:
  - host: HOST_ADDRESS_CAMERA_1
    username: YOUR_USERNAME
    password: YOUR_PASSWORD
    binary_sensors:
      - motion
      - online
    sensors:
      - last_ding

  # Add second camera
  - host: HOST_ADDRESS_CAMERA_2
    username: YOUR_USERNAME
    password: YOUR_PASSWORD
    name: "Back door"
    rtsp_port: 1554
    camera:
      - last_motion
```

## Usage tips

### Send history image via Telegram

You can use photos of the last motion and the last ding outside this integration.
For example, send it via Telegram.

History images are stored in `/config/.storage/beward/`.
For example, for a camera named "Front door" there will be files `front_door_last_motion.jpg` and `front_door_last_ding.jpg`.

Automation example (see the [Telegram documentation][telegram-photo] for more details how to send images):
```yaml
# Example configuration.yaml entry
homeassistant:
  whitelist_external_dirs:
    - /config/.storage/beward  # Required for Home Assistant version 0.48+

automation:
  - alias: "Front door Ding"
    trigger:
      platform: state
      entity_id: binary_sensor.front_door_ding
      to: 'on'
    action:
      - service: notify.NOTIFIER_NAME
        data:
          message: "The doorbell is ringing!"
          data:
            photo:
              file: /config/.storage/beward/front_door_last_ding.jpg
              caption: "The doorbell is ringing!"
```

[telegram-photo]: https://www.home-assistant.io/components/telegram/#photo-support

## Track updates

You can automatically track new versions of this component and update it by [HACS][hacs].

## Troubleshooting

To enable debug logs use this configuration:
```yaml
# Example configuration.yaml entry
logger:
  default: info
  logs:
    custom_components.beward: debug
```
... then restart HA.

## Contributions are welcome!

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We have set up a separate document containing our [contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this component is by [Andrey "Limych" Khrolenok](https://github.com/Limych).

For a full list of all authors and contributors, check [the contributor's page][contributors].

## License

MIT License

Copyright (c) 2019-2021 Andrey "Limych" Khrolenok

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

***

[component]: https://github.com/Limych/ha-beward
[commits-shield]: https://img.shields.io/github/commit-activity/y/Limych/ha-beward.svg?style=popout
[commits]: https://github.com/Limych/ha-beward/commits/master
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg?style=popout
[hacs]: https://hacs.xyz
[exampleimg]: https://github.com/Limych/ha-beward/raw/master/beward.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/t/beward-cameras-and-doorbells-integration/129388
[license]: https://github.com/Limych/ha-beward/blob/main/LICENSE.md
[license-shield]: https://img.shields.io/badge/license-Creative_Commons_BY--NC--SA_License-lightgray.svg?style=popout
[maintenance-shield]: https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout
[releases-shield]: https://img.shields.io/github/release/Limych/ha-beward.svg?style=popout
[releases]: https://github.com/Limych/ha-beward/releases
[releases-latest]: https://github.com/Limych/ha-beward/releases/latest
[user_profile]: https://github.com/Limych
[report_bug]: https://github.com/Limych/ha-beward/issues/new?template=bug_report.md
[suggest_idea]: https://github.com/Limych/ha-beward/issues/new?template=feature_request.md
[contributors]: https://github.com/Limych/ha-beward/graphs/contributors
[beward]: https://www.beward.ru/
[ffmpeg-doc]: https://www.home-assistant.io/components/ffmpeg/
