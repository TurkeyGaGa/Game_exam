#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")" && pwd)
dest=${BIRDS_TEMP:?}
mkdir -p "$dest"
cd "$dest"
if [ ! -f Linux.zip ]; then
  curl --fail --location --retry 3 -o Linux.zip https://raw.githubusercontent.com/phy-q/benchmark/514491c5e77dbacdd61066d11139434f982e3d9e/sciencebirdsgames/Linux.zip
fi
sha256sum -c "$root/linux.sha256"
unzip -qo Linux.zip
cd Linux
chmod +x 9001.x86_64
curl --fail -sSL --retry 3 -o "$dest/levels.zip" https://raw.githubusercontent.com/phy-q/benchmark/514491c5e77dbacdd61066d11139434f982e3d9e/sciencebirdslevels/generated_levels/fifth_generation.zip
unzip -p "$dest/levels.zip" fifth_generation/3/06/06/3_06_06_00002.xml > 9001_Data/StreamingAssets/Levels/novelty_level_1/type1/Levels/3_06_06_00002.xml
export ALSA_CONFIG_PATH="$root/alsa.conf"
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
tree=ET.parse("config.xml")
levels=tree.find(".//game_level_set")
level=next(item for item in levels if item.attrib["level_path"].endswith("/1_01_01_00002.xml"))
for child in list(levels): levels.remove(child)
levels.set("attempt_limit_per_level","100")
levels.append(level)
level.set("level_path",str(Path("9001_Data/StreamingAssets/Levels/novelty_level_1/type1/Levels/3_06_06_00002.xml").resolve(strict=True)))
tree.write("config.xml")
PY
export LIBGL_ALWAYS_SOFTWARE=1
java -jar game_playing_interface.jar --dev >"$dest/server.log" 2>&1 &
server=$!
trap 'kill "$server" 2>/dev/null || true; tail -45 "$dest/server.log"' EXIT
python3 -u "$root/probe.py"
