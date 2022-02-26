SECRET = 174807

class Stream:
    value = 1

    @classmethod
    def bit(cls) -> int:
        b = 0
        i = 0

        while SECRET > 2 ** i:
            b ^= (SECRET >> i) & (cls.value >> i) & 1
            i += 1
        
        cls.value = ((b << i) | cls.value) >> 1

        return b

    @classmethod
    def byte(cls) -> int:
        for _ in range(8):
            cls.bit()
        return cls.value & 255


def encrypt(plaintext: bytes) -> bytes:
    return bytes(
        byte ^ Stream.byte()
        for byte in plaintext
    )
