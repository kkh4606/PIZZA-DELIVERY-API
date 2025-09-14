import os
import re

base_path = r"C:\Users\Msi Laptop\Desktop\kit-server"
map_path = os.path.join(base_path, "map.txt")

# Regex to match filenames like u0108p1.ftex
pattern = re.compile(r"u0*(\d+)p1\.ftex", re.IGNORECASE)

with open(map_path, "w", encoding="utf-8") as f:
    # Loop over each league folder in base_path
    for league in os.listdir(base_path):
        league_path = os.path.join(base_path, league)
        if not os.path.isdir(league_path):
            continue  # skip files like map.txt

        entries = []

        # Loop over each team folder in the league
        for team_folder in os.listdir(league_path):
            p1_path = os.path.join(league_path, team_folder, "p1")
            if os.path.isdir(p1_path):
                # look for any file that matches the pattern
                for file in os.listdir(p1_path):
                    match = pattern.match(file)
                    if match:
                        team_id = int(match.group(1))
                        entries.append((team_id, f"{league}\\{team_folder}"))
                        break  # only need one file per team

        if entries:
            # Optional: sort by team_id
            entries.sort(key=lambda x: x[0])

            # Write league header
            f.write(f"# {league}\n")

            # Write all team entries
            for team_id, path in entries:
                f.write(f"{team_id}, {path}\n")

            f.write("\n")  # blank line after each league

print("✅ map.txt generated for all leagues")
