with open("flag.txt") as flag_file:
    flag = flag_file.read()

modulo = 256
public_key = 17

flag_encrypted = []
for c in flag:
    char_code = ord(c) * 2 - 1
    encrypted_char_code = pow(char_code, public_key, modulo)
    flag_encrypted.append(encrypted_char_code)

with open("rsa.enc", "wb") as encrypted_file:
    encrypted_file.write(bytes(flag_encrypted))
