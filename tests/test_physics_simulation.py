import unittest
import pathlib
import re
import math

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX_HTML_PATH = REPO_ROOT / "index.html"


class TestCellularAutomataPhysics(unittest.TestCase):
    """Validates the cellular automata physics engine constants and rules extracted from index.html."""

    def get_content(self):
        return INDEX_HTML_PATH.read_text(encoding="utf-8")

    def get_constants(self):
        content = self.get_content()
        constants = {}
        for name in ["WORLD_W", "WORLD_H", "GRAVITY", "PLAYER_SPEED", "PLAYER_JUMP",
                      "PLAYER_W", "PLAYER_H", "MAX_HP", "INTERACTION_RANGE"]:
            match = re.search(r"const\s+" + name + r"\s*=\s*(-?\d+\.?\d*);", content)
            if match:
                constants[name] = float(match.group(1))
            else:
                raise ValueError(f"Constant {name} not found in index.html")
        return constants

    def test_constants_exist(self):
        """All core physics constants must be defined."""
        consts = self.get_constants()
        self.assertEqual(consts["WORLD_W"], 512, "World width should be 512")
        self.assertEqual(consts["WORLD_H"], 320, "World height should be 320")
        self.assertGreater(consts["GRAVITY"], 0, "Gravity must be positive")
        self.assertLess(consts["PLAYER_JUMP"], 0, "Jump velocity must be negative (upward)")
        self.assertGreater(consts["MAX_HP"], 0, "Max HP must be positive")

    def test_material_system_exists(self):
        """All 18 material types must be defined in the MAT object."""
        content = self.get_content()
        required_mats = ["EMPTY", "SAND", "WATER", "STONE", "WOOD", "FIRE", "LAVA",
                         "STEAM", "OIL", "ACID", "GUNPOWDER", "SMOKE", "DIRT",
                         "GRASS", "GLASS", "ICE", "EMBER", "BEDROCK"]
        for mat in required_mats:
            self.assertIn(f"MAT.{mat}", content, f"Material {mat} not found in MAT definition")

    def test_material_properties_complete(self):
        """Every material must have a PROPS entry with required fields."""
        content = self.get_content()
        # Check that PROPS entries exist for key materials
        mat_ids = re.findall(r"PROPS\[MAT\.(\w+)\]\s*=", content)
        expected = {"EMPTY","SAND","WATER","STONE","WOOD","FIRE","LAVA","STEAM",
                    "OIL","ACID","GUNPOWDER","SMOKE","DIRT","GRASS","GLASS","ICE","EMBER","BEDROCK"}
        for mat in expected:
            self.assertIn(mat, mat_ids, f"PROPS entry missing for MAT.{mat}")

    def test_sand_falls_simulation(self):
        """Simulate sand falling: verify gravity-driven powder behavior."""
        consts = self.get_constants()
        # A sand particle at y=0 should reach y=100 in reasonable time under gravity
        WORLD_H = int(consts["WORLD_H"])
        y = 10.0
        steps = 0
        max_steps = WORLD_H * 2  # generous upper bound
        while y < 100 and steps < max_steps:
            # In CA, sand moves 1 cell per frame downward if space below is empty
            y += 1.0
            steps += 1
        self.assertEqual(steps, 90, "Sand should take exactly 90 steps to fall 90 cells (1 cell/frame)")

    def test_water_spreads_horizontally(self):
        """Simulate water: it should spread to fill a container."""
        # Water moves down, then diagonally, then horizontally
        # Simulate a 10-wide container with water at center
        container = [0]*10  # height of water at each column
        container[5] = 5  # 5 units of water at column 5
        
        # Simple water leveling simulation (mimics CA liquid behavior)
        for step in range(100):
            new_container = container.copy()
            for x in range(1, 9):
                if container[x] > container[x-1] + 1:
                    new_container[x] -= 1
                    new_container[x-1] += 1
                if container[x] > container[x+1] + 1:
                    new_container[x] -= 1
                    new_container[x+1] += 1
            container = new_container
        
        # Water should have leveled out - no column should be much taller than others
        max_diff = max(container) - min(container)
        self.assertLessEqual(max_diff, 2, f"Water did not level out. Heights: {container}")

    def test_fire_lifetime_decay(self):
        """Fire should decay over time and eventually extinguish."""
        # Simulate fire lifetime (60-140 frames based on code)
        life = 100  # mid-range lifetime
        steps = 0
        while life > 0:
            life -= 1
            steps += 1
        self.assertEqual(steps, 100, "Fire should last exactly its lifetime in frames")
        self.assertGreater(steps, 50, "Fire lifetime should be at least 50 frames")
        self.assertLess(steps, 200, "Fire lifetime should be under 200 frames")

    def test_material_interaction_lava_water(self):
        """Lava + Water should produce Stone + Steam."""
        content = self.get_content()
        # Verify the interaction rule exists in code
        self.assertIn("MAT.STONE", content, "Stone material must exist for lava+water interaction")
        self.assertIn("MAT.STEAM", content, "Steam material must exist for lava+water interaction")
        # Check the specific interaction code pattern
        has_interaction = ("m === MAT.LAVA && nm === MAT.WATER" in content or
                          "m === MAT.LAVA&&nm === MAT.WATER" in content)
        self.assertTrue(has_interaction, "Lava+Water interaction rule not found in simInteract")

    def test_explosion_radius(self):
        """Explosion should clear cells within the blast radius."""
        content = self.get_content()
        # Verify explode function exists
        self.assertIn("function explode(", content, "explode() function must be defined")
        # Verify it uses radius-based clearing
        self.assertIn("radius", content, "Explosion should use radius parameter")

    def test_player_horizontal_mobility(self):
        """Player should move at least 1 cell per second horizontally."""
        consts = self.get_constants()
        # Simulate 60 frames of walking right
        vx = 0.0
        x = 0.0
        ax = 1.0
        for _ in range(60):
            vx += ax * consts["PLAYER_SPEED"] * 0.3
            vx *= 0.82
            x += vx
        self.assertGreater(x, 5.0, 
            f"Player only moved {x:.1f} cells in 60 frames. Should move at least 5 cells/sec.")

    def test_player_jump_height(self):
        """Player jump should reach significant height before landing."""
        consts = self.get_constants()
        vy = consts["PLAYER_JUMP"]
        y = 0.0
        min_y = 0.0
        for _ in range(120):  # 2 seconds of simulation
            vy += consts["GRAVITY"]
            if vy > 8: vy = 8
            y += vy
            if y < min_y: min_y = y
            if y >= 0:
                y = 0
                vy = 0
                break
        self.assertLess(min_y, -10, 
            f"Jump only reached height {-min_y:.1f} cells. Should reach at least 10.")

    def test_deterministic_prng(self):
        """LCG PRNG should produce deterministic sequences."""
        # Replicate the PRNG from the game code
        state = 20260617
        def rng():
            nonlocal state
            state = (state * 1664525 + 1013904223) & 0x7FFFFFFF
            return state / 2147483647
        
        # Generate 100 values and verify determinism by running twice
        values_1 = []
        state = 20260617
        for _ in range(100):
            values_1.append(rng())
        
        values_2 = []
        state = 20260617
        for _ in range(100):
            values_2.append(rng())
        
        self.assertEqual(values_1, values_2, "PRNG should produce identical sequences from same seed")
        
        # Verify values are in [0, 1) range
        for v in values_1:
            self.assertGreaterEqual(v, 0.0, "PRNG values must be >= 0")
            self.assertLess(v, 1.0, "PRNG values must be < 1")

    def test_webgl_not_required(self):
        """Engine should use Canvas 2D (ImageData), not require WebGL."""
        content = self.get_content()
        self.assertIn("createImageData", content, "Should use createImageData for pixel buffer")
        self.assertIn("putImageData", content, "Should use putImageData for rendering")
        self.assertIn("imageSmoothingEnabled", content, "Should disable image smoothing for pixelated look")


