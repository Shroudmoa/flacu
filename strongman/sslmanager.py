from pathlib import Path
import socket
import ipaddress
from datetime import datetime, timedelta

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

#pip install cryptography

SSL_DIR = Path("/etc/strongman")
CERT_FILE = SSL_DIR / "server.crt"
KEY_FILE = SSL_DIR / "server.key"


def ensure_ssl():
    SSL_DIR.mkdir(parents=True, exist_ok=True)

    if CERT_FILE.exists() and KEY_FILE.exists():
        return str(CERT_FILE), str(KEY_FILE)

    hostname = socket.gethostname()

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, hostname)
    ])

    alt_names = [x509.DNSName(hostname)]

    try:
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            try:
                alt_names.append(x509.IPAddress(ipaddress.ip_address(ip)))
            except ValueError:
                pass
    except Exception:
        pass

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=3650))
        .add_extension(
            x509.SubjectAlternativeName(alt_names),
            critical=False
        )
        .sign(key, hashes.SHA256())
    )

    with open(KEY_FILE, "wb") as f:
        f.write(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption()
            )
        )

    with open(CERT_FILE, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    return str(CERT_FILE), str(KEY_FILE)
