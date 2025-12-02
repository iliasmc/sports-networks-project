import os
from collections import defaultdict

from floodlight.io.dfl import read_position_data_xml
from lxml import etree

path = 'data/'


def get_lineups_and_title(match_info_file: str):
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

    return home_lineup, away_lineup, root.find("MatchInformation").find("General").get("MatchTitle")


def get_match_title(match_info_file: str):
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


# player position -> shirt numbers
# TODO add substitutes: currently only starting lineup
match_bayern_koln_away = {'TW': [27], "LV": [40], "IVL": [4], "RV": [5], "IVR": [2], "DML": [38], "DMR": [6],
                          "ORM": [10], "OLM": [11], "ZO": [25], "STZ": [7]}
match_bayern_koln_home = {'TW': [20], "LV": [14], "IVL": [24], "RV": [2], "IVR": [4], "DML": [28], "DMR": [6],
                          "ORM": [7], "OLM": [37], "ZO": [11], "STZ": [27]}
match_bochum_leverkusen_away = {'TW': [1], "LV": [5], "IVL": [12], "RV": [30], "IVR": [4], "DML": [11], "DMR": [25],
                                "OLM": [19], "ZO": [27], "ORM": [21], "STZ": [9]}
match_dussel_regensburg_home = {'TW': [33], "LV": [34], "IVL": [30], "RV": [25], "IVR": [3], "DML": [29], "DMR": [31],
                                "OLM": [7], "ZO": [9], "ORM": [11], "STZ": [10]}
match_dussel_regensburg_away = {'TW': [1], "LV": [20], "IVL": [33], "RV": [11], "IVR": [23], "DML": [8], "DMR": [5],
                                "OLM": [29], "ZO": [19], "ORM": [30], "STZ": [18]}
match_dussel_hansa_home = {'TW': [33], "LV": [8], "IVL": [5], "RV": [25], "IVR": [15], "DML": [4], "DMR": [31],
                           "OLM": [7], "ZO": [23], "ORM": [11], "STZ": [9]}
match_dussel_hansa_guest = {'DLM': [21], 'HR': [29], 'DRM': [7], 'HL': [14], 'STR': [19], 'TW': [1], 'STL': [18],
                            'IVZ': [34], 'DMZ': [6], 'IVR': [27], 'IVL': [5]}
match_dussel_nurnberg_home = {'TW': [33], "LV": [8], "IVL": [5], "RV": [25], "IVR": [15], "DML": [31], "DMR": [4],
                              "OLM": [19], "ZO": [23], "ORM": [11], "STZ": [9]}
match_dussel_klautern_guest = {'TW': [1], "LV": [20], "IVL": [2], "RV": [37], "IVR": [32], "DML": [6], "DMR": [7],
                               "OLM": [11], "ZO": [28], "ORM": [8], "STZ": [13]}
match_dussel_pauli_guest = {'DLM': [23], 'HR': [7], 'DRM': [2], 'HL': [10], 'STR': [13], 'TW': [22], 'STL': [14],
                            'IVZ': [8], 'DMZ': [20], 'IVR': [25], 'IVL': [5]}

match_where_away_team_starts_on_right = "Fortuna Düsseldorf:1. FC Kaiserslautern"
match_title_to_players = {
    "1. FC Köln:FC Bayern München": {"home": match_bayern_koln_home, "away": match_bayern_koln_away},
    "VfL Bochum 1848:Bayer 04 Leverkusen": {"away": match_bochum_leverkusen_away},
    "Fortuna Düsseldorf:FC St. Pauli": {"away": match_dussel_pauli_guest},
    match_where_away_team_starts_on_right: {"away": match_dussel_klautern_guest},
    "Fortuna Düsseldorf:1. FC Nürnberg": {"home": match_dussel_nurnberg_home},
    "Fortuna Düsseldorf:SSV Jahn Regensburg": {"home": match_dussel_regensburg_home,
                                               "away": match_dussel_regensburg_away},
    "Fortuna Düsseldorf:F.C. Hansa Rostock": {"home": match_dussel_hansa_home, "away": match_dussel_hansa_guest},
}

form_4231 = '4-2-3-1'
form_3322 = '3-3-2-2'
DEFAULT_PERMUTATIONS_PER_FORMATION = {
    form_4231: ["TW", "LV", "IVL", "RV", "IVR", "DML", "DMR", "ORM", "OLM", "ZO", "STZ"],
    form_3322: ['TW', 'IVL', 'IVZ', 'IVR', 'DLM', 'DMZ', 'DRM', 'HL', 'HR', 'STL', 'STR'],
}


def permute_xy(xy, formation, shirt_to_index, position_to_shirt, default_permutations=None):
    if default_permutations is None:
        default_permutations = DEFAULT_PERMUTATIONS_PER_FORMATION
    positions = default_permutations[formation]

    ordered_shirts = []
    for pos in positions:
        ordered_shirts.extend(position_to_shirt[pos])

    ordered_indices = [shirt_to_index.index(s) for s in ordered_shirts]

    result = []
    for row in xy:
        new_row = []
        for i in range(len(ordered_indices)):
            new_row.append(row[ordered_indices[i] * 2])
            new_row.append(row[ordered_indices[i] * 2 + 1])
        result.append(new_row)
    return result


def process_xy(xy_objects, teamsheets, match_title, formation, team="Home"):
    if match_title != match_where_away_team_starts_on_right:
        if team == "Home":
            xy_objects["firstHalf"][team].rotate(180)
        else:
            xy_objects["secondHalf"][team].rotate(180)
    else:
        if team == "Away":
            xy_objects["firstHalf"][team].rotate(180)
        else:
            xy_objects["secondHalf"][team].rotate(180)

    if formation in DEFAULT_PERMUTATIONS_PER_FORMATION.keys():
        shirt_numbers = teamsheets[team].teamsheet.jID.tolist()  # index == xID
        position_to_shirt = match_title_to_players[match_title][team.lower()]
        result = permute_xy(xy_objects["firstHalf"][team].xy, formation, shirt_numbers, position_to_shirt)
        result += permute_xy(xy_objects["secondHalf"][team].xy, formation, shirt_numbers, position_to_shirt)

        return result

    return xy_objects["firstHalf"][team].xy.tolist() + xy_objects["secondHalf"][team].xy.tolist()


def get_xy_data_grouped_by_formation():
    info_files = [x for x in os.listdir(path) if "matchinformation" in x]
    position_files = [x for x in os.listdir(path) if "positions_raw" in x]

    formations = defaultdict(list)

    for position_file, info_file in zip(position_files, info_files):
        home_formation, away_formation, match_title = get_lineups_and_title(info_file)
        xy_objects, _, _, teamsheets, _ = read_position_data_xml(os.path.join(path, position_file),
                                                                 os.path.join(path, info_file))

        xy_home = process_xy(xy_objects, teamsheets, match_title, home_formation, team="Home")
        for time_frame in xy_home:
            formations[home_formation].append(time_frame)

        print(f"Processed home team for match: {match_title} with lineup {home_formation}")

        xy_away = process_xy(xy_objects, teamsheets, match_title, away_formation, team="Away")
        for time_frame in xy_away:
            formations[away_formation].append(time_frame)

        print(f"Processed away team for match: {match_title} with lineup {away_formation}")

    return formations
