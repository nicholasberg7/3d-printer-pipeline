import configparser, os
cfg_path = os.path.expanduser('~/AI_PIPELINE/CONFIG/color_map.cfg')
p = configparser.ConfigParser()
p.read(cfg_path)
print("Groups:", len(p.sections()))
for s in p.sections():
    print(f"- {s}: {p[s].get('label')} -> {p[s].get('hex')}")
