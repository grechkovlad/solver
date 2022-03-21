import unittest
from fractions import Fraction as Q

from arithmetics.LRATheory import solve, _create_aux_problem_canonical_repr, _pivot


def _check_constraint(constraint, valuation):
    constraint_left_side = constraint[0]
    sign = constraint[1]
    right_side = constraint[2]
    left_side_res = sum([c * val for c, val in zip(constraint_left_side, valuation)])
    match sign:
        case "<=":
            return left_side_res <= right_side
        case ">=":
            return left_side_res >= right_side
        case "=":
            return left_side_res == right_side
    raise ValueError(sign)


class TestBases:
    class TestSolvingBase(unittest.TestCase):
        def _get_constraints(self):
            raise NotImplementedError("Must define input constraints")

        def _is_sat(self):
            raise NotImplementedError("Must define the expected result")

        def test_solving(self):
            constraints = self._get_constraints()
            valuation = solve(constraints)
            if self._is_sat():
                self.assertFalse(valuation is None)
                self.assertTrue(all([_check_constraint(constraint, valuation) for constraint in constraints]))
            else:
                self.assertTrue(valuation is None)

    class CanonicalFormConstructionTestBase(unittest.TestCase):
        def _get_constraints(self):
            raise NotImplementedError("Must define input constraints")

        def _get_expected(self):
            raise NotImplementedError("Must define expected canonical form")

        def test_solving(self):
            constraints = self._get_constraints()
            obj_func_exp, A_exp, c_exp, base_vars_exp = self._get_expected()
            obj_func_act, A_act, c_act, base_vars_act, _ = _create_aux_problem_canonical_repr(constraints)
            self.assertEqual(obj_func_exp, obj_func_act)
            self.assertTrue(all([isinstance(val, Q) for val in obj_func_act]))
            self.assertEqual(A_exp, A_act)
            self.assertTrue(all([isinstance(val, Q) for row in A_act for val in row]))
            self.assertEqual(c_exp, c_act)
            self.assertTrue(all([isinstance(val, Q) for val in c_act]))
            self.assertEqual(base_vars_exp, base_vars_act)

    class PivotTestBase(unittest.TestCase):
        def _get_pivot_arguments(self):
            raise NotImplementedError("Must define input problem")

        def _get_expected_output(self):
            raise NotImplementedError("Must define expected output")

        def test_pivoting(self):
            obj_func_coeffs, obj_fun_bias, a, c, base_vars, out_constraint_index, in_var = self._get_pivot_arguments()
            obj_func_coeffs_exp, obj_fun_bias_exp, a_exp, c_exp, base_vars_exp = self._get_expected_output()
            obj_func_coeffs_act, obj_fun_bias_act, a_act, c_act, base_vars_act = _pivot(
                obj_func_coeffs, obj_fun_bias, a, c, base_vars, out_constraint_index, in_var)
            self.assertEqual(obj_func_coeffs_exp, obj_func_coeffs_act)
            self.assertEqual(obj_fun_bias_exp, obj_fun_bias_act)
            self.assertEqual(a_exp, a_act)
            self.assertEqual(base_vars_exp, base_vars_act)


class SimpleCanonicalFormTestOne(TestBases.CanonicalFormConstructionTestBase):
    def _get_constraints(self):
        return [([1, 1], "<=", 5), ([-1, 2], ">=", 0)]  # x0 + x1 <= 5 && -x0 + 2x1 >= 0

    def _get_expected(self):
        # -x6
        obj_fun = [0, 0, 0, 0, 0, 0, -1]
        # x4 = 5 - x0 - x1 + x2 + x3 + x6
        # x5 = 0 - x0 + 2x1 + x2 - 2x3 + x6
        c = [5, 0]
        A = [[-1, -1, 1, 1, 0, 0, 1], [-1, 2, 1, -2, 0, 0, 1]]
        base_vars = [4, 5]
        return obj_fun, A, c, base_vars


class SimpleCanonicalFormTestTwo(TestBases.CanonicalFormConstructionTestBase):
    def _get_constraints(self):
        return [([-2, 1], "=", 3),
                ([0, 1], ">=", 1),
                ([1, 1], "<=", 7)]

    def _get_expected(self):
        # -x8
        obj_fun = [0, 0, 0, 0, 0, 0, 0, 0, -1]
        # x4 = 3 + 2x0 - x1 - 2x2 + x3 + x8
        # x5 = -3 - 2x0 + x1 + 2x2 - x3 + x8
        # x6 = -1 + x1 - x3 + x8
        # x7 = 7 - x0 - x1 + x2 + x3 + x8
        a = [[2, -1, -2, 1, 0, 0, 0, 0, 1],
             [-2, 1, 2, -1, 0, 0, 0, 0, 1],
             [0, 1, 0, -1, 0, 0, 0, 0, 1],
             [-1, -1, 1, 1, 0, 0, 0, 0, 1]]
        c = [3, -3, -1, 7]
        base_vars = [4, 5, 6, 7]
        return obj_fun, a, c, base_vars