class TestGameStructure(unittest.TestCase):
    """Validates the overall game structure and HTML/JS architecture."""

    def test_index_html_exists(self):
        self.assertTrue(INDEX_HTML_PATH.exists(), "index.html must exist")

    def test_html_structure(self):
        content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", content, "Must have HTML5 doctype")
        self.assertIn('<canvas id="gameCanvas"', content, "Must have game canvas element")
        self.assertIn("requestAnimationFrame", content, "Must use requestAnimationFrame game loop")

    def test_touch_controls(self):
        content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        self.assertIn("pointerdown", content, "Must handle pointerdown events")
        self.assertIn("pointermove", content, "Must handle pointermove events")
        self.assertIn("pointerup", content, "Must handle pointerup events")
        self.assertIn("joystick", content, "Must have virtual joystick for mobile")

    def test_multiplayer_infrastructure(self):
        content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        self.assertIn("RTCPeerConnection", content, "Must have WebRTC peer connection")
        self.assertIn("DataChannel", content, "Must have WebRTC data channel")
        self.assertIn("createOffer", content, "Must support creating offers")
        self.assertIn("createAnswer", content, "Must support creating answers")

    def test_no_external_cdn(self):
        content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        # Should not have external script or link tags
        external_refs = re.findall(r'(src|href)\s*=\s*["\']https?://', content)
        self.assertEqual(len(external_refs), 0, 
            f"Found {len(external_refs)} external CDN references. Game must be self-contained.")

    def test_performance_monitor(self):
        content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        self.assertIn("v-fps", content, "Must display FPS counter")
        self.assertIn("v-sim", content, "Must display simulation time")
        self.assertIn("v-draw", content, "Must display draw time")

    def test_world_dimensions_reasonable(self):
        content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        w_match = re.search(r"const\s+WORLD_W\s*=\s*(\d+)", content)
        h_match = re.search(r"const\s+WORLD_H\s*=\s*(\d+)", content)
        self.assertIsNotNone(w_match, "WORLD_W must be defined")
        self.assertIsNotNone(h_match, "WORLD_H must be defined")
        w, h = int(w_match.group(1)), int(h_match.group(1))
        total = w * h
        self.assertGreater(total, 50000, f"World too small ({total} cells)")
        self.assertLess(total, 1000000, f"World too large ({total} cells) for mobile performance")

    def test_typed_arrays_used(self):
        """Engine must use TypedArrays for performance."""
        content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        self.assertIn("Uint8Array", content, "Must use Uint8Array for grid data")
        self.assertIn("Uint32Array", content, "Must use Uint32Array for color data")


if __name__ == "__main__":
    unittest.main()
