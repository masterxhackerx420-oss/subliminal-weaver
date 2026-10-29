"""
Audio LSB steganography for WAV files.
"""

import wave
import numpy as np
from typing import Optional


def embed_message_audio(audio_path: str, message: str, output_path: str, password: Optional[str] = None) -> None:
    with wave.open(audio_path, "rb") as wf:
        params = wf.getparams()
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16)

    if password:
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
            import os
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            f = Fernet(key)
            encrypted = f.encrypt(message.encode("utf-8"))
            payload = base64.urlsafe_b64encode(salt + encrypted).decode("ascii")
            message = f"ENC:{payload}"
        except ImportError:
            raise RuntimeError("cryptography required for password")

    bits = _text_to_bits(message)
    if len(bits) > len(audio):
        raise ValueError("Message too long for audio file")

    audio = audio.copy()
    for i, bit in enumerate(bits):
        audio[i] = (audio[i] & ~1) | int(bit)

    with wave.open(output_path, "wb") as wf:
        wf.setparams(params)
        wf.writeframes(audio.tobytes())

    print(f"Embedded in audio → {output_path}")


def extract_message_audio(audio_path: str, password: Optional[str] = None) -> str:
    with wave.open(audio_path, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16)

    bits = "".join(str(sample & 1) for sample in audio[:1000000])
    message = _bits_to_text(bits)

    if message.startswith("ENC:"):
        if not password:
            raise ValueError("Encrypted. Provide password.")
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
            payload = base64.urlsafe_b64decode(message[4:])
            salt = payload[:16]
            encrypted = payload[16:]
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            f = Fernet(key)
            return f.decrypt(encrypted).decode("utf-8")
        except Exception:
            raise ValueError("Decryption failed")

    return message


def _text_to_bits(text: str) -> str:
    encoded = text.encode("utf-8")
    length = len(encoded)
    bits = f"{length:032b}"
    for byte in encoded:
        bits += f"{byte:08b}"
    return bits


def _bits_to_text(bits: str) -> str:
    if len(bits) < 32:
        raise ValueError("Not enough bits")
    length = int(bits[:32], 2)
    data_bits = bits[32:32 + length * 8]
    bytes_data = bytearray()
    for i in range(0, len(data_bits), 8):
        if i + 8 > len(data_bits):
            break
        byte = int(data_bits[i:i+8], 2)
        bytes_data.append(byte)
    return bytes_data.decode("utf-8")
