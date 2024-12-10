# tracemap

A small nifty tool I quickly threw together using Claude AI to trace a visual path to a given IP/Domain

## Features

- Traces network paths to any IP or domain
- Provides geolocation data for each hop (city, country, ISP)
- Generates interactive maps showing the packet's journey
- Supports both IPv4 and IPv6

## Installation

### NixOS/Nix Users

A `shell.nix` is provided for Nix users. Simply run:

```bash
nix-shell
```

### Standard Installation

```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python tracemap.py google.com
```

Options:
```bash
python tracemap.py [destination] [options]

Options:
  --no-map          Disable map visualization
  --output/-o FILE  Save results to a file
```

## Example Output

```
Traceroute Results:
==================
Hop  1: 192.168.1.1
      Location: Boston, Massachusetts, United States
      ISP: Comcast Cable Communications
      Coordinates: 42.3601, -71.0589

Hop  2: 96.120.67.249
      Location: Boston, Massachusetts, United States
      ISP: Comcast Cable Communications
      Coordinates: 42.3601, -71.0589
...
```

An interactive HTML map is automatically generated and opened in your default browser.

## Dependencies

- Python 3.7+
- folium (map visualization)
- requests (IP geolocation)
- traceroute/tracert (system utility)

## Notes on Accuracy

The geolocation data and visualized paths are approximations:
- IP geolocation databases may not always reflect the true physical location of routers
- Some hops may be hidden or not respond to traceroute
- The actual physical cable paths often differ from the straight lines shown on the map
- Submarine cables and internet exchange points may not be visible in the trace

## Credits

- IP geolocation provided by [ip-api.com](https://ip-api.com)
- Map visualization powered by [Folium](https://python-visualization.github.io/folium/)
- Initially developed with assistance from Anthropic's Claude
