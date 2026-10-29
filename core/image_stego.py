"""
Image LSB steganography for Subliminal Weaver.
Embeds and extracts text (or encrypted payloads) in PNG/BMP images.
"""

from PIL import Image
import numpy as np
from typing import Optional


def _text_to_bits(text: str) -> str:
    encoded = text.encode("utf-8")
    length = len(encoded)
    bits = f"{length:032b}"
    for byte in encoded:
        bits += f"{byte:08b}"
    return bits


def _bits_to_text(bits: str) -> str:
    if len(bits) < 32:
        raise ValueError("Not enough bits for length prefix")
    length = int(bits[:32], 2)
    data_bits = bits[32:32 + length * 8]
    if len(data_bits) < length * 8:
        raise ValueError("Incomplete data")
    bytes_data = bytearray()
    for i in range(0, len(data_bits), 8):
        byte = int(data_bits[i:i+8], 2)
        bytes_data.append(byte)
    return bytes_data.decode("utf-8")


def embed_message(image_path: str, message: str, output_path: str, password: Optional[str] = None) -> None:
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    flat = arr.flatten()

    if password:
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
            import os
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            f = Fernet(key)
            encrypted = f.encrypt(message.encode("utf-8"))
            payload = base64.urlsafe_b64encode(salt + encrypted).decode("ascii")
            message = f"ENC:{payload}"
        except ImportError:
            raise RuntimeError("cryptography package required for password support. pip install cryptography")

    bits = _text_to_bits(message)
    if len(bits) > len(flat):
        raise ValueError(f"Message too long for image. Need {len(bits)} bits, have {len(flat)}")

    for i, bit in enumerate(bits):
        flat[i] = (flat[i] & ~1) | int(bit)

    new_arr = flat.reshape(arr.shape)
    Image.fromarray(new_arr.astype(np.uint8)).save(output_path, "PNG")
    print(f"Embedded successfully → {output_path}")


def extract_message(image_path: str, password: Optional[str] = None) -> str:
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    flat = arr.flatten()

    max_bits = min(len(flat), 1000000)
    bits = "".join(str(pixel & 1) for pixel in flat[:max_bits])

    try:
        message = _bits_to_text(bits)
    except Exception as e:
        raise ValueError(f"Failed to extract: {e}")

    if message.startswith("ENC:"):
        if not password:
            raise ValueError("Message is encrypted. Provide password.")
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
            payload = base64.urlsafe_b64decode(message[4:])
            salt = payload[:16]
            encrypted = payload[16:]
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            f = Fernet(key)
            return f.decrypt(encrypted).decode("utf-8")
        except ImportError:
            raise RuntimeError("cryptography package required")
        except Exception:
            raise ValueError("Decryption failed. Wrong password?")

    return message


def capacity(image_path: str) -> int:
    img = Image.open(image_path).convert("RGB")
    return (img.width * img.height * 3) // 8 - 4
