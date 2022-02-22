# ReoSnap

## What is it
It's a highly customizable tool that automatically saves live snapshots of Reolink security camera feeds using the Reolink APIs, and does not require an FTP server.

## Requirements
- `pip install -r requirements.txt`

- Write the Reolink camera user password in the `.env` file for each camera you want to configure.

A non-admin user account is **strongly** recommended as its password will be used in plain-text.
<br />
To create a new user, open your Reolink camera web-interface, then Settings > System > User Management > Add User.

NOTE: there seem to be issues with symbols in passwords. If an issue occurs, try changing to an alphanumeric-only password.

## Usage
```
reosnap.py [-h] [-u USERNAME] [-q QUALITY] [-r RESOLUTION | --width WIDTH | --height HEIGHT] [-H HOURS | -m MINUTES | -s SECONDS] [-i INTERVAL] [-o OUTPUT] [-v] [-l]
```

Short | Argument | Info
---|---|---
`-h` | `--help` | show this help message and exit
`-u USER` | `--username USER` | Camera username (default: snapshotuser)
`-r RES` | `--resolution RES` | [low/medium/high/max]
/ | `--width W` | Width (height will be calculated)
/ | `--height H` | Height (width will be calculated)
`-o` | `--optimize` | Optimize image
`-q QUAL` | `--quality QUAL` | Optimization quality [low/medium/high/max/0-100]
`-k` | `--keep-og` | Keep original files (if optimization is enabled)
`-H H` | `--hours H` | Delete snapshots older than H hours
`-m M` | `--minutes M` | Delete snapshots older than M minutes
`-s S` | `--seconds S` | Delete snapshots older than S seconds
`-i INT` | `--interval INT` | Snapshot interval in seconds (default=5)
`-O PATH` | `--output PATH` | Path to output directory
`-v` | `--verbose` | Enable verbosity
`-l` | `--license` | Show License

## Customization
By default, the script is set up for a two-camera system. You can add/remove `get_camN_feed()`* functions to suit your needs, using the template below:

```
async def get_camN_feed():
    '''Get camera feed'''

    cam_name = 'camN'
    cam_ip = 'http://192.168.X.Y'

    save_snapshot(cam_name, cam_ip)
```

Then add `asyncio.run(get_camN_feed())`* in the `def loop()` function.

Finally add a new variable in the `.env` file called `camN_password`*

*(where N is the progressive number of the camera)

## Contributions
Contributions are welcome, feel free to submit issues and/or pull requests.

## Disclaimer
This tool is neither affiliated with nor endorsed by Reolink in any way.

## LICENSE
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

"ReoSnap" - Save live snapshots of Reolink camera feeds.<br />
Copyright (C) 2022 Andrea Varesio <https://www.andreavaresio.com/>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a [copy of the GNU General Public License](https://github.com/andrea-varesio/ReoSnap/blob/main/LICENSE)
along with this program.  If not, see <https://www.gnu.org/licenses/>.

<div align="center">
<a href="https://github.com/andrea-varesio/ReoSnap/">
  <img src="http://hits.dwyl.com/andrea-varesio/ReoSnap.svg?style=flat-square" alt="Hit count" />
</a>
</div>
