//! Actual emitted sequence, bounded memory, independent development seed.
//! This is NOT the official Fiat-Shamir acceptance procedure.
use crate::circuit::{Op,OperationType as K,QubitId,QubitOrBit,BitId};
use crate::sim::Simulator;
use alloy_primitives::U256;
use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
struct Batch {
    sim:Simulator<'static,sha3::Shake256Reader>, expected:Vec<(U256,U256)>, expected_lam:Vec<U256>, offsets:Vec<(U256,U256)>,
    ops:usize, initial_ops:usize, started:std::time::Instant, regs:Vec<Vec<QubitOrBit>>,
}
impl Batch {
    /// Divide-only variant: the caller injects dx/dy inputs; the check then
    /// requires the lifecycle to return them unchanged (identity), phase 0 and
    /// clean ancillas. Same sim dimensions and RNG stream as the production
    /// sprint so the Hmr/R measurement outcomes reproduce exactly.
    pub fn new_divide(tx:&[super::trailmix_port::circuit::QReg],ty:&[super::trailmix_port::circuit::QReg],initial_ops:usize,rows:&[(Vec<u8>,Vec<u8>,Vec<u8>)])->Self {
        let mut seed=Shake256::default();seed.update(b"Q799-independent-whole-stream-sprint-v2");
        if let Ok(s)=std::env::var("SPRINT_STREAM_SEED"){seed.update(s.as_bytes());}
        let reader=Box::leak(Box::new(seed.finalize_xof()));
        let mut sim=Simulator::new(1024,1_000_000,reader);let mut expected=Vec::new();let mut expected_lam=Vec::new();
        let regs:Vec<Vec<QubitOrBit>>=vec![tx.iter().map(|q|QubitOrBit::Qubit(QubitId(q.id() as u64))).collect(),ty.iter().map(|q|QubitOrBit::Qubit(QubitId(q.id() as u64))).collect()];
        for lane in 0..64{
            let (xrow,yrow,lrow)=&rows[lane%rows.len()];
            let mut x=[0u8;32];x[..32].copy_from_slice(&xrow[..32]);
            let mut y=[0u8;32];y[..32].copy_from_slice(&yrow[..32]);
            let mut l=[0u8;32];l[..32].copy_from_slice(&lrow[..32]);
            sim.set_register(&regs[0],U256::from_le_bytes(x),lane);
            sim.set_register(&regs[1],U256::from_le_bytes(y),lane);
            expected.push((U256::from_le_bytes(x),U256::from_le_bytes(y)));
            expected_lam.push(U256::from_le_bytes(l));
        }
        eprintln!("SPRINT_DIVIDE_START independent_shots=64 initial_ops={initial_ops}; no stream retained");
        Self{sim,expected,expected_lam,offsets:Vec::new(),ops:0,initial_ops,started:std::time::Instant::now(),regs}
    }
    pub fn new(tx:&[super::trailmix_port::circuit::QReg],ty:&[super::trailmix_port::circuit::QReg],ox:&[super::trailmix_port::circuit::Cbit],oy:&[super::trailmix_port::circuit::Cbit],initial_ops:usize,batch:usize)->Self {
        let curve=super::compact_check::secp256k1();
        let mut seed=Shake256::default();seed.update(b"Q799-independent-whole-stream-sprint-v2");
        if let Ok(s)=std::env::var("SPRINT_STREAM_SEED"){seed.update(s.as_bytes());}
        if batch>0 {seed.update(b"\0Q795-independent-additional-batch-v1\0");seed.update(&(batch as u64).to_le_bytes());}
        let reader=Box::leak(Box::new(seed.finalize_xof()));
        let mut sim=Simulator::new(1024,1_000_000,reader);let mut expected=Vec::new();let mut offsets=Vec::new();
        let regs:Vec<Vec<QubitOrBit>>=vec![tx.iter().map(|q|QubitOrBit::Qubit(QubitId(q.id() as u64))).collect(),ty.iter().map(|q|QubitOrBit::Qubit(QubitId(q.id() as u64))).collect(),ox.iter().map(|q|QubitOrBit::Bit(BitId(q.raw() as u64))).collect(),oy.iter().map(|q|QubitOrBit::Bit(BitId(q.raw() as u64))).collect()];
        for lane in 0..64 {
            let mut a=[0u8;32];let mut b=[0u8;32];sim.xof.read(&mut a);sim.xof.read(&mut b);
            let t=curve.mul(curve.gx,curve.gy,U256::from_le_bytes(a));let o=curve.mul(curve.gx,curve.gy,U256::from_le_bytes(b));
            assert_ne!(t.0,o.0);assert_ne!(t,(U256::ZERO,U256::ZERO));assert_ne!(o,(U256::ZERO,U256::ZERO));
            expected.push(curve.add(t.0,t.1,o.0,o.1));offsets.push(o);
            for (r,v) in regs.iter().zip([t.0,t.1,o.0,o.1]){sim.set_register(r,v,lane);}
        }
        eprintln!("SPRINT_STREAM_START independent_shots=64 initial_ops={initial_ops}; no stream retained");
        Self{sim,expected,expected_lam:Vec::new(),offsets,ops:0,initial_ops,started:std::time::Instant::now(),regs:Vec::new()}
    }
    pub fn apply(&mut self,ops:&[Op]) {
        assert!(!ops.iter().any(|o|matches!(o.kind,K::PushCondition|K::PopCondition)));
        const MARKER:u64=u32::MAX as u64;
        for op in ops {if op.q_target.0==MARKER||op.q_control1.0==MARKER||op.q_control2.0==MARKER {
            panic!("Q792_MARKER_OP seq={} kind={:?} q2={} q1={} t={}; omitted-lane marker reached the emitted stream",self.ops,op.kind,op.q_control2.0,op.q_control1.0,op.q_target.0);
        }if op.kind==K::AppendToRegister {
            let r=op.r_target.0 as usize;while self.regs.len()<=r{self.regs.push(Vec::new());}
            self.regs[r].push(if op.q_target.0!=u64::MAX{QubitOrBit::Qubit(op.q_target)}else{QubitOrBit::Bit(op.c_target)});
        }}
        self.sim.apply_iter(ops.iter());self.ops+=ops.len();
    }
    pub fn finish(self,b:&super::B) {
        eprintln!("SPRINT_MEMORY_ACCOUNT ops={} op_bytes={} classical_bits={} classical_bytes={} physical_qubits={}",b.counted_ops,b.counted_ops*std::mem::size_of::<Op>(),b.next_bit,b.next_bit as u64*8,b.next_qubit);
        assert_eq!(self.ops+self.initial_ops,b.counted_ops,"real stream coverage");
        assert_eq!(self.regs.len(),4);let regs=&self.regs;let mut failures=0;
        for lane in 0..64 {
            let got=(self.sim.get_register(&regs[0],lane),self.sim.get_register(&regs[1],lane));
            if got!=self.expected[lane]{failures+=1;eprintln!("SPRINT_STREAM_MISMATCH lane={lane} got={got:?} expected={:?}",self.expected[lane]);}
            assert_eq!((self.sim.get_register(&regs[2],lane),self.sim.get_register(&regs[3],lane)),self.offsets[lane]);
        }
        let output:std::collections::BTreeSet<_>=regs.iter().flat_map(|r|r.iter()).filter_map(|q|if let QubitOrBit::Qubit(q)=q{Some(q.0 as usize)}else{None}).collect();
        let garbage=self.sim.qubits.iter().enumerate().filter(|(q,v)|!output.contains(q)&&**v!=0).count();
        if garbage>0||std::env::var("Q792_DIRTY_DUMP").ok().as_deref()==Some("1") {
            let lanes:Vec<_>=self.sim.qubits.iter().enumerate().filter(|(q,v)|!output.contains(q)&&**v!=0).collect();
            eprintln!("SPRINT_DIRTY_LANES count={} first={:?}",lanes.len(),&lanes[..lanes.len().min(24)]);
            let head:Vec<_>=(255..259).map(|i|(i,self.sim.qubits.get(i).copied().unwrap_or(0))).collect();
            eprintln!("SPRINT_HEAD_LANES {head:?}");
        }
        eprintln!("SPRINT_STREAM_RESULT shots=64 peak={} physical={} simulated_ops={} structural_T={} executed_average_T={} classical_failures={failures} phase={:#018x} dirty_ancillas={garbage} elapsed={:.1}; independent development seed, not official acceptance",b.peak_qubits,b.next_qubit,self.ops,b.counted_kind_ops[K::CCX as usize]+b.counted_kind_ops[K::CCZ as usize],self.sim.stats.toffoli_gates/64,self.sim.phase,self.started.elapsed().as_secs_f64());
        assert_eq!(failures,0);assert_eq!(self.sim.phase,0);assert_eq!(garbage,0);
    }
    pub fn finish_divide(self,b:&super::B,lambda:&[super::trailmix_port::circuit::QReg]) {
        eprintln!("SPRINT_DIVIDE_MEMORY ops={} physical_qubits={}",self.ops,b.next_qubit);
        assert_eq!(self.ops+self.initial_ops,b.counted_ops,"real stream coverage");
        let mut failures=0;
        let lr:Vec<QubitOrBit>=lambda.iter().map(|q|QubitOrBit::Qubit(QubitId(q.id() as u64))).collect();
        for lane in 0..64 {
            // The divide contract is lambda = dy * dx^-1 mod p; the returned
            // dx/dy are internal (the whole point-add only consumes lambda).
            let got_lam=self.sim.get_register(&lr,lane);
            if got_lam!=self.expected_lam[lane]{failures+=1;eprintln!("SPRINT_DIVIDE_MISMATCH lane={lane} got_lam={got_lam:?} expected_lam={:?}",self.expected_lam[lane]);}
        }
        let output:std::collections::BTreeSet<_>=self.regs.iter().flat_map(|r|r.iter()).chain(lr.iter()).filter_map(|q|if let QubitOrBit::Qubit(q)=q{Some(q.0 as usize)}else{None}).collect();
        let garbage=self.sim.qubits.iter().enumerate().filter(|(q,v)|!output.contains(q)&&**v!=0).count();
        eprintln!("SPRINT_DIVIDE_RESULT shots=64 peak={} physical={} classical_failures={failures} phase={:#018x} dirty_ancillas={garbage} elapsed={:.1}; divide-only development seed, not official acceptance",b.peak_qubits,b.next_qubit,self.sim.phase,self.started.elapsed().as_secs_f64());
        assert_eq!(failures,0);assert_eq!(self.sim.phase,0);
    }

