//! Stage-level differential: 3-hole (canonical Q793) vs 4-hole (Q792 probe)
//! on the SAME inputs, comparing every geometry-invariant state at each cut.
//! The only lanes that may legitimately differ are work1 (the A-ladder slide
//! re-homes its rails) and the phase-passenger ports; everything else -- rank,
//! a, c, sm, phase1/phase2, iteration, work2, all passengers, phase, and the
//! final 257-bit dx output -- must agree bit-for-bit at every cut.
use super::*;
use crate::circuit::{Op,OperationType,NO_QUBIT};
use crate::sim::Simulator;
use sha3::digest::XofReader;

struct Fixed(u64);
impl XofReader for Fixed{fn read(&mut self,b:&mut[u8]){for x in b{*x=rnd(&mut self.0)as u8;}}}
fn rnd(s:&mut u64)->u64{*s^=*s<<13;*s^=*s>>7;*s^=*s<<17;*s}
fn put(w:&mut[u64],i:usize,lane:usize,v:bool){let bit=1u64<<lane;w[i]=(w[i]&!bit)|if v{bit}else{0};}

struct Snapshot {name:&'static str,phase:u64,state:Vec<u64>,owned:usize,skip_w1:bool}

/// Logical projection used for cross-geometry comparison.
/// indices 0..24 = rank/a/c/sm/p1/p2/iter, 24..283 = work1 (SKIPPED),
/// 283..542 = work2; passengers appended at 542.. (same physical ids both
/// geometries, appended in identical order).
fn snapshot<R:XofReader>(sim:&Simulator<'_,R>,mapping:&[usize],passenger:&[crate::point_add::trailmix_port::circuit::QReg],name:&'static str,owned:usize,skip_w1:bool)->Snapshot{
    let mut state=vec![0u64;mapping.len()+passenger.len()];
    for(i,&q)in mapping.iter().enumerate(){if q!=u32::MAX as usize{state[i]=sim.qubits[q];}}
    for(i,p)in passenger.iter().enumerate(){state[mapping.len()+i]=sim.qubits[p.id()as usize];}
    Snapshot{name,phase:sim.phase,state,owned,skip_w1}
}

fn compare(a:&Snapshot,b:&Snapshot,tag:&str,strict_phase:bool)->bool{
    let mut first=None;
    let n=a.state.len().min(b.state.len());
    let w2shift=std::env::var("LOWQ_Q792_DIFF_W2SHIFT").ok().and_then(|v|v.parse::<i64>().ok()).unwrap_or(0);
    let w1cmp=std::env::var("LOWQ_Q792_DIFF_W1").ok().as_deref()==Some("1");
    for i in 0..n{
        // work1 region may legitimately differ; work2 and control regs and
        // passengers must agree exactly.
        // w1 lanes that exist in BOTH geometries: 24..278 (w1[0..254]).
        // w1[255] is real only in 3-hole (its bit-3 toggle has no 4-hole
        // home by design) and 256..258 are markers in both.
        if a.skip_w1&&b.skip_w1&&(24..283).contains(&i)&&!(w1cmp&&(24..278).contains(&i)){continue;}
        let j=if a.skip_w1&&b.skip_w1&&(283..541).contains(&i){
            let k=i as i64-283;let k2=if (3..=257).contains(&k){k+w2shift}else{k};283+k2.clamp(0,258)as usize
        }else{i};
        if j<n&&a.state[i]!=b.state[j]{if first.is_none(){first=Some(i);}}
    }
    let phase_diff=a.phase!=b.phase;
    let tail=if a.state.len()!=b.state.len(){Some((a.state.len(),b.state.len()))}else{None};
    let ok=first.is_none()&&(!phase_diff||!strict_phase)&&tail.is_none();
    eprintln!("DIFF_CUT {tag}: {} phase3={:#018x} phase4={:#018x} first_divergence={:?} tail={:?} owned3={} owned4={}",
        if ok{"PASS"}else{"FAIL"},a.phase,b.phase,first,tail,a.owned,b.owned);
    if let Some(i)=first{
        let s3=&a.state[i];let s4=&b.state[i];
        // print the differing lanes of the two 64-bit words
        let mut shown=0;
        for lane in 0..64{
            let (v3,v4)=((s3>>lane)&1,(s4>>lane)&1);
            if v3!=v4{eprintln!("DIFF_CUT {tag}: logical={i} lane={lane} hole3={} hole4={} (word3={s3:#x} word4={s4:#x})",v3,v4);shown+=1;if shown>=4{break;}}
        }
    }
    ok
}

fn cut<R:XofReader>(sims:&[Simulator<'_,R>],name:&'static str,mapping:&[usize],passenger:&[crate::point_add::trailmix_port::circuit::QReg],owned:usize,snaps:&mut Vec<Snapshot>){
    snaps.push(snapshot(&sims[0],mapping,passenger,name,owned,true));
}

pub fn run(){
    // Stage-level drill-in: same lifecycle as divide_forward (initialize,
    // loan bracket, 26 forward blocks, release, canonical inverse sign,
    // rebuild, 26 reverse blocks, finish) with fast checker-style emission
    // (no NCT pass; NCT cancellation preserves function, so this is exact).
    // Compare every geometry-invariant register at each cut: 3-hole (official
    // Q793 receipt is the oracle) vs 4-hole on IDENTICAL inputs.
    let mut rows:Vec<(Vec<u8>,Vec<u8>)>=Vec::new();
    let mut s=0x51ef46b9ac287d03u64;
    for _ in 0..24{
        let mut x=[0u8;32];for b in x.iter_mut(){*b=rnd(&mut s)as u8;}x[31]&=0x7f; // x < 2^255 < p
        let mut y=[0u8;32];for b in y.iter_mut(){*b=rnd(&mut s)as u8;}y[31]&=0x7f; // dy < 2^255, top lane zero
        rows.push((x.to_vec(),y.to_vec()));
    }
    for a in 244..=255{
        let mut x=[0u8;32];for b in x.iter_mut(){*b=rnd(&mut s)as u8;}
        for i in 0..256{x[i/8]&=!(1<<(i%8));}
        x[a/8]|=1<<(a%8);
        if a==255{for i in 254..255{x[i/8]&=!(1<<(i%8));}}
        let mut y=[0u8;32];for b in y.iter_mut(){*b=rnd(&mut s)as u8;}y[31]&=0x7f;
        rows.push((x.to_vec(),y.to_vec()));
    }
    if std::env::var("LOWQ_Q792_DIFF_SUBSET").ok().as_deref()==Some("few"){rows.truncate(4);}
    let count=rows.len();let batches=count.div_ceil(64);
    eprintln!("Q792_FOURHOLE_DIFF rows={count} batches={batches}");

    let mut runs:Vec<(String,Vec<Snapshot>)>=Vec::new();
    std::env::set_var("Q795_STAGE_CENSUS","1");
    for four in [false,true]{
        std::env::set_var("LOWQ_Q792_EEA",if four{"1"}else{"0"});
        std::env::set_var("Q792_QUOTIENT_TOP_BORROW","0");
        eprintln!("Q792_FOURHOLE_DIFF emitting four_hole={four}");
        let mut circ=Circuit::new();
        let dx=circ.alloc_qreg_bits("input",257);   // ids 0..256
        let mut dy=circ.alloc_qreg_bits("passenger",257); // ids 257..513
        let released_dy_top=loan_canonical_top(&mut circ,&mut dy,"fourhole-diff forward dy");
        let passenger:Vec<_>=dy.iter().map(|q|q.borrowed_alias()).collect();
        let core=initialize(&mut circ,dx,&passenger[0],&passenger[1]);
        let mapping=ids(&core);
        let initialization=std::mem::take(&mut circ.b.ops);
        let loan_fwd=remap(loan_bracket_ops(),&mapping,&passenger,false);
        let mut terminal=release_terminal(&mut circ,core);
        release_terminal_padding(&mut circ,&mut terminal);
        let release=std::mem::take(&mut circ.b.ops);
        toggle_inverse_sign(&mut circ,&terminal);
        let to_inverse=std::mem::take(&mut circ.b.ops);
        let from_inverse=std::mem::take(&mut circ.b.ops);
        restore_terminal_padding(&mut circ,&mut terminal);
        let core=rebuild_terminal(&mut circ,terminal,&passenger[0],&passenger[1]);
        let rebuilt_map=ids(&core);
        let rebuild=std::mem::take(&mut circ.b.ops);
        let dxo=finish(&mut circ,core);
        let finishing=std::mem::take(&mut circ.b.ops);
        let owned=circ.b.next_qubit as usize;
        let bits=circ.b.next_bit as usize;
        eprintln!("Q792_FOURHOLE_DIFF built four={four} owned={owned} bits={bits} peak={}",circ.b.peak_qubits);
        let mut sims:Vec<_>=(0..batches).map(|b|Simulator::new(owned,bits,Box::leak(Box::new(Fixed(0x14e5a67db802c39f^b as u64))))).collect();
        for batch in 0..batches{
            let mut seed=0x51ef46b9ac287d03u64^batch as u64;
            let mut state=vec![0u64;owned];
            for q in 257..513{state[q]=rnd(&mut seed);} // dy[0..255] random; dy[256] (id 513) stays zero
            for lane in 0..64{
                let (xrow,yrow)=&rows[(batch*64+lane)%count];
                for bit in 0..256{put(&mut state,bit,lane,xrow[bit/8]>>(bit%8)&1!=0);}
                for bit in 0..255{put(&mut state,257+bit,lane,yrow[bit/8]>>(bit%8)&1!=0);}
            }
            sims[batch].qubits=state;
        }
        let mut snaps:Vec<Snapshot>=Vec::new();
        for sim in &mut sims{sim.apply_iter(initialization.iter());}
        cut(&sims,"initialize",&mapping,&passenger,owned,&mut snaps);
        for sim in &mut sims{sim.apply_iter(loan_fwd.iter());}
        cut(&sims,"loan_open",&mapping,&passenger,owned,&mut snaps);
        for z in 0..26{
            let block=z;
            let mut templates:Vec<_>=Vec::new();
            let mut j1_stages:Vec<(&'static str,usize)>=Vec::new();
            let mut j0_stages:Vec<(&'static str,usize)>=Vec::new();
            for j in 0..4{
                let ops=remap(template(block,j),&mapping,&passenger,false);
                if block==0&&j==1{
                    j1_stages=super::super::q793_step_r03::marks();
                    eprintln!("Q792_FOURHOLE_DIFF j1_ops_len={} marks={:?}",ops.len(),j1_stages.last());
                    if std::env::var("LOWQ_Q792_DIFF_OPDUMP").ok().as_deref()==Some("1"){
                        let logical=template(block,j);
                        for(i,op)in logical.iter().take(36).enumerate(){
                            eprintln!("Q792_OPDUMP i={i} kind={:?} q2={} q1={} t={} ct={} cc={}",op.kind,op.q_control2.0,op.q_control1.0,op.q_target.0,op.c_target.0,op.c_condition.0);
                        }
                    }
                }
                if block==0&&j==0{j0_stages=super::super::q793_step_r03::marks();}
                templates.push(ops);
            }
            let first=block*64;let end=(first+64).min(1616);
            for i in 0..end-first{
                let step=first+i;
                let ops=&templates[(step+1)%4];
                if z==0&&i==3{
                    // stage cuts inside the j=0 template at step 3 (first w1
                    // divergence site)
                    let mut prev=0usize;
                    for(name,idx)in j0_stages.iter().copied(){
                        let idx=idx.min(ops.len());
                        if idx<=prev{continue;}
                        for sim in &mut sims{sim.apply_iter(ops[prev..idx].iter());}
                        let cn:&'static str=Box::leak(format!("block0_j0_{name}").into_boxed_str());
                        cut(&sims,cn,&mapping,&passenger,owned,&mut snaps);
                        prev=idx;
                    }
                    for sim in &mut sims{sim.apply_iter(ops[prev..].iter());}
                }else if z==0&&i==4{
                    // stage-level cuts inside the j=1 template at the first
                    // diverging application (step 4)
                    let mut prev=0usize;
                    for(si,(name,idx))in j1_stages.iter().copied().enumerate(){
                        let idx=idx.min(ops.len());
                        if idx<=prev{continue;}
                        if si==1{
                            // bisect the T10 stage at 2^12 granularity
                            let mut applied=prev;
                            for c in (1..(1<<12)).map(|k|prev+(idx-prev)*k/(1<<12)){
                                for sim in &mut sims{sim.apply_iter(ops[applied..c].iter());}
                                let cn:&'static str=Box::leak(format!("t10_bisect_{c}").into_boxed_str());
                                cut(&sims,cn,&mapping,&passenger,owned,&mut snaps);
                                applied=c;
                            }
                            for sim in &mut sims{sim.apply_iter(ops[applied..idx].iter());}
                            let cn:&'static str=Box::leak(format!("block0_j1_{name}").into_boxed_str());
                            cut(&sims,cn,&mapping,&passenger,owned,&mut snaps);
                        }else{
                            for sim in &mut sims{sim.apply_iter(ops[prev..idx].iter());}
                            let cn:&'static str=Box::leak(format!("block0_j1_{name}").into_boxed_str());
                            cut(&sims,cn,&mapping,&passenger,owned,&mut snaps);
                        }
                        prev=idx;
                    }
                    for sim in &mut sims{sim.apply_iter(ops[prev..].iter());}
                }else{
                    for sim in &mut sims{sim.apply_iter(ops.iter());}
                }
                if z==0&&i!=4{
                    let name:&'static str=Box::leak(format!("fwd_block0_step{i}").into_boxed_str());
                    cut(&sims,name,&mapping,&passenger,owned,&mut snaps);
                }
            }
            let name:&'static str=Box::leak(format!("fwd_block{block}").into_boxed_str());
            cut(&sims,name,&mapping,&passenger,owned,&mut snaps);
        }
        for sim in &mut sims{sim.apply_iter(loan_fwd.iter());}
        cut(&sims,"loan_close",&mapping,&passenger,owned,&mut snaps);
        for sim in &mut sims{sim.apply_iter(release.iter());}
        cut(&sims,"release_terminal",&mapping,&passenger,owned,&mut snaps);
        for sim in &mut sims{sim.apply_iter(to_inverse.iter());}
        cut(&sims,"canonical_inverse",&mapping,&passenger,owned,&mut snaps);
        for sim in &mut sims{sim.apply_iter(from_inverse.iter());}
        cut(&sims,"restore_sign",&mapping,&passenger,owned,&mut snaps);
        for sim in &mut sims{sim.apply_iter(rebuild.iter());}
        cut(&sims,"rebuild_terminal",&rebuilt_map,&passenger,owned,&mut snaps);
        for z in 0..26{
            let block=25-z;
            let templates:Vec<_>=(0..4).map(|j|remap(template(block,j),&rebuilt_map,&passenger,true)).collect();
            let first=block*64;let end=(first+64).min(1616);
            for i in 0..end-first{
                let step=end-1-i;
                let ops=&templates[(step+1)%4];
                for sim in &mut sims{sim.apply_iter(ops.iter());}
            }
            let name:&'static str=Box::leak(format!("rev_block{block}").into_boxed_str());
            cut(&sims,name,&rebuilt_map,&passenger,owned,&mut snaps);
        }
        for sim in &mut sims{sim.apply_iter(finishing.iter());}
        let mut state=vec![0u64;257+256];
        for(i,q)in dxo.iter().enumerate(){state[i]=sims[0].qubits[q.id()as usize];}
        for(i,p)in passenger.iter().enumerate(){state[257+i]=sims[0].qubits[p.id()as usize];}
        snaps.push(Snapshot{name:"finish",phase:sims[0].phase,state,owned,skip_w1:false});
        restore_canonical_top(&mut circ,&mut dy,released_dy_top);
        let label=format!("four_hole={four}");
        runs.push((label,snaps));
    }
    assert_eq!(runs[0].1.len(),runs[1].1.len());
    for(a,b)in runs[0].1.iter().zip(runs[1].1.iter()){
        let strict=a.name=="finish";
        compare(a,b,a.name,strict);
    }
    eprintln!("Q792_FOURHOLE_DIFF DRILL COMPLETE cuts={}",runs[0].1.len());
}
