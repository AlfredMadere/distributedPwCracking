import pytest
from ..src.util import flip_1_random_bit, n_close_ham, hash_array_of_bytes, sha256_hash

def test_hash_array_of_strings():
    array_of_strings = ["Hello", "World", "!"]
    hashes = hash_array_of_bytes(array_of_strings)
    
    # Check that the function returns the correct number of hashes
    assert len(hashes) == len(array_of_strings)

    # Check that each hash is the correct SHA256 hash of the corresponding string
    for string, hash in zip(array_of_strings, hashes):
        assert hash == sha256_hash(string)

def test_flip_1_random_bit():
    ciphertext = "Hello, World!"
    modified_ciphertext = flip_1_random_bit(ciphertext)
    
    # Check that the modified ciphertext is not equal to the original ciphertext
    assert modified_ciphertext != ciphertext.encode()

    # Check that the modified ciphertext is the same length as the original ciphertext
    assert len(modified_ciphertext) == len(ciphertext)

    # Check that only one bit has been flipped
    diff = sum([bin(x ^ y).count('1') for x, y in zip(modified_ciphertext, ciphertext.encode())])
    assert diff == 1


def test_n_close_ham():
    text = "Hello, World!"
    n = 5
    hashes = n_close_ham(text, n)
    
    # Check that the function returns the correct number of hashes
    assert len(hashes) == n

    # Check that each hash is not equal to the original text
    for h in hashes:
        assert h != text.encode()

    # Check that each hash is the same length as the original text
    for h in hashes:
        assert len(h) == len(text)

    # Check that each hash has exactly one bit difference from the original text
    for h in hashes:
        diff = sum([bin(x ^ y).count('1') for x, y in zip(h, text.encode())])
        assert diff == 1