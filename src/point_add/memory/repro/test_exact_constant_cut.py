from exact_constant_cut import (
    ONE,
    UNKNOWN,
    ZERO,
    store_one_if,
    store_zero_if,
    tri_and,
    tri_xor,
)


def test_lattice_is_fail_closed() -> None:
    assert tri_and(ZERO, UNKNOWN) == ZERO
    assert tri_and(ONE, UNKNOWN) == UNKNOWN
    assert tri_xor(UNKNOWN, UNKNOWN) == UNKNOWN


def test_conditional_store_preserves_only_matching_constant() -> None:
    assert store_zero_if(ZERO, UNKNOWN) == ZERO
    assert store_zero_if(ONE, UNKNOWN) == UNKNOWN
    assert store_one_if(ONE, UNKNOWN) == ONE
    assert store_one_if(ZERO, UNKNOWN) == UNKNOWN
