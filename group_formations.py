import os
from collections import defaultdict

from floodlight.io.dfl import read_position_data_xml
from lxml import etree

path = 'data/'


def get_lineup(match_info_file: str):
    # position_file = "DFL_04_03_positions_raw_observed_DFL-COM-000002_DFL-MAT-J03WOH.xml"
    # info_file = "DFL_02_01_matchinformation_DFL-COM-000002_DFL-MAT-J03WOH.xml"
    tree = etree.parse(path + str(match_info_file))
    root = tree.getroot()
    teams = root.find("MatchInformation").find("Teams")
    home_id = root.find("MatchInformation").find("General").get("HomeTeamId")
    if "AwayTeamId" in root.find("MatchInformation").find("General").attrib:
        away_id = root.find("MatchInformation").find("General").get("AwayTeamId")
    elif "GuestTeamId" in root.find("MatchInformation").find("General").attrib:
        away_id = root.find("MatchInformation").find("General").get("GuestTeamId")
    else:
        away_id = None

    home_lineup, away_lineup = None, None
    for team_info in teams:
        if team_info.get("TeamId") == home_id:
            home_lineup = team_info.get("LineUp")
        elif team_info.get("TeamId") == away_id:
            away_lineup = team_info.get("LineUp")

    return home_lineup, away_lineup


rev_form_4231 = {0: "TW",
                 1: "LV",
                 2: "IVL",
                 3: "RV",
                 4: "IVR",
                 5: "DML",
                 6: "DMR",
                 7: "ORM",
                 8: "OLM",
                 9: "ZO",
                 10: "STZ"}

form_4231 = {'TW': 0, "LV": 1, "IVL": 2, "RV": 3, "IVR": 4, "DML": 5, "DMR": 6, "ORM": 7, "OLM": 8, "ZO": 9, "STZ": 10}

# player position -> shirt numbers
# TODO add substitutes: currently only starting lineup
match_bayern_koln_away = {'TW': [27, 26], "LV": [40], "IVL": [4], "RV": [5], "IVR": [2], "DML": [38], "DMR": [6],
                          "ORM": [10], "OLM": [11], "ZO": [25], "STZ": [7]}
match_bayern_koln_home = {'TW': [20], "LV": [14], "IVL": [24], "RV": [2], "IVR": [4], "DML": [28], "DMR": [6],
                          "ORM": [7], "OLM": [37], "ZO": [11], "STZ": [27]}
match_bochum_leverkusen_away = {'TW': [1], "LV": [5], "IVL": [12], "RV": [30], "IVR": [4], "DML": [11], "DMR": [25],
                                "OLM": [19], "ZO": [27], "ORM": [21], "STZ": [9]}
match_dussel_regensburg_home = {'TW': [33], "LV": [34], "IVL": [30], "RV": [25], "IVR": [3], "DML": [29], "DMR": [31],
                                "OLM": [7], "ZO": [9], "ORM": [11], "STZ": [10]}
match_dussel_regensburg_away = {'TW': [33], "LV": [20], "IVL": [30], "RV": [25], "IVR": [3], "DML": [29], "DMR": [5],
                                "OLM": [29], "ZO": [9], "ORM": [11], "STZ": [10]}

match_title_to_players = {"1. FC Köln:FC Bayern München": [match_bayern_koln_home, match_bayern_koln_away],
                          "VfL Bochum 1848:Bayer 04 Leverkusen": [match_bochum_leverkusen_away],
                          "Fortuna Düsseldorf:SSV Jahn Regensburg": [match_dussel_regensburg_home]}


def get_permutation(formation, positions):
    if formation == '4-2-3-1':
        # positions = ['TW', 'ZO', 'IV']
        # coords = [0, 0, 1, 1, 2, 2]
        # TODO only choose starting lineup -> Starting=True
        goal_perm = ['TW', "LV", "IVL", "IVR", "RV", "DML", "DMR", "OLM", "ZO", "ORM", "STZ"]
        indices_old = [0 for _ in range(len(goal_perm))]
        for idx, position in enumerate(positions):
            indices_old[goal_perm.index(position)] = idx
        return indices_old
    pass


if __name__ == "__main__":
    info_files = [x for x in os.listdir(path) if "matchinformation" in x]
    position_files = [x for x in os.listdir(path) if "positions_raw" in x]

    formations = defaultdict(list)

    for position_file, info_file in zip(position_files, info_files):
        home_lineup, away_lineup = get_lineup(info_file)
        xy_objects, _, _, teamsheets, _ = read_position_data_xml(os.path.join(path, position_file),
                                                                 os.path.join(path, info_file))
        # home logic
        x = []
        y = []
        x_positions = xy_objects["firstHalf"]["Home"].x
        y_positions = xy_objects["firstHalf"]["Home"].y
        for time_frame in range(len(x_positions)):
            permuted_indices = get_permutation(home_lineup, teamsheets['Home'].teamsheet['position'].tolist())
            x_permutated_players = [0 for _ in range(20)]
            y_permutated_players = [0 for _ in range(20)]
            for i in range(20):
                x_permutated_players[i] = x_positions[permuted_indices[i]]
                y_permutated_players[i] = y_positions[permuted_indices[i]]
            x.append(x_permutated_players)
            y.append(y_permutated_players)

        xy = []
        for x, y in zip(x, y):
            positions_row = []
            for i in range(20):
                positions_row.append(x[i])
                positions_row.append(y[i])
            xy.append(positions_row)


        # formations[home_lineup].append(xy_objects["secondHalf"]["Home"].xy)
        # formations[away_lineup].append(xy_objects["firstHalf"]["Away"].xy)
        # formations[away_lineup].append(xy_objects["secondHalf"]["Away"].xy)

    for key, val in formations.items():
        print(key + ": " + str(len(val) / 2) + " teams")
