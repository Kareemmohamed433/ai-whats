"""
Generate VAPID keys for Web Push notifications (RFC 8292).
Produces uncompressed P-256 Public Key (Base64URL) and Private Key.
"""
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization


def generate_vapid_keypair():
    # Generate SECP256R1 (NIST P-256) private key
    private_key = ec.generate_private_key(ec.SECP256R1())

    # Get raw 32-byte private key scalar
    private_numbers = private_key.private_numbers()
    private_bytes = private_numbers.private_value.to_bytes(32, byteorder='big')
    private_key_b64 = base64.urlsafe_b64encode(private_bytes).decode('utf-8').rstrip('=')

    # Get uncompressed 65-byte public key point (0x04 + X + Y)
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    public_key_b64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')

    # Also get PEM format for pywebpush private key compatibility
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    return {
        "public_key": public_key_b64,
        "private_key": private_key_b64,
        "private_pem": private_pem
    }


if __name__ == "__main__":
    keys = generate_vapid_keypair()
    print("=" * 60)
    print("NEXORA Web Push VAPID Key Pair Generated")
    print("=" * 60)
    print(f"\nVAPID_PUBLIC_KEY={keys['public_key']}")
    print(f"\nVAPID_PRIVATE_KEY={keys['private_key']}")
    print("\nVAPID_CLAIM_EMAIL=mailto:contact@nexorasolutions.com")
    print("=" * 60)