    /// Diagnostic: verify the forward terminal work2 equals x^-1 mod p
    /// (lambda = work2 * dy, so work2 must be the canonical inverse).  The
    /// contract is lam = y * x^-1, hence x^-1 = lam * y^-1.  Report-only.
    pub fn check_forward_w2(&self,work2:&[super::trailmix_port::circuit::QReg]) {
        use alloy_primitives::U256;
        let p=U256::from_le_bytes(super::trailmix_port::mod_arith::SECP256K1_P_LE);
        let regs:Vec<QubitOrBit>=work2.iter().map(|q|QubitOrBit::Qubit(QubitId(q.id() as u64))).collect();
        let mut bad=0;
        for lane in 0..64{
            let inv_y=self.expected[lane].1.pow_mod(p.wrapping_sub(U256::from(2)),p);
            let want=self.expected_lam[lane].mul_mod(inv_y,p);
            let got=self.sim.get_register(&regs,lane);
            if got!=want{bad+=1;if bad<=4{eprintln!("SPRINT_W2_MISMATCH lane={lane} got={got:?} want={want:?}");}}
        }
        eprintln!("SPRINT_W2_CHECK mismatches={bad}/64");
    }
}
 
// Diagnostic-only fan-out: every independent simulator sees the SAME immutable
// emitted operations. Default one batch preserves the prior developer behavior.
pub(crate) struct Check { batches:Vec<Batch>,pub trace:std::cell::RefCell<Vec<Vec<alloy_primitives::U256>>> }
impl Check {
    pub fn new_divide(tx:&[super::trailmix_port::circuit::QReg],ty:&[super::trailmix_port::circuit::QReg],initial_ops:usize,rows:&[(Vec<u8>,Vec<u8>,Vec<u8>)])->Self {
        let batches=(0..1).map(|index|Batch::new_divide(tx,ty,initial_ops,rows)).collect();
        Self{batches,trace:std::cell::RefCell::new(Vec::new())}
    }
    pub fn finish_divide(self,b:&super::B,lambda:&[super::trailmix_port::circuit::QReg]){for batch in self.batches.into_iter(){batch.finish_divide(b,lambda);}}
    pub fn check_forward_w2(&self,work2:&[super::trailmix_port::circuit::QReg]){for batch in &self.batches{batch.check_forward_w2(work2);}}
    /// Per-block forward trace of the work2 data register (257 rails x 64
    /// lanes).  Both geometries trace into their own Check, so the caller can
    /// diff block by block to find the first divergent block.
    pub fn trace_w2(&self,work2:&[super::trailmix_port::circuit::QReg]){
        let regs:Vec<QubitOrBit>=work2.iter().map(|q|QubitOrBit::Qubit(QubitId(q.id() as u64))).collect();
        let mut row=Vec::with_capacity(64);
        for lane in 0..64{row.push(self.batches[0].sim.get_register(&regs,lane));}
        self.trace.borrow_mut().push(row);
    }
    pub fn new(tx:&[super::trailmix_port::circuit::QReg],ty:&[super::trailmix_port::circuit::QReg],ox:&[super::trailmix_port::circuit::Cbit],oy:&[super::trailmix_port::circuit::Cbit],initial_ops:usize)->Self {
        let count=std::env::var("SPRINT_STREAM_BATCHES").ok().map(|v|v.parse::<usize>().expect("integer independent batch count")).unwrap_or(1);
        assert!((1..=4).contains(&count),"one to four independent batches only");
        let batches=(0..count).map(|index|{
            eprintln!("SPRINT_STREAM_BATCH_START index={index} batches={count}");
            Batch::new(tx,ty,ox,oy,initial_ops,index)
        }).collect();
        Self{batches,trace:std::cell::RefCell::new(Vec::new())}
    }
    pub fn apply(&mut self,ops:&[Op]) {for batch in &mut self.batches{batch.apply(ops);}}
    pub fn finish(self,b:&super::B) {
        let count=self.batches.len();
        for(index,batch)in self.batches.into_iter().enumerate(){
            eprintln!("SPRINT_STREAM_BATCH_FINISH index={index} batches={count}");
            batch.finish(b);
        }
        // Reached only after ALL per-batch output, offset, phase, garbage,
        // register and complete-stream-coverage assertions have succeeded.
        eprintln!("SPRINT_MULTIBATCH_COMPLETE batches={count} independent_shots={} all_batches_pass=true",64*count);
    }
}
