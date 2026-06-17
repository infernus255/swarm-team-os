import unittest
import pathlib
import re
import math

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX_HTML_PATH = REPO_ROOT / "index.html"

class TestPhysicsSimulation(unittest.TestCase):
    def get_game_constants(self):
        """Extract physics constants directly from index.html to ensure test-code alignment."""
        content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        constants = {}
        for name in ["BLOCK_SIZE", "GRAVITY", "FRICTION", "WALK_ACCEL", "JUMP_FORCE", "MAX_FALL_SPEED"]:
            match = re.search(r"const\s+" + name + r"\s*=\s*(-?\d+\.?\d*);", content)
            if match:
                constants[name] = float(match.group(1))
            else:
                raise ValueError(f"Constant {name} not found in index.html")
        return constants

    def test_horizontal_mobility(self):
        """Ensure that player horizontal speed allows crossing at least 1 block per second."""
        consts = self.get_game_constants()
        
        # Simulating player update loop
        vx = 0.0
        x = 100.0
        dt = 1.0 / 60.0
        ax = 1.0  # Walking right
        
        for _ in range(60):
            vx += ax * consts["WALK_ACCEL"] * dt
            vx *= math.pow(consts["FRICTION"], dt * 60)
            x += vx * dt
            
        distance_moved = x - 100.0
        min_required_distance = consts["BLOCK_SIZE"] * 1.5  # must cross at least 1.5 blocks/sec
        
        self.assertGreater(
            distance_moved, 
            min_required_distance, 
            f"Player only moved {distance_moved:.1f} pixels in 1s (required at least {min_required_distance}px). "
            f"Check if FRICTION ({consts['FRICTION']}) is too low."
        )

    def test_probabilistic_random_walk(self):
        """Run a Monte Carlo random walk simulation to verify player state stability."""
        consts = self.get_game_constants()
        
        # Spawn player on flat ground at y=271.99 (standing on y=10, block size 32)
        x, y = 100.0, 271.99
        vx, vy = 0.0, 0.0
        on_ground = True
        dt = 1.0 / 60.0
        
        # Simple PRNG for deterministic reproducibility
        def prng(seed):
            a = seed
            while True:
                a = (a * 1103515245 + 12345) & 0x7fffffff
                yield a / 2147483647.0

        gen = prng(42)
        
        # Simulate 300 steps of random inputs
        for step in range(300):
            # Probabilistic inputs: 40% walk right, 40% walk left, 20% idle
            rand_val = next(gen)
            ax = 1.0 if rand_val < 0.4 else (-1.0 if rand_val < 0.8 else 0.0)
            
            if step < 250 and next(gen) < 0.15 and on_ground:
                vy = consts["JUMP_FORCE"]
                on_ground = False
                
            # Physics step
            vy += consts["GRAVITY"] * dt
            if vy > consts["MAX_FALL_SPEED"]:
                vy = consts["MAX_FALL_SPEED"]
                
            vx += ax * consts["WALK_ACCEL"] * dt
            vx *= math.pow(consts["FRICTION"], dt * 60)
            
            # Simple collision resolution
            x += vx * dt
            y += vy * dt
            
            # Ground constraint
            if y >= 271.99:
                y = 271.99
                vy = 0.0
                on_ground = True
                
        # Assert the simulation completed without NaN/Inf values
        self.assertTrue(math.isfinite(x), "Player X coordinate became NaN or Infinite")
        self.assertTrue(math.isfinite(y), "Player Y coordinate became NaN or Infinite")
        self.assertTrue(on_ground, "Player did not land back on the ground at the end of the random walk")

if __name__ == "__main__":
    unittest.main()
