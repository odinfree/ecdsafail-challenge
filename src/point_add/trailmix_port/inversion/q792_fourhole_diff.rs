//! Stage-level differential: 3-hole (canonical Q793) vs 4-hole (Q792 probe)
//! on the SAME inputs, comparing every geometry-invariant state at each cut.
//! The only lanes that may legitimately differ are work1 (the A-ladder slide
//! re-homes its rails) and the phase-passenger ports; everything else -- rank,
//! a, c, sm, phase1/phase2, iteration, work2, all passengers, phase, and the
//! final 257-bit dx output -- must agree bit-for-bit at every cut.
use super::*;
use crate::circuit::{Op,OperationType,NO_QUBIT};
use crate::sim::Simulator;
use sha3::digest::{XofReader,Update,ExtendableOutput};
use sha3::Shake256;

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
    if tag=="t10_bisect_36"&&a.state.len()>540{
        // loan probe: 3-hole w1[255] (logical 279) vs 4-hole w2[257] (logical 540)
        eprintln!("DIFF_LOAN_PROBE w1_255_3h={:#x} w2_258_3h={:#x} w2_258_4h={:#x} w2_257_3h={:#x} w2_257_4h={:#x} g3={:#x} g4={:#x}",
            a.state[279],a.state[541],b.state[541],a.state[540],b.state[540],a.state[544],b.state[544]);
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
    if std::env::var("LOWQ_Q792_DIFF_NO_TOP").ok().as_deref()==Some("1"){
        // restrict every row to A<=253 to isolate the top-A cargo region
        for (x,_y) in &mut rows{for i in 254..256{x[i/8]&=!(1<<(i%8));}}
    }
    if std::env::var("LOWQ_Q792_DIFF_SUBSET").ok().as_deref()==Some("few"){rows.truncate(4);}
    let count=rows.len();let batches=count.div_ceil(64);
    eprintln!("Q792_FOURHOLE_DIFF rows={count} batches={batches}");

    let mut runs:Vec<(String,Vec<Snapshot>)>=Vec::new();
    std::env::set_var("Q795_STAGE_CENSUS","1");
    // Keep the NCT frame optimization off so stage/cell marks recorded during
    // step() align with the emitted op stream (the frame is function-
    // preserving, so the differential semantics are unchanged).
    if std::env::var("LOWQ_Q792_DIFF_ALIGN").ok().as_deref()==Some("0"){
        std::env::set_var("Q793_FRAME","0");
        std::env::set_var("Q792_NO_CANCEL","1");
        std::env::set_var("Q794_TFACTOR","0");
    }
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
        // MBU reverse measurement bit (production emit_schedule allocates it
        // during emission; must exist before the sim bit-count is captured).
        let mbu_measurement=if super::super::q793_mbu::reverse(){Some(circ.b.alloc_bit())}else{None};
        let owned=circ.b.next_qubit as usize;
        let bits=circ.b.next_bit as usize;
        eprintln!("Q792_FOURHOLE_DIFF built four={four} owned={owned} bits={bits} peak={}",circ.b.peak_qubits);
        let mut sims:Vec<_>=(0..batches).map(|b|{
            // Match the production sprint's simulator RNG exactly: the Hmr/R
            // measurement outcomes draw from this stream and must reproduce
            // the official artifact's behavior.
            let mut seed=Shake256::default();
            seed.update(b"Q799-independent-whole-stream-sprint-v2");
            if let Ok(s)=std::env::var("SPRINT_STREAM_SEED"){seed.update(s.as_bytes());}
            if b>0{seed.update(b"\0Q795-independent-additional-batch-v1\0");seed.update(&(b as u64).to_le_bytes());}
            Simulator::new(owned,bits,Box::leak(Box::new(seed.finalize_xof())))
        }).collect();
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
            let mut j1_subs:Vec<(&'static str,usize)>=Vec::new();
            let mut j1_main:Vec<(&'static str,usize)>=Vec::new();
            let mut j0_stages:Vec<(&'static str,usize)>=Vec::new();
            let mut j0_cells:Vec<(usize,Vec<usize>)>=Vec::new();
            let mut j0_subs:Vec<(&'static str,usize)>=Vec::new();
            for j in 0..4{
                super::super::q793_t10_fused_v3::clear_cell_bounds();
                super::super::q793_r01_dynamic_timefix_r01::clear_sub_bounds();
                super::super::q793_r01_normal_timefix_r01::clear_main_bounds();
                let ops=remap(template(block,j),&mapping,&passenger,false);
                if block==0&&j==1{
                    j1_stages=super::super::q793_step_r03::marks();
                    j1_subs=super::super::q793_r01_dynamic_timefix_r01::sub_bounds();
                    j1_main=super::super::q793_r01_normal_timefix_r01::main_bounds();
                    eprintln!("Q792_FOURHOLE_DIFF j1_ops_len={} marks={:?}",ops.len(),j1_stages.last());
                    if std::env::var("LOWQ_Q792_DIFF_OPDUMP").ok().as_deref()==Some("1"){
                        let logical=template(block,j);
                        for(i,op)in logical.iter().take(36).enumerate(){
                            eprintln!("Q792_OPDUMP i={i} kind={:?} q2={} q1={} t={} ct={} cc={}",op.kind,op.q_control2.0,op.q_control1.0,op.q_target.0,op.c_target.0,op.c_condition.0);
                        }
                    }
                }
                if block==0&&j==0{j0_stages=super::super::q793_step_r03::marks();j0_cells=super::super::q793_t10_fused_v3::cell_bounds();j0_subs=super::super::q793_r01_dynamic_timefix_r01::sub_bounds();}
                templates.push(ops);
            }
            let first=block*64;let end=(first+64).min(1616);
            for i in 0..end-first{
                let step=first+i;
                let ops=&templates[(step+1)%4];
                if z==0&&i==3{
                    // per-cell cuts inside add_and_clear (j=0, step 3)
                    let main=j0_cells.iter().max_by_key(|(n,_b)|*n);
                    if main.is_none(){
                        for sim in &mut sims{sim.apply_iter(ops.iter());}
                    }else{
                        let cb=&main.unwrap().1;
                        for sim in &mut sims{sim.apply_iter(ops[..cb[0]].iter());}
                        cut(&sims,"block0_j0_pre_add",&mapping,&passenger,owned,&mut snaps);
                        let mut last_cell_end=cb[0];
                        for(ci,&b)in cb.iter().enumerate(){
                            let e=cb.get(ci+1).copied()
                                .or_else(||j0_stages.iter().map(|(_,i)|*i).filter(|i|*i>b).min())
                                .unwrap_or(ops.len()).min(ops.len());
                            for sim in &mut sims{sim.apply_iter(ops[b..e].iter());}
                            let cn:&'static str=Box::leak(format!("block0_j0_cell{ci}").into_boxed_str());
                            cut(&sims,cn,&mapping,&passenger,owned,&mut snaps);
                            last_cell_end=e;
                        }
                        // remaining template in stage chunks per the marks
                        for(name,idx)in j0_stages.iter().copied(){
                            let idx=idx.min(ops.len());
                            if idx<=last_cell_end{continue;}
                            if name=="R01"{
                                let mut p=last_cell_end;
                                for(sn,si)in j0_subs.iter().copied(){
                                    let si=si.min(idx);
                                    if si<=p{continue;}
                                    for sim in &mut sims{sim.apply_iter(ops[p..si].iter());}
                                    let cn:&'static str=Box::leak(format!("block0_j0_r01_{sn}").into_boxed_str());
                                    cut(&sims,cn,&mapping,&passenger,owned,&mut snaps);
                                    p=si;
                                }
                                for sim in &mut sims{sim.apply_iter(ops[p..idx].iter());}
                                let cn:&'static str=Box::leak(format!("block0_j0_r01_tail").into_boxed_str());
                                cut(&sims,cn,&mapping,&passenger,owned,&mut snaps);
                            }else{
                                for sim in &mut sims{sim.apply_iter(ops[last_cell_end..idx].iter());}
                                let cn:&'static str=Box::leak(format!("block0_j0_{name}").into_boxed_str());
                                cut(&sims,cn,&mapping,&passenger,owned,&mut snaps);
                            }
                            last_cell_end=idx;
                        }
                        for sim in &mut sims{sim.apply_iter(ops[last_cell_end..].iter());}
                    }
                }else if z==0&&i==4{
                    // stage-level cuts inside the j=1 template at the first
                    // diverging application (step 4)
                    let mut prev=0usize;
                    for(si,(name,idx))in j1_stages.iter().copied().enumerate(){
                        let idx=idx.min(ops.len());
                        if idx<=prev{continue;}
                        if name=="R01"{
                            let mut p=prev;
                            for(sn,si2)in j1_subs.iter().copied(){
                                let si2=si2.min(idx);
                                if si2<=p{continue;}
                                if sn=="r01_main"{
                                    let mut q=p;
                                    for(mn,mi)in j1_main.iter().copied(){
                                        let mi=mi.min(si2);
                                        if mi<=q{continue;}
                                        for sim in &mut sims{sim.apply_iter(ops[q..mi].iter());}
                                        let cn:&'static str=Box::leak(format!("block0_j1_main_{mn}").into_boxed_str());
                                        cut(&sims,cn,&mapping,&passenger,owned,&mut snaps);
                                        q=mi;
                                    }
                                    for sim in &mut sims{sim.apply_iter(ops[q..si2].iter());}
                                    let cn:&'static str=Box::leak(format!("block0_j1_main_tail").into_boxed_str());
                                    cut(&sims,cn,&mapping,&passenger,owned,&mut snaps);
                                }else{
                                    for sim in &mut sims{sim.apply_iter(ops[p..si2].iter());}
                                    let cn:&'static str=Box::leak(format!("block0_j1_r01_{sn}").into_boxed_str());
                                    cut(&sims,cn,&mapping,&passenger,owned,&mut snaps);
                                }
                                p=si2;
                            }
                            for sim in &mut sims{sim.apply_iter(ops[p..idx].iter());}
                            let cn:&'static str=Box::leak(format!("block0_j1_r01_tail").into_boxed_str());
                            cut(&sims,cn,&mapping,&passenger,owned,&mut snaps);
                        }else if si==1{
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
        // Production emit_reverse brackets the reverse traversal with the
        // loan bracket remapped with inverse=true.
        let loan_rev=remap(loan_bracket_ops(),&rebuilt_map,&passenger,true);
        for sim in &mut sims{sim.apply_iter(loan_rev.iter());}
        cut(&sims,"loan_rev_open",&rebuilt_map,&passenger,owned,&mut snaps);
        // Production emit_schedule reverse uses the MBU measurement-based
        // uncomputation templates (q793_mbu::template with a fresh classical
        // bit), NOT the plain forward templates reversed.
        let measurement=mbu_measurement;
        for z in 0..26{
            let block=25-z;
            let templates:Vec<_>=(0..4).map(|j|{
                if let Some(bit)=measurement{
                    remap(super::super::q793_mbu::template(block,j,bit),&rebuilt_map,&passenger,false)
                }else{
                    remap(template(block,j),&rebuilt_map,&passenger,true)
                }
            }).collect();
            let first=block*64;let end=(first+64).min(1616);
            for i in 0..end-first{
                let step=end-1-i;
                let ops=&templates[(step+1)%4];
                for sim in &mut sims{sim.apply_iter(ops.iter());}
            }
            let name:&'static str=Box::leak(format!("rev_block{block}").into_boxed_str());
            cut(&sims,name,&rebuilt_map,&passenger,owned,&mut snaps);
        }
        for sim in &mut sims{sim.apply_iter(loan_rev.iter());}
        cut(&sims,"loan_rev_close",&rebuilt_map,&passenger,owned,&mut snaps);
        for sim in &mut sims{sim.apply_iter(finishing.iter());}
        let mut state=vec![0u64;257+256];
        for(i,q)in dxo.iter().enumerate(){state[i]=sims[0].qubits[q.id()as usize];}
        for(i,p)in passenger.iter().enumerate(){state[257+i]=sims[0].qubits[p.id()as usize];}
        // per-row finish self-check: dx output bits 0..255 must equal x
        let mut perrow=[0usize;64];
        for lane in 0..64{
            let row=&rows[(0*64+lane)%count];
            for bit in 0..256{
                if (state[bit]>>lane&1)!=((row.0[bit/8]>>(bit%8)&1)as u64){perrow[lane]+=1;}
            }
            if state[256]>>lane&1!=0{perrow[lane]+=1;}
        }
        eprintln!("Q792_FINISH_SELFCHECK four={four} wrong_bits_per_row={perrow:?}",);
        if std::env::var("LOWQ_Q792_DIFF_DUMPX").ok().as_deref()==Some("1"){
            let row=&rows[0];
            let mut out=[0u8;32];let mut inp=[0u8;32];
            for bit in 0..256{
                if (state[bit]&1)!=0{out[bit/8]|=1<<(bit%8);}
                if (row.0[bit/8]>>(bit%8)&1)!=0{inp[bit/8]|=1<<(bit%8);}
            }
            let hs=|b:&[u8]|b.iter().map(|x|format!("{x:02x}")).collect::<String>();
            eprintln!("Q792_X_DUMP four={four} lane0_out={} lane0_in={}",hs(&out),hs(&row.0));
        }
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

/// Production-parity divide-only gate: count_only circuit with a sprint check
/// attached, so the emission flows op-by-op to the sprint sim exactly as the
/// whole-stream does. The check requires the lifecycle to return its inputs
/// unchanged (identity), phase 0, clean ancillas.
pub fn run_sprint(){
    std::env::set_var("POINT_ADD_COUNT_ONLY","1");
    use alloy_primitives::U256;
    let p=U256::from_le_bytes(crate::point_add::trailmix_port::mod_arith::SECP256K1_P_LE);
    let inv=|a:U256|->U256{a.pow_mod(p.wrapping_sub(U256::from(2)),p)};
    let mut rows:Vec<(Vec<u8>,Vec<u8>,Vec<u8>)>=Vec::new();
    let mut s=0x51ef46b9ac287d03u64;
    for _ in 0..24{
        let mut x=[0u8;32];for b in x.iter_mut(){*b=rnd(&mut s)as u8;}x[31]&=0x7f;
        let mut y=[0u8;32];for b in y.iter_mut(){*b=rnd(&mut s)as u8;}y[31]&=0x7f;
        let xu=U256::from_le_bytes(x);let yu=U256::from_le_bytes(y);
        let l=inv(xu).mul_mod(yu,p);
        let lo:[u8;32]=l.to_le_bytes();
        rows.push((x.to_vec(),y.to_vec(),lo.to_vec()));
    }
    for a in 244..=255{
        let mut x=[0u8;32];for b in x.iter_mut(){*b=rnd(&mut s)as u8;}
        for i in 0..256{x[i/8]&=!(1<<(i%8));}
        x[a/8]|=1<<(a%8);
        if a==255{for i in 254..255{x[i/8]&=!(1<<(i%8));}}
        let mut y=[0u8;32];for b in y.iter_mut(){*b=rnd(&mut s)as u8;}y[31]&=0x7f;
        let xu=U256::from_le_bytes(x);let yu=U256::from_le_bytes(y);
        let l=inv(xu).mul_mod(yu,p);
        let lo:[u8;32]=l.to_le_bytes();
        rows.push((x.to_vec(),y.to_vec(),lo.to_vec()));
    }
    if std::env::var("LOWQ_Q792_DIFF_SUBSET").ok().as_deref()==Some("few"){rows.truncate(4);}
    let four_only=std::env::var("LOWQ_Q792_SPRINT_FOUR_ONLY").ok().as_deref()==Some("1");
    for four in if four_only{[true].as_slice()}else{[false,true].as_slice()}{
        std::env::set_var("LOWQ_Q792_EEA",if four{"1"}else{"0"});
        std::env::set_var("Q792_QUOTIENT_TOP_BORROW","0");
        eprintln!("Q792_SPRINT four={four} rows={}",rows.len());
        let mut circ=Circuit::new();
        let dx=circ.alloc_qreg_bits("input",257);
        let dy=circ.alloc_qreg_bits("passenger",257);
        let initial_ops=circ.b.counted_ops;
        circ.b.sprint_sim=Some(crate::point_add::sprint_stream_check::Check::new_divide(&dx,&dy,initial_ops,&rows));
        let (_dxo,_dyo,lambda)=divide_forward(&mut circ,dx,dy);
        let check=circ.b.sprint_sim.take().expect("sprint check attached");
        check.finish_divide(&circ.b,&lambda);
    }
}
