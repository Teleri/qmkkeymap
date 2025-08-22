#!/usr/bin/env python3
import os, re, xml.etree.ElementTree as ET
home = os.path.expanduser("~")
gamelists_root = os.path.join(home, ".emulationstation", "gamelists")
collections_dir = os.path.join(home, ".emulationstation", "collections")
os.makedirs(collections_dir, exist_ok=True)
out_path = os.path.join(collections_dir, "custom-2 Player Games.cfg")

def max_players_from_text(t: str) -> int:
    if not t: return 0
    s = t.strip().lower()
    # Common forms: "2", "1-2", "2-4", "2+", "up to 4", etc.
    # If it has "2+" -> assume 2+
    plus = re.match(r"^\s*(\d+)\s*\+\s*$", s)
    if plus:
        return int(plus.group(1))
    # Ranges like "1-4"
    rng = re.match(r"^\s*(\d+)\s*-\s*(\d+)\s*$", s)
    if rng:
        return max(int(rng.group(1)), int(rng.group(2)))
    # Extract all numbers and take the max
    nums = [int(x) for x in re.findall(r"\d+", s)]
    return max(nums) if nums else 0

def abs_rom_path(system: str, rom_path: str) -> str:
    # If path is already absolute, keep it
    if os.path.isabs(rom_path):
        return rom_path
    # Some gamelists store "./rom.zip" or "roms/xyz"
    romdir = os.path.join(home, "RetroPie", "roms", system)
    # Remove leading "./" if present
    rp = rom_path.lstrip("./")
    return os.path.normpath(os.path.join(romdir, rp))

selected = []
if os.path.isdir(gamelists_root):
    for system in sorted(os.listdir(gamelists_root)):
        gl = os.path.join(gamelists_root, system, "gamelist.xml")
        if not os.path.isfile(gl):
            continue
        try:
            tree = ET.parse(gl)
            root = tree.getroot()
        except Exception:
            continue
        for game in root.findall("game"):
            ptag = game.find("players")
            path_tag = game.find("path")
            if path_tag is None: 
                continue
            maxp = max_players_from_text(ptag.text if ptag is not None else "")
            if maxp >= 2:
                fullpath = abs_rom_path(system, path_tag.text or "")
                # Filter obvious non-ROMs
                if fullpath and os.path.splitext(fullpath)[1]:
                    selected.append(fullpath)

# De-duplicate while preserving order
seen = set()
unique = []
for p in selected:
    if p not in seen:
        seen.add(p)
        unique.append(p)

with open(out_path, "w", encoding="utf-8") as f:
    for p in unique:
        f.write(p + "\n")

print(f"Wrote {len(unique)} entries to: {out_path}")