pub(crate) fn divide_peak_binding_round(after_round: usize) -> bool {
    matches!(
        after_round,
        334..=370
            | 372
            | 502
            | 504
            | 506
            | 508
            | 510..=541
            | 543
            | 545
            | 609
            | 611
            | 613
            | 615..=644
    )
}

pub(crate) fn multiply_peak_binding_round(after_round: usize) -> bool {
    matches!(
        after_round,
        318
            | 320
            | 322..=367
            | 369
            | 495
            | 497
            | 501..=538
            | 540
            | 608..=637
            | 639
            | 641
            | 643
    )
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum BitOnePassenger {
    U,
    V,
}

pub(crate) fn fourth_passenger(after_round: usize) -> BitOnePassenger {
    if after_round % 2 == 0 {
        BitOnePassenger::U
    } else {
        BitOnePassenger::V
    }
}

pub(crate) fn fourth_tape_control_indices(
    after_round: usize,
    tape_len: usize,
) -> Result<std::ops::RangeInclusive<usize>, &'static str> {
    if after_round == 0 {
        return Err("fourth passenger is seeded only after fused round 1");
    }
    if tape_len != after_round + 1 {
        return Err("fourth passenger requires the exact post-round sign tape");
    }
    Ok(1..=after_round)
}

pub(crate) fn fourth_feature_enabled(
    fourth_flag: Option<&str>,
    third_flag: Option<&str>,
    divide: bool,
    after_round: usize,
) -> Result<bool, &'static str> {
    if fourth_flag != Some("1") {
        return Ok(false);
    }
    let binding = if divide {
        divide_peak_binding_round(after_round)
    } else {
        multiply_peak_binding_round(after_round)
    };
    if !binding {
        return Ok(false);
    }
    if third_flag != Some("1") {
        return Err("SUB4_PP_FOURTH_PASSENGER=1 requires SUB4_PP_THIRD_PASSENGER=1");
    }
    Ok(true)
}

#[cfg(test)]
mod tests {
    use super::{
        divide_peak_binding_round, fourth_feature_enabled, fourth_passenger,
        fourth_tape_control_indices, multiply_peak_binding_round, BitOnePassenger,
    };

    #[test]
    fn exact_232_peak_binding_rounds_are_selected() {
        let divide_expected: Vec<usize> = (334..=370)
            .chain([372, 502, 504, 506, 508])
            .chain(510..=541)
            .chain([543, 545, 609, 611, 613])
            .chain(615..=644)
            .collect();
        let multiply_expected: Vec<usize> = [318, 320]
            .into_iter()
            .chain(322..=367)
            .chain([369, 495, 497])
            .chain(501..=538)
            .chain([540])
            .chain(608..=637)
            .chain([639, 641, 643])
            .collect();

        let divide_selected: Vec<usize> = (314..=645)
            .filter(|&round| divide_peak_binding_round(round))
            .collect();
        let multiply_selected: Vec<usize> = (314..=645)
            .filter(|&round| multiply_peak_binding_round(round))
            .collect();

        assert_eq!(divide_selected, divide_expected);
        assert_eq!(multiply_selected, multiply_expected);
        assert_eq!(divide_selected.len(), 109);
        assert_eq!(multiply_selected.len(), 123);
        assert_eq!(divide_selected.len() + multiply_selected.len(), 232);
    }

    #[test]
    fn out_of_window_and_gap_rounds_are_rejected() {
        for round in [
            0,
            313,
            371,
            373,
            501,
            503,
            509,
            542,
            544,
            608,
            610,
            612,
            614,
            645,
            646,
            usize::MAX,
        ] {
            assert!(!divide_peak_binding_round(round), "divide round {round}");
        }
        for round in [
            0,
            313,
            314,
            317,
            319,
            321,
            368,
            370,
            494,
            496,
            498,
            500,
            539,
            541,
            607,
            638,
            640,
            642,
            644,
            645,
            646,
            usize::MAX,
        ] {
            assert!(
                !multiply_peak_binding_round(round),
                "multiply round {round}"
            );
        }
    }

