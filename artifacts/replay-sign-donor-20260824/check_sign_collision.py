#!/usr/bin/env python3
from collections import defaultdict


def complement_sandwich_add(width: int, source: int, target: int, sign: int) -> int:
    mask = (1 << width) - 1
    sign_mask = mask if sign else 0
    return (((target ^ sign_mask) + source) & mask) ^ sign_mask


def halving_wire_permutation(width: int, value: int) -> int:
    bits = [(value >> i) & 1 for i in range(width)]
    for i in range(width - 1):
        bits[i], bits[i + 1] = bits[i + 1], bits[i]
    bits[width - 1] ^= bits[width - 2]
    return sum(bit << i for i, bit in enumerate(bits))


def walk(width: int, source: int, target: int) -> tuple[int, int]:
    assert source & 1 and target & 1
    sign = ((target >> 1) ^ (source >> 1)) & 1
    summed = complement_sandwich_add(width, source, target, sign)
    return sign, halving_wire_permutation(width, summed)


def main() -> None:
    witness_width = 259
    witness = [(target, *walk(witness_width, 1, target)) for target in (1, 3)]
    assert witness == [(1, 0, 1), (3, 1, 1)], witness
    print("actual_width=259 witness_source=1 branches=" + repr(witness))

    total_inputs = 0
    total_collision_keys = 0
    for width in range(4, 11):
        buckets: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
        for source in range(1, 1 << width, 2):
            for target in range(1, 1 << width, 2):
                sign, post = walk(width, source, target)
                assert post & 1 == 1
                assert ((post >> (width - 1)) & 1) == ((post >> (width - 2)) & 1)
                buckets[(source, post)].append((target, sign))

        expected_keys = 1 << (2 * width - 3)
        assert len(buckets) == expected_keys
        assert all(len(preimages) == 2 for preimages in buckets.values())
        assert all({sign for _, sign in preimages} == {0, 1} for preimages in buckets.values())
        inputs = 1 << (2 * width - 2)
        total_inputs += inputs
        total_collision_keys += len(buckets)
        print(
            f"width={width} inputs={inputs} post_keys={len(buckets)} "
            f"preimages_per_key=2 signs_per_key=0,1"
        )

    print(
        f"PASS total_inputs={total_inputs} total_collision_keys={total_collision_keys} "
        "sign_is_not_a_function_of_post_walk_state=true"
    )


if __name__ == "__main__":
    main()
