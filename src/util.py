from Crypto.Hash import SHA256
import random

def sha256_hash(data):
    sha256 = SHA256.new()

    # Update the hash object with the input data
    sha256.update(data.encode('utf-8'))

    # Get the hexadecimal representation of the digest
    hash_hex = sha256.hexdigest()

    return hash_hex

def sha256_hash_bytes(data):
    sha256 = SHA256.new()

    # Update the hash object with the input data
    # sha256.update(data.encode('utf-8'))

    # Get the hexadecimal representation of the digest
    hash_hex = sha256.hexdigest()

    return hash_hex



def hash_array_of_bytes(array_of_strings: list[bytes]) -> list[str]:
  array_of_hashes = []
  for string in array_of_strings:
    array_of_hashes.append(sha256_hash_bytes(string))
  return array_of_hashes


def flip_1_random_bit(ciphertext:str) -> bytes:
    #flip a random bit in the cypher text
    encoded_ciphertext = ciphertext.encode()
    modified_ciphertext = bytearray(encoded_ciphertext)
    byte_to_flip = random.randint(0, len(modified_ciphertext) - 1)
    bit_to_flip = 1 << random.randint(0, 7)  # Select a random bit within the byte
    modified_ciphertext[byte_to_flip] ^= bit_to_flip  # Flip the selected bit
    return bytes(modified_ciphertext)

def n_close_ham(text:str, n:int) -> list[bytes]:
  array_of_hashes = []
  for i in range(n):
    array_of_hashes.append(flip_1_random_bit(text))
  return array_of_hashes

def find_number_of_bytes_different(bytes1: bytes, bytes2: bytes) -> int:
    # Check that the byte strings are the same length
    if len(bytes1) != len(bytes2):
        raise ValueError("Byte strings must be the same length")

    # Count the number of bytes that are different
    num_different_bytes = sum(b1 != b2 for b1, b2 in zip(bytes1, bytes2))

    return num_different_bytes
 
original = "Hello, World!"
close_hammed = n_close_ham(original, 10)

print(f"Original: {original}")
print(f"Close Hammed: {close_hammed}")
hashed_hams = hash_array_of_bytes(close_hammed)
print(f"Hashed Hammed: {hashed_hams}")
num_bytes_different = [find_number_of_bytes_different(sha256_hash_bytes(original).encode(), hash) for hash in hashed_hams] 
print (f"Number of bits different: {num_bytes_different}")


# # Example usage
# data_to_hash = "Hello, World!"

# hashed_result = sha256_hash(data_to_hash)

# print(f"Original Data: {data_to_hash}")
# print(f"SHA-256 Hash: {hashed_result}")


