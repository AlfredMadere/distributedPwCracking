
from ..src.collision_finder import CollisionFinder
from ..src.util import sha256_hash
import pytest

def test_collision_finder():
    # Create a CollisionFinder with a small digest size
    cf = CollisionFinder(sha256_hash, 5)

    # Call find_collisions and check that it returns a value
    collision = cf.find_collisions()
    assert collision is not None

    # Check that the returned value is in seen_hashes
    assert cf.hash_value(collision) in cf.seen_hashes
    cf.print_stats()



def test_hash_value():
    cf = CollisionFinder(sha256_hash, 16)
    value = "test"
    digest = cf.hash_value(value)
    assert len(digest) == 2  # 16 bits = 2 bytes

    cf = CollisionFinder(sha256_hash, 24)
    digest = cf.hash_value(value)
    assert len(digest) == 3  # 24 bits = 3 bytes

    cf = CollisionFinder(sha256_hash, 1)
    digest = cf.hash_value(value)
    assert len(digest) == 1  # 1 bit = 1 byte (because we can't have less than a byte)

    cf = CollisionFinder(sha256_hash, 8)
    digest = cf.hash_value(value)
    assert len(digest) == 1  # 8 bits = 1 byte

    cf = CollisionFinder(sha256_hash, 9)
    digest = cf.hash_value(value)
    assert len(digest) == 2  # 9 bits = 2 bytes (because we can't have less than a byte)