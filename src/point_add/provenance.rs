use std::collections::HashMap;
use std::ops::{Deref, Index};

use crate::circuit::Op;

use super::current_trace_context;

pub(crate) const ORIGIN_SYNTHETIC_TAIL: u16 = 1;
pub(crate) const ORIGIN_TAIL_NONCE_REWRITTEN: u16 = 2;
pub(crate) const ORIGIN_EMIT_INVERSE: u16 = 4;
const KNOWN_ORIGIN_FLAGS: u16 =
    ORIGIN_SYNTHETIC_TAIL | ORIGIN_TAIL_NONCE_REWRITTEN | ORIGIN_EMIT_INVERSE;

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
pub(crate) struct OriginRef {
    pub(crate) site_id: u32,
    pub(crate) emission_ordinal: u32,
    pub(crate) inverse_depth: u16,
    pub(crate) flags: u16,
}

impl OriginRef {
    fn validate_transform_chain(self) {
        assert_eq!(
            self.flags & !KNOWN_ORIGIN_FLAGS,
            0,
            "unknown provenance transform flags"
        );
        assert_eq!(
            self.inverse_depth != 0,
            self.flags & ORIGIN_EMIT_INVERSE != 0,
            "inverse provenance depth/flag disagreement"
        );
    }

    pub(crate) fn transform_chain(self) -> String {
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
}

#[derive(Clone)]
pub(crate) struct TracedOps {
    ops: Vec<Op>,
    origins: Vec<OriginRef>,
    sites: Vec<SourceSite>,
    site_ids: HashMap<(&'static str, u32, u32), u32>,
    enabled: bool,
}

impl TracedOps {
    pub(crate) fn new(enabled: bool) -> Self {
        Self {
            ops: Vec::new(),
            origins: Vec::new(),
            sites: Vec::new(),
            site_ids: HashMap::new(),
            enabled,
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
        let emission_ordinal =
            u32::try_from(self.ops.len()).expect("provenance emission ordinal exceeds u32");
        if self.enabled {
            let key = (file, line, trace_context);
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
            self.ops.push(op);
            self.origins.push(origin);
        } else {
            self.ops.push(op);
        }
        self.assert_paired();
    }

    pub(crate) fn push_inherited(&mut self, op: Op, mut origin: OriginRef) {
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

    pub(crate) fn truncate(&mut self, len: usize) {
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

    #[test]
    fn origin_ref_is_twelve_bytes() {
        assert_eq!(std::mem::size_of::<OriginRef>(), 12);
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
                },
                SourceSite {
                    file: "second.rs",
                    line: 22,
                    trace_context: 8,
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
        traced.push_at(op(OperationType::Z), "two.rs", 2, 20, 0, 0);

        let taken = traced.take();

        assert!(traced.is_empty());
        assert!(traced.origins().is_empty());
        assert!(traced.sites().is_empty());
        assert_eq!(taken.len(), 2);
        assert_eq!(taken.origins().len(), 2);
        assert_eq!(taken.sites().len(), 2);
        assert_eq!(
            taken
                .origins()
                .iter()
                .map(|origin| origin.emission_ordinal)
                .collect::<Vec<_>>(),
            vec![0, 1]
        );
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
                },
                SourceSite {
                    file: file!(),
                    line: z_line,
                    trace_context: 0,
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
