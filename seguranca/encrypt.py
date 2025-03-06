import base64
import time
import itertools
import string

def xor_encrypt(password):
    s1 = password
    s2 = password[::-1]
    xor_list = [chr(ord(a) ^ ord(b)) for a, b in zip(s1, s2)]
    s3 = ''.join(xor_list)
    return base64.b64encode(s3.encode()).decode()

def xor_decrypt(encoded_password, original_length):
    decoded = base64.b64decode(encoded_password).decode()
    for candidate in itertools.product(string.printable, repeat=original_length):
        candidate = ''.join(candidate)
        if xor_encrypt(candidate) == encoded_password:
            return candidate
    return None

def main():
    password = input("Digite a senha para criptografar: ")
    encrypted_password = xor_encrypt(password)
    print(f"Senha criptografada: {encrypted_password}")
    
    start_time = time.time()
    cracked_password = xor_decrypt(encrypted_password, len(password))
    end_time = time.time()
    
    if cracked_password:
        print(f"Senha quebrada: {cracked_password}")
        print(f"Tempo necessário: {end_time - start_time:.2f} segundos")
    else:
        print("Falha ao quebrar a senha.")

if __name__ == "__main__":
    main()