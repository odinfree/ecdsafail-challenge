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

#[cfg(test)]
mod tests {
    use super::{divide_peak_binding_round, multiply_peak_binding_round};

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
}
