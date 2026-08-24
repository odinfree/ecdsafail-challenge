from affine_nonlinear_scan import (
    ONE,
    UNKNOWN,
    ZERO,
    affine_not,
    affine_xor,
    atom,
    product,
)


def test_affine_xor_and_complement_are_canonical() -> None:
    a = atom(1)
    b = atom(2)
    assert affine_xor(a, a) == ZERO
    assert affine_xor(a, affine_not(a)) == ONE
    assert affine_xor(a, b) == affine_xor(b, a)


def test_boolean_products_reduce_equal_and_complementary_controls() -> None:
    a = atom(1)
    assert product([a, a]) == a
    assert product([a, affine_not(a)]) == ZERO
    assert product([ONE, a]) == a
    assert product([UNKNOWN, ZERO]) == ZERO


def test_three_way_affine_inconsistency_is_proved_zero() -> None:
    a = atom(1)
    b = atom(2)
    a_xor_b = affine_xor(a, b)
    assert product([a, b, a_xor_b]) == ZERO
