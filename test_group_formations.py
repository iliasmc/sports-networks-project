from unittest import TestCase

from group_formations import permute_xy, permute_xy_with_subs


class Test(TestCase):
    def test_permute_xy(self):
        form_4231 = '4-2-3-1'
        def_perm = {form_4231: ['TW', "LV", "RV"]}

        # input - assume we have 3 players and 5 time frames
        xy_home = [[12, 34, 56, 3, 22, 88], [13, 35, 57, 4, 23, 89], [1, 3, 5, 3, 2, 8], [0, 0, 0, 0, 0, 0],
                   [100, 134, 156, 103, 122, 188]]

        home_formation = '4-2-3-1'
        position_to_shirt_number = {"LV": [20], 'TW': [1], "RV": [15]}
        shirt_number_to_index = [15, 1, 20]

        # output - expected: xy_home permuted
        output = [[56, 3, 22, 88, 12, 34], [57, 4, 23, 89, 13, 35], [5, 3, 2, 8, 1, 3], [0, 0, 0, 0, 0, 0],
                  [156, 103, 122, 188, 100, 134]]

        assert permute_xy(xy_home, home_formation, shirt_number_to_index, position_to_shirt_number, def_perm) == output

    def test_permute_xy_subs(self):
        form_4231 = '4-2-3-1'
        def_perm = {form_4231: ['TW', "LV", "RV"]}

        substitute_player_shirt1 = 77
        substitute_player_shirt2 = 88

        # input - assume we have 3 players + 1 substitute and 5 time frames
        xy_home = [[12, 34, 56, 3, 22, 88, None, None, None, None], [13, 35, 57, 4, 23, 89, None, None, None, None],
                   [1, 3, 5, 3, 2, 8, None, None], [0, 0, None, None, 0, 0, 0, 0, None, None],
                   [100, 134, None, None, 122, 188, None, None, 156, 103]]

        home_formation = '4-2-3-1'
        position_to_shirt_number = {"LV": [20], 'TW': [1, substitute_player_shirt1, substitute_player_shirt2],
                                    "RV": [15]}
        shirt_number_to_index = [15, 1, 20, substitute_player_shirt1, substitute_player_shirt2]

        # expected output
        output = [[56, 3, 22, 88, 12, 34], [57, 4, 23, 89, 13, 35], [5, 3, 2, 8, 1, 3], [0, 0, 0, 0, 0, 0],
                  [156, 103, 122, 188, 100, 134]]

        assert permute_xy_with_subs(xy_home, home_formation, shirt_number_to_index, position_to_shirt_number,
                                    def_perm) == output
