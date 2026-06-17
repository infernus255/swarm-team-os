import unittest
import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX_HTML_PATH = REPO_ROOT / "index.html"
APP_RESULT_HTML_PATH = REPO_ROOT / "app_result" / "index.html"

class TestMobileGame(unittest.TestCase):
    def test_html_files_exist(self):
        """Verify that the game index.html files exist in the proposed locations."""
        self.assertTrue(INDEX_HTML_PATH.exists(), "index.html does not exist in workspace root")
        self.assertTrue(APP_RESULT_HTML_PATH.exists(), "index.html does not exist in app_result/")

    def test_zero_dependencies(self):
        """Verify that the game has no external dependencies (CDNs, external styles, scripts, or images)."""
        if not INDEX_HTML_PATH.exists():
            self.skipTest("index.html not found")
            
        content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        
        # Check for external scripts (src="..." where src contains http, https, or remote references)
        external_scripts = re.findall(r'<script\s+[^>]*src=["\']([^"\']+)["\']', content, re.IGNORECASE)
        # Verify local relative scripts exist and filter them out
        for script in external_scripts:
            if script.startswith("js/"):
                self.assertTrue((REPO_ROOT / script).exists(), f"Local script {script} not found")
        external_scripts = [s for s in external_scripts if not s.startswith("js/")]
        self.assertEqual(len(external_scripts), 0, f"Found external script references: {external_scripts}")
        
        # Check for external CSS (href="..." where href contains http, https, or remote references)
        external_css = re.findall(r'<link\s+[^>]*rel=["\']stylesheet["\']\s+[^>]*href=["\']([^"\']+)["\']', content, re.IGNORECASE)
        # Verify local relative styles exist and filter them out
        for css in external_css:
            if css.startswith("css/"):
                self.assertTrue((REPO_ROOT / css).exists(), f"Local CSS {css} not found")
        external_css = [c for c in external_css if not c.startswith("css/")]
        self.assertEqual(len(external_css), 0, f"Found external CSS references: {external_css}")
        
        # Check for remote CDNs or URLs anywhere in scripts/links, combined with local JS and CSS files
        all_contents = content
        js_dir = REPO_ROOT / "js"
        if js_dir.exists():
            for js_file in js_dir.glob("*.js"):
                all_contents += "\n" + js_file.read_text(encoding="utf-8")
        css_dir = REPO_ROOT / "css"
        if css_dir.exists():
            for css_file in css_dir.glob("*.css"):
                all_contents += "\n" + css_file.read_text(encoding="utf-8")

        remote_refs = re.findall(r'https?://[^\s"\'>]+', all_contents)
        # Allow STUN server for WebRTC (required for P2P, not a CDN dependency)
        forbidden_cdns = ["cdnjs", "unpkg", "jsdelivr", "googleapis", "tailwind", "bootstrap", "jquery"]
        for ref in remote_refs:
            for cdn in forbidden_cdns:
                self.assertNotIn(cdn, ref.lower(), f"Found potential remote dependency reference: {ref}")

    def test_html_structure(self):
        """Verify that the index.html contains the necessary DOM elements for the game HUD and Canvas."""
        if not INDEX_HTML_PATH.exists():
            self.skipTest("index.html not found")
            
        content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        
        required_elements = [
            'id="gameCanvas"',
            'id="hud"',
            'id="perf"',
            'id="palette"',
            'id="btn-sound"',
            'id="btn-reset"'
        ]
        
        for element in required_elements:
            with self.subTest(element=element):
                self.assertIn(element, content, f"Required DOM element spec '{element}' not found in index.html")

    def test_js_modules_and_classes(self):
        """Verify that the core game architecture modules and classes are defined in the JS script."""
        if not INDEX_HTML_PATH.exists():
            self.skipTest("index.html not found")
            
        content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        js_dir = REPO_ROOT / "js"
        if js_dir.exists():
            for js_file in sorted(js_dir.glob("*.js")):
                content += "\n" + js_file.read_text(encoding="utf-8")
        
        required_signatures = [
            "class Noise2D",
            "class Audio",
            "class Player",
            "class Camera",
            "class Game",
            "class Multiplayer",
            "WORLD_W",
            "WORLD_H",
            "function simulate()",
            "function explode(",
            "function generateWorld()",
            "simPowder(",
            "simLiquid(",
            "simGas(",
            "simInteract(",
            "requestAnimationFrame(loop)"
        ]
        
        for sig in required_signatures:
            with self.subTest(signature=sig):
                self.assertIn(sig, content, f"Required JS engine signature '{sig}' not found in index.html or external JS files")

if __name__ == "__main__":
    unittest.main()
