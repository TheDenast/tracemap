import subprocess
import platform
import re
from datetime import datetime
import requests
import time
from typing import Dict, List, Union
import argparse
import sys
import folium
from folium import plugins
import webbrowser
import os


def get_ip_location(ip: str) -> Dict[str, str]:
    """
    Get geolocation data for an IP address using ip-api.com
    Includes rate limiting to comply with free tier restrictions
    """
    try:
        # Rate limit: max 45 requests per minute
        time.sleep(1.5)
        response = requests.get(f'http://ip-api.com/json/{ip}')
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {
                    'country': data.get('country', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'lat': data.get('lat', 0),
                    'lon': data.get('lon', 0),
                    'isp': data.get('isp', 'Unknown')
                }
    except Exception as e:
        print(f"Error getting location for IP {ip}: {str(e)}")

    return {
        'country': 'Unknown',
        'city': 'Unknown',
        'region': 'Unknown',
        'lat': 0,
        'lon': 0,
        'isp': 'Unknown'
    }


def trace_route(destination: str) -> Union[List[Dict], str]:
    """
    Performs a traceroute to the specified destination 
    and returns parsed results with geolocation
    """
    # Determine the correct command based on OS
    if platform.system().lower() == "windows":
        command = ["tracert", destination]
    else:
        command = ["traceroute", "-n", destination]

    try:
        # Run the traceroute command
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            return f"Error: {result.stderr}"

        # Parse the output
        hops = []
        for line in result.stdout.split('\n'):
            # Skip empty lines and headers
            if not line or "trace" in line.lower() or "*" * 3 in line:
                continue

            # Extract IP addresses from the line
            ips = re.findall(r'(?:\d{1,3}\.){3}\d{1,3}', line)
            if ips:
                hop_num = len(hops) + 1
                ip = ips[0]
                location = get_ip_location(ip)

                hops.append({
                    'hop': hop_num,
                    'ip': ip,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'location': location
                })

        return hops

    except Exception as e:
        return f"Error: {str(e)}"


def create_trace_map(hops: List[Dict]) -> None:
    """
    Creates an interactive HTML map showing the traceroute path
    """
    # Filter out hops with invalid coordinates (0,0)
    valid_hops = [hop for hop in hops if hop['location']
                  ['lat'] != 0 and hop['location']['lon'] != 0]

    if not valid_hops:
        print("No valid geographical coordinates found in the trace")
        return

    # Create a map centered on the first valid hop
    first_hop = valid_hops[0]
    m = folium.Map(
        location=[first_hop['location']['lat'], first_hop['location']['lon']],
        zoom_start=4
    )

    # Add markers and path
    coordinates = []
    for hop in valid_hops:
        lat = hop['location']['lat']
        lon = hop['location']['lon']
        coordinates.append([lat, lon])

        # Create popup content
        popup_content = f"""
            <b>Hop {hop['hop']}</b><br>
            IP: {hop['ip']}<br>
            Location: {hop['location']['city']}, {hop['location']['region']}, {hop['location']['country']}<br>
            ISP: {hop['location']['isp']}
        """

        # Add marker
        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            popup=popup_content,
            color='red',
            fill=True,
            fill_color='red'
        ).add_to(m)

    # Add path lines
    folium.PolyLine(
        coordinates,
        weight=2,
        color='blue',
        opacity=0.8
    ).add_to(m)

    # Add a marker cluster for better visualization when points overlap
    plugins.MarkerCluster().add_to(m)

    # Save map
    output_path = os.path.join(os.getcwd(), 'trace_map.html')
    m.save(output_path)

    # Open in browser
    webbrowser.open('file://' + output_path)


def print_trace(hops: Union[List[Dict], str]) -> None:
    """
    Pretty prints the traceroute results with geolocation information
    """
    if isinstance(hops, str) and hops.startswith("Error"):
        print(hops)
        return

    print("\nTraceroute Results:")
    print("==================")
    for hop in hops:
        location = hop['location']
        print(f"Hop {hop['hop']:2d}: {hop['ip']}")
        print(f"      Location: {location['city']}, {
              location['region']}, {location['country']}")
        print(f"      ISP: {location['isp']}")
        print(f"      Coordinates: {location['lat']}, {location['lon']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Trace route to a destination with geolocation')
    parser.add_argument('destination', help='Destination IP or domain')
    parser.add_argument('--no-map', action='store_true',
                        help='Disable map visualization')
    parser.add_argument('--output', '-o', help='Save results to a file')

    args = parser.parse_args()

    results = trace_route(args.destination)

    if isinstance(results, str):  # Error case
        print(results)
        sys.exit(1)

    print_trace(results)

    if not args.no_map:
        create_trace_map(results)

    if args.output:
        with open(args.output, 'w') as f:
            for hop in results:
                f.write(f"Hop {hop['hop']}: {hop['ip']}\n")
                f.write(f"Location: {hop['location']['city']}, {
                        hop['location']['region']}, {hop['location']['country']}\n")
                f.write(f"ISP: {hop['location']['isp']}\n")
                f.write(f"Coordinates: {hop['location']['lat']}, {
                        hop['location']['lon']}\n\n")


if __name__ == '__main__':
    main()
