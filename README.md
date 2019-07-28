# HA-Beward

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE.md)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Home Assistant component to integrate with [Beward devices][beward]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show something `True` or `False`.
`sensor` | Show info from blueprint API.
`switch` | Switch something `True` or `False`.

![example][exampleimg]

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `blueprint`.
4. Download _all_ the files from the `custom_components/blueprint/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. Choose:
   - Add `blueprint:` to your HA configuration.
   - In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Blueprint"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/blueprint/.translations/en.json
custom_components/blueprint/.translations/nb.json
custom_components/blueprint/.translations/sensor.nb.json
custom_components/blueprint/__init__.py
custom_components/blueprint/binary_sensor.py
custom_components/blueprint/config_flow.py
custom_components/blueprint/const.py
custom_components/blueprint/manifest.json
custom_components/blueprint/sensor.py
custom_components/blueprint/switch.py
```

## Example configuration.yaml

```yaml
blueprint:
  username: my_username
  password: my_password
  binary_sensor:
    - enabled: true
      name: My custom name
  sensor:
    - enabled: true
      name: My custom name
  switch:
    - enabled: true
      name: My custom name
```

## Configuration options

Key | Type | Required | Description
-- | -- | -- | --
`username` | `string` | `False` | Username for the client.
`password` | `string` | `False` | Password for the client.
`binary_sensor` | `list` | `False` | Configuration for the `binary_sensor` platform.
`sensor` | `list` | `False` | Configuration for the `sensor` platform.
`switch` | `list` | `False` | Configuration for the `switch` platform.

### Configuration options for `binary_sensor` list

Key | Type | Required | Default | Description
-- | -- | -- | -- | --
`enabled` | `boolean` | `False` | `True` | Boolean to enable/disable the platform.
`name` | `string` | `False` | `blueprint` | Custom name for the entity.

### Configuration options for `sensor` list

Key | Type | Required | Default | Description
-- | -- | -- | -- | --
`enabled` | `boolean` | `False` | `True` | Boolean to enable/disable the platform.
`name` | `string` | `False` | `blueprint` | Custom name for the entity.


### Configuration options for `switch` list

Key | Type | Required | Default | Description
-- | -- | -- | -- | --
`enabled` | `boolean` | `False` | `True` | Boolean to enable/disable the platform.
`name` | `string` | `False` | `blueprint` | Custom name for the entity.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[beward]: https://www.beward.ru/
[buymecoffee]: https://www.buymeacoffee.com/ludeeus
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/Limych/ha-beward.svg?style=for-the-badge
[commits]: https://github.com/Limych/ha-beward/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/Limych/ha-beward.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Joakim%20Sørensen%20%40ludeeus-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/Limych/ha-beward.svg?style=for-the-badge
[releases]: https://github.com/Limych/ha-beward/releases
