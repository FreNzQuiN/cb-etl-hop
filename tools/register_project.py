import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lingkungan import cari_hop, pesan_hop

CONFIG = os.path.join(cari_hop() or "", "config", "hop-config.json")
PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMA_PROJECT = "tokomaju"

if not os.path.exists(CONFIG):
    print(pesan_hop())
    raise SystemExit(1)

with open(CONFIG, "r", encoding="utf-8") as f:
    cfg = json.load(f)

projects = cfg.setdefault("projectsConfig", {}).setdefault("projectConfigurations", [])
entry = {
    "projectName": NAMA_PROJECT,
    "projectHome": PROJECT_HOME.replace("\\", "/"),
    "configFilename": "project-config.json",
    "readOnly": False,
    "group": None,
    "tags": [],
    "tagsAsDisplayString": "",
}

for i, project in enumerate(projects):
    if project.get("projectName") == NAMA_PROJECT:
        projects[i] = entry
        break
else:
    projects.append(entry)

with open(CONFIG, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2)

print("project %s terdaftar di %s -> %s" % (NAMA_PROJECT, CONFIG, entry["projectHome"]))
