from src.util import sha256_hash
import uuid
import time 
import matplotlib.pyplot as plt

class CollisionFinder: 
  def __init__(self, hash_function: callable, digest_size: int) -> None:
    self.hash_function = hash_function
    self.digest_size = digest_size
    self.seen_hashes = {}
    self.start_time = 0
    self.end_time = 0

  def find_collisions(self):
    self.start_time = time.time()
    value = CollisionFinder.generate_unique_string()
    hash = self.hash_value(value)
    while not hash in self.seen_hashes:
      self.seen_hashes[hash] = value
      value = CollisionFinder.generate_unique_string()
      hash = self.hash_value(value)
    self.end_time = time.time()
    return value

  
  def print_stats(self):
    print (f"Time elapsed: {self.end_time - self.start_time}")
    print (f"Number of hashes calculated: {len(self.seen_hashes)}")
    print ("digest size: ", self.digest_size)


  def hash_value(self, value: str) -> bytes:
    #truncate data to digest size i bits. I want the first i bits of the digest
    digest = sha256_hash(value)
    int_value = int.from_bytes(digest.encode(), 'big')
    mask = (1 << self.digest_size) - 1
    result = int_value >> (len(value * 8) - self.digest_size)
    extracted_bits = result & mask 
    byte_length = (self.digest_size + 7) // 8  # Calculate how many bytes are needed
    return extracted_bits.to_bytes(byte_length, 'big')
  
  def generate_unique_string():
    return str(uuid.uuid4())
  
  def generate_graphs():
    digest_sizes = []
    num_hashes = []
    times = []
    for i in range (8, 50, 2):
      print(f"starting digest size: {i}")
      cf = CollisionFinder(sha256_hash, i)
      cf.find_collisions()
      print (f"finished digest size: {i}")
      digest_sizes.append(i)
      num_hashes.append(len(cf.seen_hashes))
      times.append(cf.end_time - cf.start_time)
      del cf
    
    plt.figure()
    plt.plot(digest_sizes, num_hashes)
    plt.xlabel('Digest Size')
    plt.ylabel('Number of Hashes Calculated')
    plt.title('Relationship between Digest Size and Number of Hashes Calculated')
    plt.savefig('num_hashes.png')

    plt.figure()
    plt.plot(digest_sizes, times)
    plt.xlabel('Digest Size')
    plt.ylabel('Time Taken')
    plt.title('Relationship between Digest Size and Time Taken')
    plt.savefig('time_taken.png')
      