class SimpleCanonicalFormTestThree(TestBases.CanonicalFormConstructionTestBase):
    def _get_constraints(self):
        return [([1, 1], "=", -1)]

    def _get_expected(self):
        # -x6
        obj_fun = [0, 0, 0, 0, 0, 0, -1]
        # x4 = -1 - x0 - x1 + x2 + x3 + x6
        # x5 = 1 + x0 + x1 - x2 - x3 + x6
        a = [[-1, -1, 1, 1, 0, 0, 1],
             [1, 1, -1, -1, 0, 0, 1]]
        c = [-1, 1]
        base_vars = [4, 5]
        return obj_fun, a, c, base_vars


class SimplePivotTestOne(TestBases.PivotTestBase):
    def _get_pivot_arguments(self):
        obj_fun_coeffs = [0, 0, 0, 0, 0, 0, -1]
        obj_fun_bias = 0
        a = [[-1, -1, 1, 1, 0, 0, 1],
             [1, 1, -1, -1, 0, 0, 1]]
        c = [-1, 1]
        base_vars = [4, 5]
        out_constraint = 0
        in_var = 6
        return obj_fun_coeffs, obj_fun_bias, a, c, base_vars, out_constraint, in_var

    def _get_expected_output(self):
        obj_fun_coeffs = [-1, -1, 1, 1, -1, 0, 0]
        obj_fun_bias = -1
        a = [[1, 1, -1, -1, 1, 0, 0],
             [2, 2, -2, -2, 1, 0, 0]]
        c = [1, 2]
        base_vars = [6, 5]
        return obj_fun_coeffs, obj_fun_bias, a, c, base_vars


class SimplePivotTestTwo(TestBases.PivotTestBase):
    def _get_pivot_arguments(self):
        obj_fun_coeffs = [-1, -1, 1, 1, -1, 0, 0]
        obj_fun_bias = -1
        a = [[1, 1, -1, -1, 1, 0, 0],
             [2, 2, -2, -2, 1, 0, 0]]
        c = [1, 2]
        base_vars = [6, 5]
        out_constraint = 0
        in_var = 2
        return obj_fun_coeffs, obj_fun_bias, a, c, base_vars, out_constraint, in_var

    def _get_expected_output(self):
        obj_fun_coeffs = [0, 0, 0, 0, 0, 0, -1]
        obj_fun_bias = 0
        a = [[1, 1, 0, -1, 1, 0, -1],
             [0, 0, 0, 0, -1, 0, 2]]
        c = [1, 0]
        base_vars = [2, 5]
        return obj_fun_coeffs, obj_fun_bias, a, c, base_vars


class EmptyTest(TestBases.TestSolvingBase):
    def _is_sat(self):
        return True

    def _get_constraints(self):
        return []


class SingleConstraintTest(TestBases.TestSolvingBase):
    def _is_sat(self):
        return True

    def _get_constraints(self):
        return [([1], "<=", 0)]  # x <= 0


class TwoConstraintsTest(TestBases.TestSolvingBase):
    def _is_sat(self):
        return True

    def _get_constraints(self):
        return [([1, 1], "<=", 5), ([-1, 2], ">=", 0)]  # x0 + x1 <= 5 && -x0 + 2x1 >= 0


class SimpleTestOne(TestBases.TestSolvingBase):
    def _is_sat(self):
        return True

    def _get_constraints(self):
        return [([1, 1], ">=", 3),
                ([0, 1], "<=", 10),
                ([1, 0], "=", 2)]


class SimpleTestTwo(TestBases.TestSolvingBase):
    def _is_sat(self):
        return True

    def _get_constraints(self):
        return [([0, 1], ">=", 2),
                ([0, 1], ">=", 3),
                ([1, -1], ">=", 0)]


class SimpleTestThree(TestBases.TestSolvingBase):
    def _is_sat(self):
        return True

    def _get_constraints(self):
        return [([1, 2, -1], ">=", 2),
                ([-2, 0, 1], "<=", 1),
                ([1, -1], "=", -1)]


class SimpleTestFour(TestBases.TestSolvingBase):
    def _is_sat(self):
        return True

    def _get_constraints(self):
        return [([2, -1, 3], ">=", 100),
                ([2, 1, 1], "=", 108),
                ([0, 1, 0], ">=", -5)]


class SimpleTestFive(TestBases.TestSolvingBase):
    def _is_sat(self):
        return True

    def _get_constraints(self):
        return [([2, -1, 3], "=", 324),
                ([2, 1, 1], "=", 108),
                ([0, 1, 0], "=", -2), ]


class SimpleTestSix(TestBases.TestSolvingBase):
    def _is_sat(self):
        return False

    def _get_constraints(self):
        return [([0, 1], ">=", 3),
                ([1, 0], ">=", 4),
                ([1, 1], "<=", 1)]


class SimpleTextSeven(TestBases.TestSolvingBase):
    def _is_sat(self):
        return True

    def _get_constraints(self):
        return [([2], "=", 1)]


class SimplestContradictionTest(TestBases.TestSolvingBase):
    def _is_sat(self):
        return False

    def _get_constraints(self):
        return [([1], "<=", 0), ([1], ">=", 1)]  # x <= 0 && x >= 1
