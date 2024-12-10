{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python and packages
    python3
    python3Packages.requests
    python3Packages.folium
    
    # Network utilities
    traceroute
    inetutils    # Additional networking tools like ping
  ];

  shellHook = ''
    # Print Python version on shell entry
    python --version
    echo "Development environment ready with traceroute and Python packages"
  '';
}
