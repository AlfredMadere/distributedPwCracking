from src.collision_finder import CollisionFinder
from src.util import sha256_hash

## do the main thing

# cf = CollisionFinder(sha256_hash, 50)
# cf.find_collisions()
# cf.print_stats()
CollisionFinder.generate_graphs()