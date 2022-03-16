from arithmetics.LAProblemParser import parse
import unittest


class TestBases:
    class ParsingTestBase(unittest.TestCase):
        def _get_input(self):
            raise NotImplementedError("Must define input constraints")

        def _get_expected(self):
            raise NotImplementedError("Must define expected result")

        def test_parsing(self):
            constraints, names = parse(self._get_input())
            for actual_constraint, expected_constraint in zip(constraints, self._get_expected()):
                self.assertEqual(expected_constraint[1], actual_constraint[1])
                self.assertEqual(expected_constraint[2], actual_constraint[2])
                for var_name, var_coeff in expected_constraint[0].items():
                    self.assertEqual(var_coeff, actual_constraint[0][names[var_name]])


class SimpleTestOne(TestBases.ParsingTestBase):
    def _get_input(self):
        return ["5x + y <= 12",
                "x - 2y = -4"]

    def _get_expected(self):
        return [({"x": 5, "y": 1}, "<=", 12),
                ({"x": 1, "y": -2}, "=", -4)]


class SimpleTestTwo(TestBases.ParsingTestBase):
    def _get_input(self):
        return ["-x + y <= -5"]

    def _get_expected(self):
        return [({"x": -1, "y": 1}, "<=", -5)]


class SimpleTestThree(TestBases.ParsingTestBase):
    def _get_input(self):
        return ["10x - 2x + x - 2y + z = -6",
                "2z - y = 15",
                "2y >= 0"]

    def _get_expected(self):
        return [({"x": 9, "y": -2, "z": 1}, "=", -6),
                ({"z": 2, "y": -1, "x": 0}, "=", 15),
                ({"x": 0, "y": 2, "z": 0}, ">=", 0)]