    #[test]
    fn fourth_feature_selects_exactly_the_232_third_passenger_cells() {
        let divide_selected: Vec<usize> = (0..=646)
            .filter(|&round| {
                fourth_feature_enabled(Some("1"), Some("1"), true, round)
                    .expect("valid divide precondition")
            })
            .collect();
        let multiply_selected: Vec<usize> = (0..=646)
            .filter(|&round| {
                fourth_feature_enabled(Some("1"), Some("1"), false, round)
                    .expect("valid multiply precondition")
            })
            .collect();

        assert_eq!(divide_selected.len(), 109);
        assert_eq!(multiply_selected.len(), 123);
        assert_eq!(divide_selected.len() + multiply_selected.len(), 232);
        assert!(divide_selected
            .iter()
            .all(|&round| divide_peak_binding_round(round)));
        assert!(multiply_selected
            .iter()
            .all(|&round| multiply_peak_binding_round(round)));
    }

    #[test]
    fn fourth_feature_is_exact_literal_and_requires_third_on_binding_cells() {
        for fourth in [None, Some(""), Some("0"), Some("01"), Some("true"), Some("invalid")] {
            assert_eq!(
                fourth_feature_enabled(fourth, None, true, 334),
                Ok(false),
                "fourth={fourth:?}"
            );
        }

        for third in [None, Some(""), Some("0"), Some("01"), Some("true"), Some("invalid")] {
            assert!(
                fourth_feature_enabled(Some("1"), third, true, 334).is_err(),
                "third={third:?}"
            );
        }

        assert_eq!(
            fourth_feature_enabled(Some("1"), None, true, 333),
            Ok(false),
            "a nonbinding call remains dormant before checking the precondition"
        );
        assert_eq!(
            fourth_feature_enabled(Some("1"), Some("1"), true, 334),
            Ok(true)
        );
    }

    #[test]
    fn fourth_passenger_is_distinct_from_third_for_both_parities() {
        assert_eq!(fourth_passenger(318), BitOnePassenger::U);
        assert_eq!(fourth_passenger(319), BitOnePassenger::V);

        let third_even = BitOnePassenger::V;
        let third_odd = BitOnePassenger::U;
        assert_ne!(fourth_passenger(318), third_even);
        assert_ne!(fourth_passenger(319), third_odd);
    }

    #[test]
    fn fourth_tape_fan_in_clears_and_restores_for_both_parities() {
        for after_round in 1..=8 {
            let width = after_round;
            for pattern in 0usize..(1usize << width) {
                let mut tape = vec![0u8; after_round + 1];
                for index in 1..=after_round {
                    tape[index] = ((pattern >> (index - 1)) & 1) as u8;
                }
                let original = 1u8 ^ tape[1..].iter().copied().fold(0, |a, b| a ^ b);
                let controls = fourth_tape_control_indices(after_round, tape.len())
                    .expect("exact post-round tape length");

                let mut cleared = original ^ 1;
                for index in controls.clone() {
                    cleared ^= tape[index];
                }
                assert_eq!(cleared, 0, "round={after_round} pattern={pattern}");

                let mut restored = cleared;
                for index in controls.rev() {
                    restored ^= tape[index];
                }
                restored ^= 1;
                assert_eq!(restored, original, "round={after_round} pattern={pattern}");

                let expected = if after_round % 2 == 0 {
                    BitOnePassenger::U
                } else {
                    BitOnePassenger::V
                };
                assert_eq!(fourth_passenger(after_round), expected);
            }
        }
    }

    #[test]
    fn fourth_tape_range_rejects_round_zero_and_mismatched_lengths() {
        assert!(fourth_tape_control_indices(0, 1).is_err());
        assert!(fourth_tape_control_indices(334, 334).is_err());
        assert!(fourth_tape_control_indices(334, 336).is_err());
        assert_eq!(
            fourth_tape_control_indices(334, 335)
                .expect("valid range")
                .collect::<Vec<_>>(),
            (1..=334).collect::<Vec<_>>()
        );
    }
}
