use std::collections::HashMap;
use std::ops::{Deref, Index};
use std::sync::atomic::{AtomicU64, Ordering};

use crate::circuit::{Op, OperationType, QubitId, NO_BIT, NO_QUBIT, NO_REG};

use super::current_trace_context;

pub(crate) const ORIGIN_SYNTHETIC_TAIL: u16 = 1;
pub(crate) const ORIGIN_TAIL_NONCE_REWRITTEN: u16 = 2;
pub(crate) const ORIGIN_EMIT_INVERSE: u16 = 4;
const KNOWN_ORIGIN_FLAGS: u16 =
    ORIGIN_SYNTHETIC_TAIL | ORIGIN_TAIL_NONCE_REWRITTEN | ORIGIN_EMIT_INVERSE;

pub(crate) fn j3_dead_gate_audit_value_is_enabled(value: Option<&str>) -> bool {
    value == Some("1")
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
pub(crate) struct OriginRef {
    pub(crate) site_id: u32,
    pub(crate) emission_ordinal: u32,
    pub(crate) inverse_depth: u16,
    pub(crate) flags: u16,
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub(crate) struct SourceLiteralMetadata {
    pub(crate) key: u16,
    pub(crate) value: u32,
}

impl SourceLiteralMetadata {
    pub(crate) const NONE: Self = Self { key: 0, value: 0 };

    pub(crate) fn validate(self) -> Result<(), &'static str> {
        if self.key == 0 && self.value != 0 {
            return Err("source literal metadata has a value without a key");
        }
        Ok(())
    }

    pub(crate) fn validate_explicit(self) -> Result<(), &'static str> {
        self.validate()?;
        if self == Self::NONE {
            return Err("exact source predicate requires explicit literal metadata");
        }
        Ok(())
    }

    pub(crate) fn is_explicit(self) -> bool {
        self.key != 0
    }
}

