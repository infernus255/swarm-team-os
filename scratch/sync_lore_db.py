import sys
import os
from datetime import datetime

# Add root folder to sys.path to resolve core module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.sga_client import sga_client

def main():
    print("[Sync] Initiating Neon SGA DB Sync...")
    
    project_id = "PROJECT_FORGE_2D_V1.4"
    phase = "GAMEPLAY_ROADMAP_AND_OVERLAP_FIXES"
    
    # 1. Gameplay Enhancements: Relics & Dash
    gameplay_content = (
        "Project Forge 2D (PES 1.4) integrates the complete gameplay roadmap perks: "
        "(1) Ankh of Life gives +1 HP regen per second and 25% hazard reduction. "
        "(2) Eye of Horus draws a wrapped chest locator line pointing to the nearest unopened chest. "
        "(3) Scarab of Power unlocks brush size 12 and continuous mining/painting with a 50% reduced mining cooldown (4 frames). "
        "(4) Spacebar Dodge Roll / Dash provides high-speed horizontal movement, particle trails, and temporary invincibility (iframes)."
    )
    success1 = sga_client.push_memory(
        project_id=project_id,
        phase=phase,
        content=gameplay_content,
        metadata={"category": "game_mechanics", "tags": ["relics", "dash", "perks"]}
    )
    
    # 2. Physics & Ground Overlap Resolution
    physics_content = (
        "Identified a critical overlap/sinking bug where players and enemies fell into solid blocks due to coordinate rounding errors. "
        "Resolved by implementing an unstuck recovery check (`unstuck()`) that performs an upward scan up to 24px, "
        "and replacing approximate floor equations in enemy physics with a pixel-by-pixel alignment loop that snaps entities perfectly flush "
        "with the ground. This resolves all sinking bugs on spawn and under falling CA sand."
    )
    success2 = sga_client.push_memory(
        project_id=project_id,
        phase=phase,
        content=physics_content,
        metadata={"category": "physics_fixes", "tags": ["sinking_bug", "unstuck", "collision"]}
    )
    
    # 3. Turrets, Elements, and Invite Links
    features_content = (
        "Added static obelisk turrets that shoot linear magenta energy shots at the player, spawning in caverns and core zones. "
        "Implemented elemental staff shots (Fire, Acid, Ice, Plasma) that match the selected material. Acid dissolves blocks; "
        "Ice slows enemies and freezes water/oil; Plasma deals 25 damage and melts stone into lava. "
        "Integrated WebRTC auto-join links (`?#join=offerCode`) that open the invite panel and start connection negotiation automatically."
    )
    success3 = sga_client.push_memory(
        project_id=project_id,
        phase=phase,
        content=features_content,
        metadata={"category": "features_integration", "tags": ["turrets", "elemental_shots", "webrtc_urls"]}
    )
    
    if success1 and success2 and success3:
        print("[Sync] SGA L0/L1 Neon DB Sync completed successfully!")
    else:
        print("[Sync] Neon DB Sync failed or partially failed.", file=sys.stderr)

if __name__ == "__main__":
    main()
