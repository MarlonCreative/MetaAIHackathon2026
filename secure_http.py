"""Verified TLS, including the macOS system CA bundle for standalone Python installs."""
import ssl
from pathlib import Path

def tls_context():
    context = ssl.create_default_context()
    system_bundle = Path('/etc/ssl/cert.pem')
    if system_bundle.is_file():
        context.load_verify_locations(cafile=str(system_bundle))
    return context