impl OriginRef {
    pub(crate) fn try_validate_transform_chain(self) -> Result<(), &'static str> {
        if self.flags & !KNOWN_ORIGIN_FLAGS != 0 {
            return Err("unknown provenance transform flags");
        }
        if (self.inverse_depth != 0) != (self.flags & ORIGIN_EMIT_INVERSE != 0) {
            return Err("inverse provenance depth/flag disagreement");
        }
        Ok(())
    }

    fn validate_transform_chain(self) {
        if let Err(message) = self.try_validate_transform_chain() {
            panic!("{message}");
        }
    }

    fn transform_chain_components(self) -> Vec<&'static str> {
        self.validate_transform_chain();

        let mut components = Vec::with_capacity(
            usize::from(self.inverse_depth)
                + usize::from(self.flags & ORIGIN_SYNTHETIC_TAIL != 0)
                + usize::from(self.flags & ORIGIN_TAIL_NONCE_REWRITTEN != 0),
        );
        components.extend(std::iter::repeat_n(
            "emit_inverse",
            usize::from(self.inverse_depth),
        ));
        if self.flags & ORIGIN_SYNTHETIC_TAIL != 0 {
            components.push("synthetic_tail");
        }
        if self.flags & ORIGIN_TAIL_NONCE_REWRITTEN != 0 {
            components.push("tail_nonce_rewritten");
        }
        components
    }

    pub(crate) fn transform_chain(self) -> String {
        let components = self.transform_chain_components();
        if components.is_empty() {
            "-".to_owned()
        } else {
            components.join(">")
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct SourceSite {
    pub(crate) file: &'static str,
    pub(crate) line: u32,
    pub(crate) trace_context: u32,
    pub(crate) source_literal: SourceLiteralMetadata,
}

pub(crate) struct SyntheticTailSuffix {
    owner_generation: u64,
    ticket: u64,
    start: usize,
    len: usize,
}

struct PendingSyntheticTail {
    ticket: u64,
    start: usize,
    len: usize,
}

static NEXT_OWNER_GENERATION: AtomicU64 = AtomicU64::new(1);

fn next_owner_generation_from(generation: &AtomicU64) -> u64 {
    generation
        .fetch_update(Ordering::Relaxed, Ordering::Relaxed, |current| {
            current.checked_add(1)
        })
        .expect("TracedOps owner generation exhausted")
}

fn next_owner_generation() -> u64 {
    next_owner_generation_from(&NEXT_OWNER_GENERATION)
}

fn is_canonical_synthetic_tail_x(op: &Op) -> bool {
    op.kind == OperationType::X
        && op.q_control2 == NO_QUBIT
        && op.q_control1 == NO_QUBIT
        && op.q_target != NO_QUBIT
        && op.c_target == NO_BIT
        && op.c_condition == NO_BIT
        && op.r_target == NO_REG
}

pub(crate) struct TracedOps {
    ops: Vec<Op>,
    origins: Vec<OriginRef>,
    sites: Vec<SourceSite>,
    site_ids: HashMap<(&'static str, u32, u32, SourceLiteralMetadata), u32>,
    next_emission_ordinal: u32,
    enabled: bool,
    owner_generation: u64,
    next_synthetic_tail_ticket: u64,
    pending_synthetic_tail: Option<PendingSyntheticTail>,
}

impl Clone for TracedOps {
    fn clone(&self) -> Self {
        Self {
            ops: self.ops.clone(),
            origins: self.origins.clone(),
            sites: self.sites.clone(),
            site_ids: self.site_ids.clone(),
            next_emission_ordinal: self.next_emission_ordinal,
            enabled: self.enabled,
            owner_generation: next_owner_generation(),
            next_synthetic_tail_ticket: 1,
            pending_synthetic_tail: None,
        }
    }
}

impl TracedOps {
    pub(crate) fn new(enabled: bool) -> Self {
        Self {
            ops: Vec::new(),
            origins: Vec::new(),
            sites: Vec::new(),
            site_ids: HashMap::new(),
            next_emission_ordinal: 0,
            enabled,
            owner_generation: next_owner_generation(),
            next_synthetic_tail_ticket: 1,
            pending_synthetic_tail: None,
        }
    }

    pub(crate) fn enabled(&self) -> bool {
        self.enabled
    }

    pub(crate) fn len(&self) -> usize {
        self.ops.len()
    }

    pub(crate) fn is_empty(&self) -> bool {
        self.ops.is_empty()
    }

    pub(crate) fn iter(&self) -> std::slice::Iter<'_, Op> {
        self.ops.iter()
    }

    pub(crate) fn origins(&self) -> &[OriginRef] {
        &self.origins
    }

    pub(crate) fn sites(&self) -> &[SourceSite] {
        &self.sites
    }

    pub(crate) fn to_vec(&self) -> Vec<Op> {
        self.ops.clone()
    }

    pub(crate) fn into_ops(self) -> Vec<Op> {
        self.ops
    }

    pub(crate) fn take(&mut self) -> Self {
        let enabled = self.enabled;
        std::mem::replace(self, Self::new(enabled))
    }

    #[track_caller]
    pub(crate) fn push(&mut self, op: Op) {
        let caller = std::panic::Location::caller();
        self.push_at(
            op,
            caller.file(),
            caller.line(),
            current_trace_context(),
            0,
            0,
        );
    }

    pub(crate) fn push_at(
        &mut self,
        op: Op,
        file: &'static str,
        line: u32,
        trace_context: u32,
        inverse_depth: u16,
        flags: u16,
    ) {
        self.push_at_with_source_literal(
            op,
            file,
            line,
            trace_context,
            inverse_depth,
            flags,
            SourceLiteralMetadata::NONE,
        );
    }

    pub(crate) fn push_at_with_source_literal(
        &mut self,
        op: Op,
        file: &'static str,
        line: u32,
        trace_context: u32,
        inverse_depth: u16,
        flags: u16,
        source_literal: SourceLiteralMetadata,
    ) {
        self.pending_synthetic_tail = None;
        if self.enabled {
            let emission_ordinal = self.next_emission_ordinal;
            let next_emission_ordinal = emission_ordinal
                .checked_add(1)
                .expect("provenance emission ordinal exceeds u32");
            let key = (file, line, trace_context, source_literal);
            let (site_id, new_site) = if let Some(&site_id) = self.site_ids.get(&key) {
                (site_id, None)
            } else {
                let site_id =
                    u32::try_from(self.sites.len()).expect("provenance site count exceeds u32");
                (
                    site_id,
                    Some(SourceSite {
                        file,
                        line,
                        trace_context,
                        source_literal,
                    }),
                )
            };
            let origin = OriginRef {
                site_id,
                emission_ordinal,
                inverse_depth,
                flags,
            };
            origin.validate_transform_chain();
            if let Some(site) = new_site {
                self.sites.push(site);
                self.site_ids.insert(key, site_id);
            }
            self.next_emission_ordinal = next_emission_ordinal;
            self.ops.push(op);
            self.origins.push(origin);
        } else {
            self.ops.push(op);
        }
        self.assert_paired();
    }

    pub(crate) fn push_inherited(&mut self, op: Op, mut origin: OriginRef) {
        self.pending_synthetic_tail = None;
        origin.inverse_depth = origin
            .inverse_depth
            .checked_add(1)
            .expect("inverse provenance depth overflow");
        origin.flags |= ORIGIN_EMIT_INVERSE;
        if self.enabled {
            origin.validate_transform_chain();
        }
        self.ops.push(op);
        if self.enabled {
            self.origins.push(origin);
        }
        self.assert_paired();
    }

    #[track_caller]
    pub(crate) fn append_synthetic_tail(
        &mut self,
        ops: &[Op],
    ) -> Result<SyntheticTailSuffix, String> {
        let caller = std::panic::Location::caller();
        self.append_synthetic_tail_at(ops, caller.file(), caller.line(), current_trace_context())
    }

    pub(crate) fn append_synthetic_tail_at(
        &mut self,
        ops: &[Op],
        file: &'static str,
        line: u32,
        trace_context: u32,
    ) -> Result<SyntheticTailSuffix, String> {
        if self.pending_synthetic_tail.is_some() {
            return Err("a synthetic tail rewrite is already pending".to_owned());
        }
        if ops.is_empty() {
            return Err("synthetic tail is empty".to_owned());
        }
        if ops.iter().any(|op| !is_canonical_synthetic_tail_x(op)) {
            return Err("synthetic tail contains a non-canonical X operation".to_owned());
        }
        let start = self.ops.len();
        start
            .checked_add(ops.len())
            .ok_or_else(|| "synthetic tail length overflows usize".to_owned())?;
        let ticket = self.next_synthetic_tail_ticket;
        let next_ticket = ticket
            .checked_add(1)
            .ok_or_else(|| "synthetic tail capability tickets exhausted".to_owned())?;
        if self.enabled {
            let append_count = u32::try_from(ops.len())
                .map_err(|_| "synthetic tail length exceeds u32".to_owned())?;
            self.next_emission_ordinal
                .checked_add(append_count)
                .ok_or_else(|| "synthetic tail emission ordinals exceed u32".to_owned())?;
        }
        self.ops
            .try_reserve(ops.len())
            .map_err(|error| format!("cannot reserve synthetic tail operations: {error}"))?;
        if self.enabled {
            self.origins
                .try_reserve(ops.len())
                .map_err(|error| format!("cannot reserve synthetic tail origins: {error}"))?;
            let key = (file, line, trace_context, SourceLiteralMetadata::NONE);
            if !self.site_ids.contains_key(&key) {
                self.sites.try_reserve(1).map_err(|error| {
                    format!("cannot reserve synthetic tail source site: {error}")
                })?;
                self.site_ids.try_reserve(1).map_err(|error| {
                    format!("cannot reserve synthetic tail site index: {error}")
                })?;
            }
        }

        for op in ops.iter().copied() {
            self.push_at(op, file, line, trace_context, 0, ORIGIN_SYNTHETIC_TAIL);
        }
        self.next_synthetic_tail_ticket = next_ticket;
        self.pending_synthetic_tail = Some(PendingSyntheticTail {
            ticket,
            start,
            len: ops.len(),
        });
        Ok(SyntheticTailSuffix {
            owner_generation: self.owner_generation,
            ticket,
            start,
            len: ops.len(),
        })
    }

    pub(crate) fn rewrite_synthetic_tail_targets(
        &mut self,
        tail: SyntheticTailSuffix,
        targets: &[QubitId],
    ) -> Result<(), String> {
        if tail.owner_generation != self.owner_generation {
            return Err(
                "synthetic tail capability belongs to a different operation stream".to_owned(),
            );
        }
        let Some(pending) = self.pending_synthetic_tail.as_ref() else {
            return Err("synthetic tail capability is not pending".to_owned());
        };
        if pending.ticket != tail.ticket || pending.start != tail.start || pending.len != tail.len {
            return Err("synthetic tail capability does not match the pending suffix".to_owned());
        }
        self.pending_synthetic_tail = None;

        if targets.len() != tail.len {
            return Err(format!(
                "synthetic tail target count mismatch: {} targets, {} operations",
                targets.len(),
                tail.len
            ));
        }
        let end = tail
            .start
            .checked_add(tail.len)
            .ok_or_else(|| "synthetic tail handle overflows usize".to_owned())?;
        if end != self.ops.len() {
            return Err("synthetic tail handle is not the complete operation suffix".to_owned());
        }
        if targets.iter().any(|target| *target == NO_QUBIT) {
            return Err("synthetic tail rewrite contains a missing qubit target".to_owned());
        }
        if self.ops[tail.start..end]
            .iter()
            .any(|op| !is_canonical_synthetic_tail_x(op))
        {
            return Err("synthetic tail suffix contains a non-canonical X operation".to_owned());
        }
        if self.enabled {
            self.assert_paired();
            let first_origin = self.origins[tail.start];
            for (offset, origin) in self.origins[tail.start..end].iter().copied().enumerate() {
                let expected_ordinal = first_origin
                    .emission_ordinal
                    .checked_add(offset as u32)
                    .ok_or_else(|| "synthetic tail ordinal sequence overflows u32".to_owned())?;
                if origin.site_id != first_origin.site_id
                    || origin.emission_ordinal != expected_ordinal
                    || origin.inverse_depth != 0
                    || origin.flags != ORIGIN_SYNTHETIC_TAIL
                {
                    return Err(
                        "synthetic tail provenance is not a canonical paired suffix".to_owned()
                    );
                }
            }
        }

        for (op, target) in self.ops[tail.start..end]
            .iter_mut()
            .zip(targets.iter().copied())
        {
            op.q_target = target;
        }
        if self.enabled {
            for origin in &mut self.origins[tail.start..end] {
                origin.flags |= ORIGIN_TAIL_NONCE_REWRITTEN;
            }
        }
        self.assert_paired();
        Ok(())
    }

    pub(crate) fn truncate(&mut self, len: usize) {
        self.pending_synthetic_tail = None;
        self.ops.truncate(len);
        if self.enabled {
            self.origins.truncate(len);
        }
        self.assert_paired();
    }

    pub(crate) fn paired_range(&self, start: usize, end: usize) -> Vec<(Op, OriginRef)> {
        assert!(
            self.enabled,
            "paired provenance requested while audit is disabled"
        );
        assert!(
            start <= end && end <= self.ops.len(),
            "invalid provenance range"
        );
        self.assert_paired();
        self.ops[start..end]
            .iter()
            .copied()
            .zip(self.origins[start..end].iter().copied())
            .collect()
    }

    fn assert_paired(&self) {
        if self.enabled {
            assert_eq!(
                self.ops.len(),
                self.origins.len(),
                "operation/provenance length drift"
            );
        } else {
            assert!(
                self.origins.is_empty(),
                "audit-disabled origin sidecar allocated"
            );
        }
    }
}

impl Deref for TracedOps {
    type Target = [Op];

    fn deref(&self) -> &Self::Target {
        &self.ops
    }
}

impl<I> Index<I> for TracedOps
where
    [Op]: Index<I>,
{
    type Output = <[Op] as Index<I>>::Output;

    fn index(&self, index: I) -> &Self::Output {
        &self.ops[..][index]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::circuit::{Op, OperationType};
    use crate::point_add::{emit_inverse, B};
    use std::sync::atomic::AtomicU64;

    fn op(kind: OperationType) -> Op {
        let mut op = Op::empty();
        op.kind = kind;
        op
    }

    fn audited_builder() -> B {
        let mut builder = B::new_for_test();
        builder.ops = TracedOps::new(true);
        builder
    }

    fn canonical_tail(target: QubitId) -> [Op; 2] {
        let mut tail = [op(OperationType::X), op(OperationType::X)];
        tail[0].q_target = target;
        tail[1].q_target = target;
        tail
    }

    fn x(target: QubitId) -> Op {
        let mut operation = op(OperationType::X);
        operation.q_target = target;
        operation
    }

    fn rewritten_nonce_fixture(enabled: bool) -> TracedOps {
        let mut builder = B::new_for_test();
        builder.ops = TracedOps::new(enabled);
        emit_inverse(&mut builder, |builder| builder.push_op(x(QubitId(9))));

        let mut stream = builder.ops.take();
        let mut targets = [QubitId(0); 96];
        for bit in 0usize..48 {
            let target = if bit.is_multiple_of(2) {
                QubitId(1)
            } else {
                QubitId(0)
            };
            targets[2 * bit] = target;
            targets[2 * bit + 1] = target;
        }
        let tail = stream
            .append_synthetic_tail(&[x(QubitId(0)); 96])
            .expect("append exact synthetic tail");
        stream
            .rewrite_synthetic_tail_targets(tail, &targets)
            .expect("rewrite exact synthetic tail");
        stream
    }

    fn forge_synthetic_tail(tail: &SyntheticTailSuffix) -> SyntheticTailSuffix {
        SyntheticTailSuffix {
            owner_generation: tail.owner_generation,
            ticket: tail.ticket,
            start: tail.start,
            len: tail.len,
        }
    }

    fn snapshot(traced: &TracedOps) -> (Vec<Op>, Vec<OriginRef>, Vec<SourceSite>) {
        (
            traced.to_vec(),
            traced.origins().to_vec(),
            traced.sites().to_vec(),
        )
    }

    #[test]
    fn origin_ref_is_twelve_bytes() {
        assert_eq!(std::mem::size_of::<OriginRef>(), 12);
    }

    #[test]
    fn stream_owner_generations_are_unique_and_overflow_fails_closed() {
        let first = TracedOps::new(false);
        let second = TracedOps::new(false);
        assert_ne!(first.owner_generation, second.owner_generation);

        let exhausted = AtomicU64::new(u64::MAX);
        assert!(std::panic::catch_unwind(|| next_owner_generation_from(&exhausted)).is_err());
        assert_eq!(
            exhausted.load(std::sync::atomic::Ordering::Relaxed),
            u64::MAX
        );
    }

    #[test]
    fn push_keeps_operation_and_origin_lengths_equal() {
        let mut traced = TracedOps::new(true);
        traced.push_at(op(OperationType::X), "first.rs", 11, 7, 0, 0);
        traced.push_at(op(OperationType::Z), "second.rs", 22, 8, 0, 0);
        traced.push_at(op(OperationType::CX), "first.rs", 11, 7, 0, 0);

        assert_eq!(traced.len(), 3);
        assert_eq!(traced.origins().len(), traced.len());
        assert_eq!(
            traced.sites(),
            &[
                SourceSite {
                    file: "first.rs",
                    line: 11,
                    trace_context: 7,
                    source_literal: SourceLiteralMetadata::NONE,
                },
                SourceSite {
                    file: "second.rs",
                    line: 22,
                    trace_context: 8,
                    source_literal: SourceLiteralMetadata::NONE,
                },
            ]
        );
        assert_eq!(
            traced
                .origins()
                .iter()
                .map(|origin| (origin.site_id, origin.emission_ordinal))
                .collect::<Vec<_>>(),
            vec![(0, 0), (1, 1), (0, 2)]
        );
    }

    #[test]
    fn raw_public_push_records_its_real_caller() {
        let mut traced = TracedOps::new(true);
        let expected_line = line!() + 1;
        traced.push(op(OperationType::X));

        assert_eq!(
            traced.sites(),
            &[SourceSite {
                file: file!(),
                line: expected_line,
                trace_context: 0,
                source_literal: SourceLiteralMetadata::NONE,
            }]
        );
        assert_eq!(
            traced.origins(),
            &[OriginRef {
                site_id: 0,
                emission_ordinal: 0,
                inverse_depth: 0,
                flags: 0,
            }]
        );
    }

    #[test]
    fn truncate_removes_matching_origins() {
        let mut traced = TracedOps::new(true);
        traced.push_at(op(OperationType::X), "one.rs", 1, 10, 0, 0);
        traced.push_at(op(OperationType::Z), "two.rs", 2, 20, 0, 0);
        traced.push_at(op(OperationType::CX), "three.rs", 3, 30, 0, 0);

        traced.truncate(1);

        assert_eq!(traced.len(), 1);
        assert_eq!(traced.origins().len(), 1);
        assert_eq!(traced[0].kind, OperationType::X);
        assert_eq!(traced.origins()[0].emission_ordinal, 0);
    }

    #[test]
    fn take_returns_empty_buffer_and_complete_stream() {
        let mut traced = TracedOps::new(true);
        traced.push_at(op(OperationType::X), "one.rs", 1, 10, 0, 0);
        traced.push_at(
            op(OperationType::Z),
            "two.rs",
            2,
            20,
            1,
            ORIGIN_EMIT_INVERSE | ORIGIN_SYNTHETIC_TAIL,
        );

        let taken = traced.take();

        assert!(traced.is_empty());
        assert!(traced.origins().is_empty());
        assert!(traced.sites().is_empty());
        assert!(traced.site_ids.is_empty());
        assert_eq!(traced.next_emission_ordinal, 0);
        assert_eq!(
            taken
                .iter()
                .map(|operation| operation.kind)
                .collect::<Vec<_>>(),
            vec![OperationType::X, OperationType::Z]
        );
        assert_eq!(
            taken.sites(),
            &[
                SourceSite {
                    file: "one.rs",
                    line: 1,
                    trace_context: 10,
                    source_literal: SourceLiteralMetadata::NONE,
                },
                SourceSite {
                    file: "two.rs",
                    line: 2,
                    trace_context: 20,
                    source_literal: SourceLiteralMetadata::NONE,
                },
            ]
        );
        assert_eq!(
            taken.origins(),
            &[
                OriginRef {
                    site_id: 0,
                    emission_ordinal: 0,
                    inverse_depth: 0,
                    flags: 0,
                },
                OriginRef {
                    site_id: 1,
                    emission_ordinal: 1,
                    inverse_depth: 1,
                    flags: ORIGIN_EMIT_INVERSE | ORIGIN_SYNTHETIC_TAIL,
                },
            ]
        );
        assert_eq!(taken.next_emission_ordinal, 2);

        traced.push_at(op(OperationType::CX), "three.rs", 3, 30, 0, 0);
        assert_eq!(traced.origins()[0].emission_ordinal, 0);
    }

    #[test]
    fn audit_disabled_sidecars_stay_empty_through_push_truncate_and_take() {
        let mut traced = TracedOps::new(false);
        traced.push_at(op(OperationType::X), "one.rs", 1, 10, 0, 0);
        traced.push_at(op(OperationType::Z), "two.rs", 2, 20, 0, 0);
        assert!(traced.origins().is_empty());
        assert!(traced.sites().is_empty());
        assert!(traced.site_ids.is_empty());
        assert_eq!(traced.next_emission_ordinal, 0);

        traced.truncate(1);
        assert_eq!(traced.len(), 1);
        assert!(traced.origins().is_empty());
        assert!(traced.sites().is_empty());
        assert!(traced.site_ids.is_empty());
        assert_eq!(traced.next_emission_ordinal, 0);

        let taken = traced.take();
        assert!(traced.is_empty());
        assert!(traced.origins().is_empty());
        assert!(traced.sites().is_empty());
        assert_eq!(
            taken
                .iter()
                .map(|operation| operation.kind)
                .collect::<Vec<_>>(),
            vec![OperationType::X]
        );
        assert!(taken.origins().is_empty());
        assert!(taken.sites().is_empty());
        assert!(taken.site_ids.is_empty());
        assert_eq!(taken.next_emission_ordinal, 0);
    }

    #[test]
    fn audit_flag_requires_exact_string_one() {
        assert!(j3_dead_gate_audit_value_is_enabled(Some("1")));
        for value in [
            None,
            Some(""),
            Some("0"),
            Some("01"),
            Some("true"),
            Some(" 1"),
            Some("1 "),
        ] {
            assert!(
                !j3_dead_gate_audit_value_is_enabled(value),
                "unexpected audit enable for {value:?}"
            );
        }
    }

    #[test]
    fn inverse_and_nonce_tail_have_total_provenance() {
        let stream = rewritten_nonce_fixture(true);
        assert_eq!(stream.origins().len(), stream.len());
        assert_eq!(stream.len(), 97);
        assert_eq!(stream.origins()[0].inverse_depth, 1);
        assert_eq!(stream.origins()[0].flags, ORIGIN_EMIT_INVERSE);
        assert!(stream.origins()[1..].iter().all(|origin| {
            origin.flags == (ORIGIN_SYNTHETIC_TAIL | ORIGIN_TAIL_NONCE_REWRITTEN)
        }));
    }

    #[test]
    fn nonce_tail_has_96_synthetic_origins() {
        let stream = rewritten_nonce_fixture(true);
        assert_eq!(
            stream
                .origins()
                .iter()
                .filter(|origin| origin.flags & ORIGIN_SYNTHETIC_TAIL != 0)
                .count(),
            96
        );
    }

    #[test]
    fn nonce_rewrite_preserves_sites_and_adds_only_rewrite_flag() {
        let mut stream = TracedOps::new(true);
        let tail = stream
            .append_synthetic_tail(&[x(QubitId(0)); 96])
            .expect("append exact synthetic tail");
        let before = stream.origins().to_vec();
        let targets = [QubitId(7); 96];
        stream
            .rewrite_synthetic_tail_targets(tail, &targets)
            .expect("rewrite exact synthetic tail");

        for (before, after) in before.iter().zip(stream.origins()) {
            assert_eq!(
                OriginRef {
                    flags: before.flags | ORIGIN_TAIL_NONCE_REWRITTEN,
                    ..*before
                },
                *after
            );
        }
    }

    #[test]
    fn emit_inverse_inherits_forward_site_and_reverses_origins() {
        let mut builder = audited_builder();
        let x_line = line!() + 3;
        let z_line = line!() + 3;
        emit_inverse(&mut builder, |builder| {
            builder.push_op(op(OperationType::X));
            builder.push_op(op(OperationType::Z));
        });

        assert_eq!(
            builder.ops.iter().map(|op| op.kind).collect::<Vec<_>>(),
            vec![OperationType::Z, OperationType::X]
        );
        assert_eq!(
            builder.ops.sites(),
            &[
                SourceSite {
                    file: file!(),
                    line: x_line,
                    trace_context: 0,
                    source_literal: SourceLiteralMetadata::NONE,
                },
                SourceSite {
                    file: file!(),
                    line: z_line,
                    trace_context: 0,
                    source_literal: SourceLiteralMetadata::NONE,
                },
            ]
        );
        assert_eq!(
            builder.ops.origins(),
            &[
                OriginRef {
                    site_id: 1,
                    emission_ordinal: 1,
                    inverse_depth: 1,
                    flags: ORIGIN_EMIT_INVERSE,
                },
                OriginRef {
                    site_id: 0,
                    emission_ordinal: 0,
                    inverse_depth: 1,
                    flags: ORIGIN_EMIT_INVERSE,
                },
            ]
        );
    }

    #[test]
    fn emit_inverse_drops_reset_and_annotation_origins_with_their_ops() {
        let mut builder = audited_builder();
        let x_line = line!() + 3;
        emit_inverse(&mut builder, |builder| {
            builder.push_op(op(OperationType::Register));
            builder.push_op(op(OperationType::X));
            builder.push_op(op(OperationType::R));
            builder.push_op(op(OperationType::AppendToRegister));
            builder.push_op(op(OperationType::DebugPrint));
        });

        assert_eq!(builder.ops.len(), 1);
        assert_eq!(builder.ops.origins().len(), 1);
        assert_eq!(builder.ops[0].kind, OperationType::X);
        let origin = builder.ops.origins()[0];
        assert_eq!(builder.ops.sites()[origin.site_id as usize].line, x_line);
        assert_eq!(origin.emission_ordinal, 1);
        assert_eq!(origin.inverse_depth, 1);
        assert_eq!(origin.flags, ORIGIN_EMIT_INVERSE);
    }

    #[test]
    fn nested_emit_inverse_increments_depth_without_duplicate_ordinals() {
        let mut builder = audited_builder();
        emit_inverse(&mut builder, |builder| {
            emit_inverse(builder, |builder| {
                builder.push_op(op(OperationType::X));
                builder.push_op(op(OperationType::Z));
            });
        });

        assert_eq!(
            builder.ops.iter().map(|op| op.kind).collect::<Vec<_>>(),
            vec![OperationType::X, OperationType::Z]
        );
        assert_eq!(
            builder
                .ops
                .origins()
                .iter()
                .map(|origin| origin.emission_ordinal)
                .collect::<Vec<_>>(),
            vec![0, 1]
        );
        assert!(builder
            .ops
            .origins()
            .iter()
            .all(|origin| origin.inverse_depth == 2 && origin.flags == ORIGIN_EMIT_INVERSE));
    }

    #[test]
    fn inverse_filtering_never_reuses_emission_ordinals() {
        let mut builder = audited_builder();
        emit_inverse(&mut builder, |builder| {
            builder.push_op(op(OperationType::Register));
            builder.push_op(op(OperationType::X));
        });
        builder.push_op(op(OperationType::Z));
        builder.push_op(op(OperationType::CX));

        assert_eq!(
            builder
                .ops
                .origins()
                .iter()
                .map(|origin| origin.emission_ordinal)
                .collect::<Vec<_>>(),
            vec![1, 2, 3]
        );
        assert_eq!(builder.ops.next_emission_ordinal, 4);
    }

    #[test]
    fn nested_inverse_filtering_never_reuses_emission_ordinals() {
        let mut builder = audited_builder();
        emit_inverse(&mut builder, |builder| {
            emit_inverse(builder, |builder| {
                builder.push_op(op(OperationType::Register));
                builder.push_op(op(OperationType::X));
            });
        });
        builder.push_op(op(OperationType::Z));

        assert_eq!(
            builder
                .ops
                .origins()
                .iter()
                .map(|origin| origin.emission_ordinal)
                .collect::<Vec<_>>(),
            vec![1, 2]
        );
        assert_eq!(builder.ops.origins()[0].inverse_depth, 2);
        assert_eq!(builder.ops.next_emission_ordinal, 3);
    }

    #[test]
    fn synthetic_tail_append_and_rewrite_are_paired_and_preflighted() {
        let mut traced = TracedOps::new(true);
        traced.push_at(op(OperationType::Z), "src/point_add/base.rs", 1, 0, 0, 0);

        let before_invalid = (
            traced.to_vec(),
            traced.origins().to_vec(),
            traced.sites().to_vec(),
        );
        assert!(traced
            .append_synthetic_tail_at(&[op(OperationType::Z)], "src/point_add/tail.rs", 2, 3,)
            .is_err());
        assert_eq!(
            (
                traced.to_vec(),
                traced.origins().to_vec(),
                traced.sites().to_vec(),
            ),
            before_invalid
        );
        let mut malformed_x = op(OperationType::X);
        malformed_x.q_target = QubitId(1);
        malformed_x.c_condition = crate::circuit::BitId(0);
        assert!(traced
            .append_synthetic_tail_at(&[malformed_x], "src/point_add/tail.rs", 2, 3,)
            .is_err());
        assert_eq!(
            (
                traced.to_vec(),
                traced.origins().to_vec(),
                traced.sites().to_vec(),
            ),
            before_invalid
        );

        let tail_ops = canonical_tail(QubitId(4));
        let tail = traced
            .append_synthetic_tail_at(&tail_ops, "src/point_add/tail.rs", 2, 3)
            .expect("append tail");
        traced
            .rewrite_synthetic_tail_targets(tail, &[QubitId(7), QubitId(7)])
            .expect("rewrite tail");
        assert_eq!(traced.len(), 3);
        assert_eq!(traced[1].q_target, QubitId(7));
        assert_eq!(traced[2].q_target, QubitId(7));
        assert!(traced.origins()[1..].iter().all(|origin| {
            origin.inverse_depth == 0
                && origin.flags == (ORIGIN_SYNTHETIC_TAIL | ORIGIN_TAIL_NONCE_REWRITTEN)
        }));
        assert_eq!(
            traced.origins()[1..]
                .iter()
                .map(|origin| origin.emission_ordinal)
                .collect::<Vec<_>>(),
            vec![1, 2]
        );
        let tail_site = &traced.sites()[traced.origins()[1].site_id as usize];
        assert_eq!(tail_site.file, "src/point_add/tail.rs");
        assert_eq!(tail_site.line, 2);
        assert_eq!(tail_site.trace_context, 3);
        assert_eq!(tail_site.source_literal, SourceLiteralMetadata::NONE);
    }

    #[test]
    fn synthetic_tail_rewrite_rejects_a_stale_non_suffix_handle_atomically() {
        let mut traced = TracedOps::new(true);
        let tail_ops = canonical_tail(QubitId(0));
        let tail = traced
            .append_synthetic_tail_at(&tail_ops, "src/point_add/tail.rs", 2, 3)
            .expect("append tail");
        traced.push_at(op(OperationType::X), "src/point_add/later.rs", 3, 4, 0, 0);
        let before = snapshot(&traced);
        assert!(traced
            .rewrite_synthetic_tail_targets(tail, &[QubitId(1), QubitId(1)])
            .is_err());
        assert_eq!(snapshot(&traced), before);
    }

    #[test]
    fn synthetic_tail_rewrite_rejects_same_range_general_replacement_in_both_audit_modes() {
        let mut errors = Vec::new();
        for enabled in [false, true] {
            let mut traced = TracedOps::new(enabled);
            traced.push_at(op(OperationType::Z), "src/point_add/base.rs", 1, 0, 0, 0);
            let stale = traced
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(2)),
                    "src/point_add/tail.rs",
                    2,
                    3,
                )
                .expect("append tail");

            traced.truncate(1);
            for replacement in canonical_tail(QubitId(4)) {
                traced.push_at(replacement, "src/point_add/replacement.rs", 4, 5, 0, 0);
            }
            let replacement = snapshot(&traced);
            let error = traced
                .rewrite_synthetic_tail_targets(stale, &[QubitId(8), QubitId(8)])
                .expect_err("general replacement must invalidate the stale tail capability");

            assert_eq!(snapshot(&traced), replacement, "audit={enabled}");
            errors.push(error);
        }
        assert_eq!(
            errors,
            vec![
                "synthetic tail capability is not pending".to_owned(),
                "synthetic tail capability is not pending".to_owned(),
            ]
        );
    }

    #[test]
    fn every_general_mutation_invalidates_a_pending_synthetic_tail() {
        for enabled in [false, true] {
            let mut after_truncate = TracedOps::new(enabled);
            let truncate_tail = after_truncate
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(1)),
                    "src/point_add/truncate_tail.rs",
                    2,
                    3,
                )
                .expect("append truncate tail");
            after_truncate.truncate(1);
            let truncate_snapshot = snapshot(&after_truncate);
            assert_eq!(
                after_truncate
                    .rewrite_synthetic_tail_targets(truncate_tail, &[QubitId(8), QubitId(8)],)
                    .expect_err("truncate must invalidate the pending tail"),
                "synthetic tail capability is not pending",
                "audit={enabled}"
            );
            assert_eq!(
                snapshot(&after_truncate),
                truncate_snapshot,
                "audit={enabled}"
            );

            let mut after_push = TracedOps::new(enabled);
            let push_tail = after_push
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(1)),
                    "src/point_add/push_tail.rs",
                    4,
                    5,
                )
                .expect("append push tail");
            let mut pushed = op(OperationType::X);
            pushed.q_target = QubitId(3);
            after_push.push_at(pushed, "src/point_add/later.rs", 6, 7, 0, 0);
            let push_snapshot = snapshot(&after_push);
            assert_eq!(
                after_push
                    .rewrite_synthetic_tail_targets(push_tail, &[QubitId(8), QubitId(8)])
                    .expect_err("push must invalidate the pending tail"),
                "synthetic tail capability is not pending",
                "audit={enabled}"
            );
            assert_eq!(snapshot(&after_push), push_snapshot, "audit={enabled}");

            let mut after_inherited = TracedOps::new(enabled);
            let inherited_tail = after_inherited
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(1)),
                    "src/point_add/inherited_tail.rs",
                    8,
                    9,
                )
                .expect("append inherited tail");
            let mut inherited = op(OperationType::X);
            inherited.q_target = QubitId(3);
            after_inherited.push_inherited(
                inherited,
                OriginRef {
                    site_id: 0,
                    emission_ordinal: 0,
                    inverse_depth: 0,
                    flags: 0,
                },
            );
            let inherited_snapshot = snapshot(&after_inherited);
            assert_eq!(
                after_inherited
                    .rewrite_synthetic_tail_targets(inherited_tail, &[QubitId(8), QubitId(8)],)
                    .expect_err("push_inherited must invalidate the pending tail"),
                "synthetic tail capability is not pending",
                "audit={enabled}"
            );
            assert_eq!(
                snapshot(&after_inherited),
                inherited_snapshot,
                "audit={enabled}"
            );
        }
    }

    #[test]
    fn synthetic_tail_replay_is_rejected_in_both_audit_modes_without_mutation() {
        for enabled in [false, true] {
            let mut traced = TracedOps::new(enabled);
            let tail = traced
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(2)),
                    "src/point_add/tail.rs",
                    2,
                    3,
                )
                .expect("append tail");
            let replay = forge_synthetic_tail(&tail);
            traced
                .rewrite_synthetic_tail_targets(tail, &[QubitId(5), QubitId(5)])
                .expect("first rewrite");

            let before_replay = snapshot(&traced);
            assert!(traced
                .rewrite_synthetic_tail_targets(replay, &[QubitId(7), QubitId(7)])
                .is_err());
            assert_eq!(snapshot(&traced), before_replay, "audit={enabled}");
        }
    }

    #[test]
    fn synthetic_tail_cross_stream_handle_does_not_clear_legitimate_pending_capability() {
        for enabled in [false, true] {
            let mut source = TracedOps::new(enabled);
            let source_tail = source
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(1)),
                    "src/point_add/source_tail.rs",
                    2,
                    3,
                )
                .expect("append source tail");
            let source_rewrite = forge_synthetic_tail(&source_tail);

            let mut receiver = TracedOps::new(enabled);
            let receiver_tail = receiver
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(2)),
                    "src/point_add/receiver_tail.rs",
                    4,
                    5,
                )
                .expect("append receiver tail");
            let receiver_before = snapshot(&receiver);

            assert!(receiver
                .rewrite_synthetic_tail_targets(source_tail, &[QubitId(8), QubitId(8)])
                .is_err());
            assert_eq!(snapshot(&receiver), receiver_before, "audit={enabled}");
            receiver
                .rewrite_synthetic_tail_targets(receiver_tail, &[QubitId(9), QubitId(9)])
                .expect("receiver capability remains live");
            source
                .rewrite_synthetic_tail_targets(source_rewrite, &[QubitId(7), QubitId(7)])
                .expect("source capability remains live");
        }
    }

    #[test]
    fn synthetic_tail_ticket_and_range_must_match_without_consuming_pending_state() {
        for enabled in [false, true] {
            for corrupt_ticket in [false, true] {
                let mut traced = TracedOps::new(enabled);
                let tail = traced
                    .append_synthetic_tail_at(
                        &canonical_tail(QubitId(1)),
                        "src/point_add/tail.rs",
                        2,
                        3,
                    )
                    .expect("append tail");
                let mut forged = forge_synthetic_tail(&tail);
                if corrupt_ticket {
                    forged.ticket = forged.ticket.wrapping_add(1);
                } else {
                    forged.start += 1;
                }
                let before_forgery = snapshot(&traced);

                assert!(traced
                    .rewrite_synthetic_tail_targets(forged, &[QubitId(8), QubitId(8)])
                    .is_err());
                assert_eq!(snapshot(&traced), before_forgery, "audit={enabled}");
                traced
                    .rewrite_synthetic_tail_targets(tail, &[QubitId(9), QubitId(9)])
                    .expect("legitimate pending capability remains live");
            }
        }
    }

    #[test]
    fn clone_gets_a_fresh_owner_and_does_not_invalidate_the_original_capability() {
        for enabled in [false, true] {
            let mut original = TracedOps::new(enabled);
            let tail = original
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(3)),
                    "src/point_add/tail.rs",
                    2,
                    3,
                )
                .expect("append tail");
            let cloned_handle = forge_synthetic_tail(&tail);
            let original_owner = original.owner_generation;
            let mut cloned = original.clone();
            let cloned_before = snapshot(&cloned);

            assert_ne!(cloned.owner_generation, original_owner);
            assert!(cloned
                .rewrite_synthetic_tail_targets(cloned_handle, &[QubitId(6), QubitId(6)])
                .is_err());
            assert_eq!(snapshot(&cloned), cloned_before, "audit={enabled}");
            original
                .rewrite_synthetic_tail_targets(tail, &[QubitId(7), QubitId(7)])
                .expect("original capability remains live");
        }
    }

    #[test]
    fn take_moves_tail_ownership_and_replaces_it_with_a_fresh_owner() {
        for enabled in [false, true] {
            let mut original = TracedOps::new(enabled);
            let tail = original
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(3)),
                    "src/point_add/tail.rs",
                    2,
                    3,
                )
                .expect("append tail");
            let replacement_handle = forge_synthetic_tail(&tail);
            let original_owner = original.owner_generation;
            let mut taken = original.take();

            assert_eq!(taken.owner_generation, original_owner);
            assert_ne!(original.owner_generation, original_owner);
            let replacement_before = snapshot(&original);
            assert!(original
                .rewrite_synthetic_tail_targets(replacement_handle, &[QubitId(6), QubitId(6)],)
                .is_err());
            assert_eq!(snapshot(&original), replacement_before, "audit={enabled}");
            taken
                .rewrite_synthetic_tail_targets(tail, &[QubitId(7), QubitId(7)])
                .expect("taken stream preserves capability ownership");
        }
    }

    #[test]
    fn pending_tail_blocks_append_and_survives_the_rejected_append() {
        for enabled in [false, true] {
            let mut traced = TracedOps::new(enabled);
            let tail = traced
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(1)),
                    "src/point_add/first_tail.rs",
                    2,
                    3,
                )
                .expect("append first tail");
            let before_second_append = snapshot(&traced);
            assert!(traced
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(2)),
                    "src/point_add/second_tail.rs",
                    4,
                    5,
                )
                .is_err());
            assert_eq!(snapshot(&traced), before_second_append, "audit={enabled}");
            traced
                .rewrite_synthetic_tail_targets(tail, &[QubitId(8), QubitId(8)])
                .expect("pending capability survives rejected append");
        }
    }

    #[test]
    fn matching_tail_attempt_is_consumed_before_target_validation() {
        for enabled in [false, true] {
            let mut traced = TracedOps::new(enabled);
            let tail = traced
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(1)),
                    "src/point_add/tail.rs",
                    2,
                    3,
                )
                .expect("append tail");
            let replay = forge_synthetic_tail(&tail);
            let before_failure = snapshot(&traced);

            assert!(traced
                .rewrite_synthetic_tail_targets(tail, &[QubitId(8)])
                .is_err());
            assert_eq!(snapshot(&traced), before_failure, "audit={enabled}");
            assert!(traced
                .rewrite_synthetic_tail_targets(replay, &[QubitId(8), QubitId(8)])
                .is_err());
            assert_eq!(snapshot(&traced), before_failure, "audit={enabled}");
            assert!(traced
                .append_synthetic_tail_at(
                    &canonical_tail(QubitId(2)),
                    "src/point_add/recovery_tail.rs",
                    4,
                    5,
                )
                .is_ok());
        }
    }

    #[test]
    fn audit_off_and_on_return_identical_fixture_ops() {
        let plain = rewritten_nonce_fixture(false);
        let audited = rewritten_nonce_fixture(true);
        assert_eq!(plain.to_vec(), audited.to_vec());
        assert!(plain.origins().is_empty());
        assert!(plain.sites().is_empty());
        assert_eq!(audited.origins().len(), audited.len());
    }

    #[test]
    fn paired_tail_matches_legacy_nonce_targets() {
        for nonce in [0, 1, 8107117281543, (1u64 << 48) - 1, u64::MAX] {
            let mut expected = vec![x(QubitId(0)); 96];
            let mut targets = [QubitId(0); 96];
            for bit in 0usize..48 {
                let target = if (nonce >> bit) & 1 == 1 {
                    QubitId(1)
                } else {
                    QubitId(0)
                };
                expected[2 * bit].q_target = target;
                expected[2 * bit + 1].q_target = target;
                targets[2 * bit] = target;
                targets[2 * bit + 1] = target;
            }

            let mut stream = TracedOps::new(false);
            let tail = stream
                .append_synthetic_tail(&[x(QubitId(0)); 96])
                .expect("append exact synthetic tail");
            stream
                .rewrite_synthetic_tail_targets(tail, &targets)
                .expect("rewrite exact synthetic tail");
            assert_eq!(stream.to_vec(), expected, "nonce {nonce}");
        }
    }

    #[test]
    fn transform_chain_renders_nested_inverse_and_flags_in_canonical_order() {
        let origin = OriginRef {
            site_id: 9,
            emission_ordinal: 12,
            inverse_depth: 2,
            flags: ORIGIN_TAIL_NONCE_REWRITTEN | ORIGIN_EMIT_INVERSE | ORIGIN_SYNTHETIC_TAIL,
        };
        assert_eq!(
            origin.transform_chain(),
            "emit_inverse>emit_inverse>synthetic_tail>tail_nonce_rewritten"
        );
        assert_eq!(
            OriginRef {
                inverse_depth: 0,
                flags: ORIGIN_SYNTHETIC_TAIL,
                ..origin
            }
            .transform_chain(),
            "synthetic_tail"
        );
        assert_eq!(
            OriginRef {
                inverse_depth: 0,
                flags: 0,
                ..origin
            }
            .transform_chain(),
            "-"
        );
    }

    #[test]
    #[should_panic(expected = "inverse provenance depth/flag disagreement")]
    fn transform_chain_rejects_flag_depth_disagreement() {
        OriginRef {
            site_id: 0,
            emission_ordinal: 0,
            inverse_depth: 1,
            flags: 0,
        }
        .transform_chain();
    }

    #[test]
    #[should_panic(expected = "inverse provenance depth/flag disagreement")]
    fn transform_chain_rejects_inverse_flag_without_depth() {
        OriginRef {
            site_id: 0,
            emission_ordinal: 0,
            inverse_depth: 0,
            flags: ORIGIN_EMIT_INVERSE,
        }
        .transform_chain();
    }
}
