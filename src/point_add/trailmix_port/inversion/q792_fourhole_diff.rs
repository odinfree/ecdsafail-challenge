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
    // Actual layout: logical 0..24 = control (rank/a/c/sm/p1/p2/iter),
    // then work1 (256 rails 3h / 255 rails 4h), then work2 (259 rails both),
    // then 257 passengers.  work1 rails 0..254 exist at the same logical
    // indices 24..278 in both geometries; work2 starts at 280 (3h) / 279 (4h).
    let w1a=if a.skip_w1{a.state.len()-257-259-24}else{0};
    let w1b=if b.skip_w1{b.state.len()-257-259-24}else{0};
    let wa=24+w1a; // work2 start in a
    let wb=24+w1b; // work2 start in b
    // control registers
    for i in 0..24{let j=i;if j<n&&a.state[i]!=b.state[j]{if first.is_none(){first=Some(i);}}}
    // common work1 rails 0..254 (identical logical positions in both)
    if w1cmp{for i in 0..255{if 24+i<wa&&24+i<wb&&a.state[24+i]!=b.state[24+i]{if first.is_none(){first=Some(24+i);}}}}
    // work2 rails, mapped by rail index with the optional shift
    for k in 0..259{let i=wa+k;let k2=if (3..=257).contains(&k){k as i64+w2shift}else{k as i64};let j=(wb as i64+k2).clamp(0,b.state.len()as i64)as usize;
        if i<n&&j<n&&a.state[i]!=b.state[j]{if first.is_none(){first=Some(i);}}}
    // passengers (257, appended in identical order)
    for k in 0..257{let i=a.state.len()-257+k;let j=b.state.len()-257+k;
        if i<n&&j<n&&a.state[i]!=b.state[j]{if first.is_none(){first=Some(i);}}}
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
    if runs[0].1.len()!=runs[1].1.len(){
        eprintln!("Q792_FOURHOLE_DIFF snap counts differ: 3h={} 4h={}",runs[0].1.len(),runs[1].1.len());
    }
    // Pair by cut name so per-geometry stage/cell mark differences do not
    // shift the comparison; every geometry-invariant cut still gets compared.
    for a in &runs[0].1{
        if let Some(b)=runs[1].1.iter().find(|b|b.name==a.name){
            let strict=a.name=="finish";
            compare(a,b,a.name,strict);
        }
    }
    eprintln!("Q792_FOURHOLE_DIFF DRILL COMPLETE cuts_3h={} cuts_4h={}",runs[0].1.len(),runs[1].1.len());
}

/// Production-parity divide-only gate: count_only circuit with a sprint check
/// attached, so the emission flows op-by-op to the sprint sim exactly as the
/// whole-stream does. The check requires the lifecycle to return its inputs
/// unchanged (identity), phase 0, clean ancillas.
pub fn run_sprint(){
    std::env::set_var("POINT_ADD_COUNT_ONLY","1");
    if std::env::var("Q792_SPRINT_FWD_ONLY").ok().as_deref()==Some("1"){
        run_sprint_fwd_only();return;
    }
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
    let fours:Vec<bool>=if four_only{vec![true]}else{vec![false,true]};
    let mut traces:Vec<(bool,Vec<Vec<U256>>)>=Vec::new();
    for four in fours{
        std::env::set_var("LOWQ_Q792_EEA",if four{"1"}else{"0"});
        std::env::set_var("Q792_QUOTIENT_TOP_BORROW","0");
        eprintln!("Q792_SPRINT four={four} rows={}",rows.len());
        let mut circ=Circuit::new();
        let dx=circ.alloc_qreg_bits("input",257);
        let mut dy=circ.alloc_qreg_bits("passenger",257);
        let initial_ops=circ.b.counted_ops;
        circ.b.sprint_sim=Some(crate::point_add::sprint_stream_check::Check::new_divide(&dx,&dy,initial_ops,&rows));
        let (_dxo,_dyo,lambda)=divide_forward(&mut circ,dx,dy);
        if let Some(check)=&circ.b.sprint_sim{traces.push((four,check.trace.borrow().clone()));}
        if traces.len()==2{
            let (blocks3,blocks4)=(&traces[0].1,&traces[1].1);
            eprintln!("Q792_SPRINT_W2_TRACE blocks_3h={} blocks_4h={}",blocks3.len(),blocks4.len());
            let mut reported=false;
            for b in 0..blocks3.len().min(blocks4.len()){
                for lane in 0..64{
                    if blocks3[b][lane]!=blocks4[b][lane]{
                        eprintln!("Q792_SPRINT_W2_TRACE first_divergence block={b} lane={lane} w2_3h={} w2_4h={}",blocks3[b][lane],blocks4[b][lane]);
                        reported=true;break;
                    }
                }
                if reported{break;}
            }
            if !reported{eprintln!("Q792_SPRINT_W2_TRACE all blocks identical");}
        }
        let check=circ.b.sprint_sim.take().expect("sprint check attached");
        check.finish_divide(&circ.b,&lambda);
    }
}

/// Forward-only localization: initialize + emit_forward in both geometries on
/// identical rows, tracing work2 after every block; report the first divergent
/// block/lane.  Skips release/rebuild/mod_mul so each geometry costs roughly
/// half the full divide sprint.
pub fn run_sprint_fwd_only(){
    std::env::set_var("Q792_SPRINT_W2_TRACE","1");
    std::env::set_var("Q792_SPRINT_W2_TRACE_STEP","1");
    use alloy_primitives::U256;
    let p=U256::from_le_bytes(crate::point_add::trailmix_port::mod_arith::SECP256K1_P_LE);
    let inv=|a:U256|->U256{a.pow_mod(p.wrapping_sub(U256::from(2)),p)};
    let mut rows:Vec<(Vec<u8>,Vec<u8>,Vec<u8>)>=Vec::new();
    let mut s=0x51ef46b9ac287d03u64;
    for _ in 0..24{
        let mut x=[0u8;32];for b in x.iter_mut(){*b=rnd(&mut s)as u8;}x[31]&=0x7f;
        let mut y=[0u8;32];for b in y.iter_mut(){*b=rnd(&mut s)as u8;}y[31]&=0x7f;
        let xu=U256::from_le_bytes(x);let yu=U256::from_le_bytes(y);
        let l=inv(xu).mul_mod(yu,p);let lo:[u8;32]=l.to_le_bytes();
        rows.push((x.to_vec(),y.to_vec(),lo.to_vec()));
    }
    for a in 244..=255{
        let mut x=[0u8;32];for b in x.iter_mut(){*b=rnd(&mut s)as u8;}
        for i in 0..256{x[i/8]&=!(1<<(i%8));}
        x[a/8]|=1<<(a%8);
        if a==255{for i in 254..255{x[i/8]&=!(1<<(i%8));}}
        let mut y=[0u8;32];for b in y.iter_mut(){*b=rnd(&mut s)as u8;}y[31]&=0x7f;
        let xu=U256::from_le_bytes(x);let yu=U256::from_le_bytes(y);
        let l=inv(xu).mul_mod(yu,p);let lo:[u8;32]=l.to_le_bytes();
        rows.push((x.to_vec(),y.to_vec(),lo.to_vec()));
    }
    rows.truncate(4);
    let mut traces:Vec<(bool,Vec<Vec<U256>>)>=Vec::new();
    for four in [false,true]{
        std::env::set_var("LOWQ_Q792_EEA",if four{"1"}else{"0"});
        std::env::set_var("Q792_QUOTIENT_TOP_BORROW","0");
        eprintln!("Q792_SPRINT_FWD four={four} rows={}",rows.len());
        let mut circ=Circuit::new();
        let dx=circ.alloc_qreg_bits("input",257);
        let mut dy=circ.alloc_qreg_bits("passenger",257);
        let initial_ops=circ.b.counted_ops;
        circ.b.sprint_sim=Some(crate::point_add::sprint_stream_check::Check::new_divide(&dx,&dy,initial_ops,&rows));
        let released=loan_canonical_top(&mut circ,&mut dy,"fwd-trace dy");
        let core=initialize(&mut circ,dx,&dy[0],&dy[1]);
        emit_forward(&mut circ,&core,&dy);
        restore_canonical_top(&mut circ,&mut dy,released);
        if let Some(check)=&circ.b.sprint_sim{traces.push((four,check.trace.borrow().clone()));}
    }
    if traces.len()==2{
        let (b3,b4)=(&traces[0].1,&traces[1].1);
        eprintln!("Q792_SPRINT_W2_TRACE steps_3h={} steps_4h={}",b3.len(),b4.len());
        let mut reported=false;
        for blk in 0..b3.len().min(b4.len()){
            for lane in 0..64{
                if b3[blk][lane]!=b4[blk][lane]{
                    eprintln!("Q792_SPRINT_W2_TRACE first_divergence step={blk} block={} template_j={} lane={lane} w2_3h={} w2_4h={}",blk/8,(blk+1)%4,b3[blk][lane],b4[blk][lane]);
                    let mut xors=String::new();
                    for l in 0..64{
                        let x=b3[blk][l]^b4[blk][l];
                        let bytes:[u8;32]=x.to_be_bytes();
                        let mut s=String::new();for bb in bytes.iter().rev().take(4).rev(){s.push_str(&format!("{bb:02x}"));}
                        if x!=alloy_primitives::U256::ZERO{xors.push_str(&format!("{l}:{s} "));}
                    }
                    eprintln!("Q792_SPRINT_W2_TRACE step{blk}_xor_low4bytes={xors}");
                    reported=true;break;
                }
            }
            if reported{break;}
        }
        if !reported{eprintln!("Q792_SPRINT_W2_TRACE all blocks identical");}
    }
}

/// Static diagnostic: emit block/j templates in both geometries and dump the
/// ops touching the given work2 rails (logical ids 283+rail), to diff the
/// write structure around a localized divergence rail.
pub fn run_template_opdiff(){
    let block:usize=std::env::var("Q792_OPDIFF_BLOCK").ok().map(|v|v.parse().unwrap()).unwrap_or(0);
    let j:usize=std::env::var("Q792_OPDIFF_J").ok().map(|v|v.parse().unwrap()).unwrap_or(2);
    let rail:usize=std::env::var("Q792_OPDIFF_RAIL").ok().map(|v|v.parse().unwrap()).unwrap_or(2);
    let base=283+rail; // template logical: rank/a/c/sm/p1/p2/iter=24, w1=259 -> w2 starts at 283
    for four in [false,true]{
        std::env::set_var("LOWQ_Q792_EEA",if four{"1"}else{"0"});
        let ops=template(block,j);
        eprintln!("Q792_OPDIFF four={four} block={block} j={j} rail={rail} (logical {base}) total_ops={}",ops.len());
        for (i,op)in ops.iter().enumerate(){
            if op.q_target.0==base as u64||op.q_control1.0==base as u64||op.q_control2.0==base as u64||
               (base+1..base+4).any(|r|op.q_target.0==r as u64||op.q_control1.0==r as u64||op.q_control2.0==r as u64){
                eprintln!("Q792_OPDIFF four={four} i={i} kind={:?} q2={} q1={} t={} ct={} cc={}",op.kind,op.q_control2.0,op.q_control1.0,op.q_target.0,op.c_target.0,op.c_condition.0);
            }
        }
    }
}

/// Empirical template bisect: replay steps 0..4, then apply the step-5
/// template in fixed-size op chunks in BOTH geometries on the same inputs and
/// trace the work2 value after every chunk.  The 3-hole chunk values are the
/// correct evolution; the first 4-hole chunk whose value is foreign to the
/// 3-hole sequence pins the buggy op range.
pub fn run_template_bisect(){
    std::env::set_var("POINT_ADD_COUNT_ONLY","1");
    std::env::set_var("Q793_FRAME","0");
    std::env::set_var("Q792_NO_CANCEL","1");
    std::env::set_var("Q794_TFACTOR","0");
    std::env::set_var("Q795_STAGE_CENSUS","1");
    use alloy_primitives::U256;
    let block=0usize;let step=5;let tj=(step+1)%4; // template index for global step 5
    let p=U256::from_le_bytes(crate::point_add::trailmix_port::mod_arith::SECP256K1_P_LE);
    let inv=|a:U256|->U256{a.pow_mod(p.wrapping_sub(U256::from(2)),p)};
    let mut rows:Vec<(Vec<u8>,Vec<u8>,Vec<u8>)>=Vec::new();
    let mut s=0x51ef46b9ac287d03u64;
    for _ in 0..4{
        let mut x=[0u8;32];for b in x.iter_mut(){*b=rnd(&mut s)as u8;}x[31]&=0x7f;
        let mut y=[0u8;32];for b in y.iter_mut(){*b=rnd(&mut s)as u8;}y[31]&=0x7f;
        let xu=U256::from_le_bytes(x);let yu=U256::from_le_bytes(y);
        let l=inv(xu).mul_mod(yu,p);let lo:[u8;32]=l.to_le_bytes();
        rows.push((x.to_vec(),y.to_vec(),lo.to_vec()));
    }
    let mut seqs:Vec<(bool,Vec<Vec<U256>>)>=Vec::new();
    for four in [false,true]{
        std::env::set_var("LOWQ_Q792_EEA",if four{"1"}else{"0"});
        std::env::set_var("Q792_QUOTIENT_TOP_BORROW","0");
        let mut circ=Circuit::new();
        let dx=circ.alloc_qreg_bits("input",257);
        let mut dy=circ.alloc_qreg_bits("passenger",257);
        let initial_ops=circ.b.counted_ops;
        circ.b.sprint_sim=Some(crate::point_add::sprint_stream_check::Check::new_divide(&dx,&dy,initial_ops,&rows));
        let released=loan_canonical_top(&mut circ,&mut dy,"bisect dy");
        let core=initialize(&mut circ,dx,&dy[0],&dy[1]);
        let mapping=ids(&core);
        // steps 0..4 use templates (s+1)%4 = 1,2,3,0,1
        for st in 0..step{
            let ops=remap(template(block,(st+1)%4),&mapping,&dy,false);
            if let Some(check)=&mut circ.b.sprint_sim{check.apply(&ops);}
        }
        // stage-apply the step-5 template (no-cancel keeps marks aligned)
        let logical=template(block,tj);
        let ops=remap(logical.clone(),&mapping,&dy,false);
        let marks=super::super::q793_step_r03::marks();
        let boundaries:Vec<usize>=marks.iter().map(|&(_,i)|i).filter(|&i|i>0&&i<ops.len()).collect();
        let mut seq=Vec::new();
        let mut prev=0;
        for &b in boundaries.iter().chain(std::iter::once(&ops.len())){
            circ.b.sprint_sim.as_mut().unwrap().apply(&ops[prev..b]);
            let mut row=Vec::with_capacity(64);
            for lane in 0..64{
                row.push(circ.b.sprint_sim.as_ref().unwrap().read_w2(&core.work2[..257],lane));
            }
            seq.push(row);
            prev=b;
        }
        restore_canonical_top(&mut circ,&mut dy,released);
        seqs.push((four,seq));
        eprintln!("Q792_BISECT four={four} marks={:?} boundaries={:?} ops={}",marks.iter().map(|&(n,i)|(n,i)).collect::<Vec<_>>(),boundaries,ops.len());
    }
    // 3-hole value set per chunk index is NOT position-aligned across
    // geometries; instead collect the multiset of all 3-hole visited values
    // per lane and find the first 4-hole value outside it.
    let (seq3,seq4)=(&seqs[0].1,&seqs[1].1);
    eprintln!("Q792_BISECT stages_3h={} stages_4h={}",seq3.len(),seq4.len());
    for (ci,(r3,r4))in seq3.iter().zip(seq4.iter()).enumerate(){
        let mut xors=String::new();
        for lane in 0..4{
            let x=r3[lane]^r4[lane];
            let bytes:[u8;32]=x.to_be_bytes();
            let mut s=String::new();
            for b in bytes.iter().take(32){s.push_str(&format!("{b:02x}"));}
            if xors.is_empty(){xors=s;}else{xors.push(' ');xors.push_str(&s);}
        }
        eprintln!("Q792_BISECT stage{ci} xor_lanes0_3={xors}");
    }
    let mut found=None;
    'outer: for (ci,row) in seq4.iter().enumerate(){
        for lane in 0..64{
            let want=seq3.get(ci).map(|r|r[lane]);
            if let Some(w)=want{
                if w!=row[lane]{found=Some((ci,lane,w,row[lane]));break 'outer;}
            }else{
                found=Some((ci,lane,row[lane],row[lane]));break 'outer;
            }
        }
    }
    match found{
        Some((ci,lane,want,got))=>eprintln!("Q792_BISECT first_stage_divergence stage_idx={ci} lane={lane} w2_3h={want} w2_4h={got}"),
        None=>{
            if seq3.len()==seq4.len(){eprintln!("Q792_BISECT all stages identical");}
            else{eprintln!("Q792_BISECT stage counts differ");}
        }
    }
}

/// R01 differential falsifier: run q793_r01_dynamic_timefix_r01::signless in
/// both geometries on identical logical states and compare every rail that
/// must agree (rank/a/c/sm/p1/p2/iter, work2, helpers, w1[0..255]).  Random
/// off-guard states are legal - the body restores everything off g.
pub fn run_r01_diff(){
    use crate::sim::Simulator;
    let rows=64usize;
    let mut out:Vec<(bool,Vec<Vec<u64>>,Vec<(&'static str,usize)>,Vec<(&'static str,u64,u64,u64,u64)>,Vec<u64>)>=Vec::new();
    for four in [false,true]{
        std::env::set_var("LOWQ_Q792_EEA",if four{"1"}else{"0"});
        let mut circ=Circuit::new();
        let rank=circ.alloc_qreg_bits("rank",5);let a=circ.alloc_qreg_bits("a",6);let c=circ.alloc_qreg_bits("c",6);let sm=circ.alloc_qreg_bits("sm",4);
        let p1=circ.alloc_qreg("p1");let p2=circ.alloc_qreg("p2");let iter=circ.alloc_qreg("iter");
        let w1=circ.alloc_qreg_bits("w1",259);let w2=circ.alloc_qreg_bits("w2",259);
        let helpers=circ.alloc_qreg_bits("helpers",23);
        circ.q797_a_support=Some((0,5));
        let owned=circ.b.next_qubit as usize;
        super::super::q793_r01_normal_timefix_r01::clear_main_bounds();
        super::super::q793_r01_dynamic_timefix_r01::clear_sub_bounds();
        super::super::q793_r01_dynamic_timefix_r01::signless(&mut circ,&rank,&a,&c,&sm,&p1,&p2,&w1,&w2,&helpers,1,257);
        let bounds=super::super::q793_r01_dynamic_timefix_r01::sub_bounds();
        let b=circ.into_builder();
        let mkstate=|lane:usize,owned:usize|->Vec<u64>{
            let mut state=vec![0u64;owned];
            let mut seed=0x793_6015eedu64^((lane as u64)<<48);
            for q in 0..owned{state[q]=rnd(&mut seed);}
            state[w1[255].id()as usize]=u64::MAX; // omitted p-bit-3: constant 1
            // structured active-domain state, mirroring the numeric seed check:
            // g=1, ha=decision=0, mask(p1)=1, p2=0, sm=0, a in the support.
            let rk=(lane%32)as u64;let av=2u64;
            for i in 0..5{state[rank[i].id()as usize]=(rk>>i&1)as u64*u64::MAX;}
            for i in 0..6{state[a[i].id()as usize]=(av>>i&1)as u64*u64::MAX;}
            for i in 0..4{state[sm[i].id()as usize]=0;}
            state[helpers[0].id()as usize]=u64::MAX; // g=1
            state[helpers[1].id()as usize]=0;         // ha=0
            state[helpers[2].id()as usize]=0;         // decision=0
            state[p1.id()as usize]=0;                 // mask starts 0 (flag/lower set it)
            state[p2.id()as usize]=0;
            // shared-domain chart on even lanes: zero the 4th rails
            if lane%2==0{
                state[w2[3].id()as usize]=0;
                state[w2[255].id()as usize]=0;
                state[w1[3].id()as usize]=0;
            }
            // reachability: (t|v)&1==1 -> if t0=0 then v0=1
            for bit in 0..64{
                let t0=(state[w1[0].id()as usize]>>bit)&1;
                let v0=(state[w2[258].id()as usize]>>bit)&1;
                if t0==0{state[w2[258].id()as usize]|=1<<bit;}
            }
            state
        };
        // lane-0 sub-stage trace of w2[1]
        let mut rng=Fixed(0x51ef46b9ac287d03u64);
        let mut sim=Simulator::new(owned,0,&mut rng);
        sim.qubits=mkstate(0,owned);sim.phase=0;
        let mut trace=Vec::new();
        let mut prev=0;
        // merge the r01_main internal marks into the boundary list
        let mut merged:Vec<(&'static str,usize)>=bounds.clone();
        let ms=bounds.iter().position(|&(n,_)|n=="r01_main").map(|p|(bounds[p-1].1,bounds[p].1)).unwrap_or((0,0));
        for k in 1..10{
            let pos=ms.0+(ms.1-ms.0)*k/10;
            merged.push((Box::leak(format!("main_{k}0%").into_boxed_str()),pos));
        }
        merged.sort_by_key(|&(_,i)|i);merged.dedup_by_key(|&mut(_,i)|i);
        for &(name,idx) in merged.iter().chain(std::iter::once(&("end",b.ops.len()))){
            if idx>prev{sim.apply_iter(b.ops[prev..idx].iter());}
            trace.push((name,sim.qubits[p1.id()as usize],sim.qubits[sm[0].id()as usize],sim.qubits[sm[1].id()as usize],sim.qubits[helpers[1].id()as usize]));
            prev=idx;
        }
        // op-level w2[2] write sequence within r01_main (lane 0 bit)
        if four{
            let ms=bounds.iter().position(|&(n,_)|n=="r01_main").map(|p|(bounds[p-1].1,bounds[p].1)).unwrap_or((0,0));
            let mut rng2=Fixed(0x51ef46b9ac287d03u64);
            let mut sim2=Simulator::new(owned,0,&mut rng2);
            sim2.qubits=mkstate(0,owned);sim2.phase=0;
            sim2.apply_iter(b.ops[..ms.0].iter());
            let mut seq=Vec::new();
            let mut last=sim2.qubits[w2[2].id()as usize];
            for (k,op) in b.ops[ms.0..ms.1].iter().enumerate(){
                sim2.apply_iter(std::slice::from_ref(op).iter());
                let cur=sim2.qubits[w2[2].id()as usize];
                if cur!=last{seq.push((k,op.kind,op.q_target.0,op.q_control1.0,op.q_control2.0,cur&1));last=cur;}
            }
            eprintln!("Q792_R01_DIFF w2[2]_write_seq_4h lane0={:?}",seq.iter().map(|&(k,kind,t,q1,q2,b)|(k,format!("{kind:?}"),t,q1,q2,b)).collect::<Vec<_>>());
            eprintln!("Q792_R01_DIFF 4h_main_first30={:?}",b.ops[ms.0..ms.0+30].iter().enumerate().map(|(k,o)|(k,format!("{:?}",o.kind),o.q_target.0,o.q_control1.0,o.q_control2.0)).collect::<Vec<_>>());
            eprintln!("Q792_R01_DIFF 4h_around_first_w2[2]_write={:?}",b.ops[ms.0+4438..ms.0+4456].iter().enumerate().map(|(k,o)|(4438+k,format!("{:?}",o.kind),o.q_target.0,o.q_control1.0,o.q_control2.0)).collect::<Vec<_>>());
            // ha write sequence (first ~40 toggles)
            let mut rng3=Fixed(0x51ef46b9ac287d03u64);
            let mut sim3=Simulator::new(owned,0,&mut rng3);
            sim3.qubits=mkstate(0,owned);sim3.phase=0;
            sim3.apply_iter(b.ops[..ms.0].iter());
            let mut hseq=Vec::new();
            let mut hlast=sim3.qubits[helpers[1].id()as usize];
            for (k,op) in b.ops[ms.0..ms.1].iter().enumerate(){
                sim3.apply_iter(std::slice::from_ref(op).iter());
                let h=sim3.qubits[helpers[1].id()as usize];
                if h!=hlast{hseq.push((k,op.kind,op.q_target.0,op.q_control1.0,op.q_control2.0,h&0xff));hlast=h;}
            }
            eprintln!("Q792_R01_DIFF ha_write_seq_4h={:?}",hseq.iter().map(|&(k,k2,t,q1,q2,b)|(k,format!("{k2:?}"),t,q1,q2,b)).collect::<Vec<_>>());
        }else{
            let ms=bounds.iter().position(|&(n,_)|n=="r01_main").map(|p|(bounds[p-1].1,bounds[p].1)).unwrap_or((0,0));
            let mut rng2=Fixed(0x51ef46b9ac287d03u64);
            let mut sim2=Simulator::new(owned,0,&mut rng2);
            sim2.qubits=mkstate(0,owned);sim2.phase=0;
            sim2.apply_iter(b.ops[..ms.0].iter());
            let mut seq=Vec::new();
            let mut last=sim2.qubits[w2[2].id()as usize];
            for (k,op) in b.ops[ms.0..ms.1].iter().enumerate(){
                sim2.apply_iter(std::slice::from_ref(op).iter());
                let cur=sim2.qubits[w2[2].id()as usize];
                if cur!=last{seq.push((k,op.kind,op.q_target.0,op.q_control1.0,op.q_control2.0,cur&1));last=cur;}
            }
            eprintln!("Q792_R01_DIFF w2[2]_write_seq_3h lane0={:?}",seq.iter().map(|&(k,kind,t,q1,q2,b)|(k,format!("{kind:?}"),t,q1,q2,b)).collect::<Vec<_>>());
            let mut rng3=Fixed(0x51ef46b9ac287d03u64);
            let mut sim3=Simulator::new(owned,0,&mut rng3);
            sim3.qubits=mkstate(0,owned);sim3.phase=0;
            sim3.apply_iter(b.ops[..ms.0].iter());
            let mut hseq=Vec::new();
            let mut hlast=sim3.qubits[helpers[1].id()as usize];
            for (k,op) in b.ops[ms.0..ms.1].iter().enumerate(){
                sim3.apply_iter(std::slice::from_ref(op).iter());
                let h=sim3.qubits[helpers[1].id()as usize];
                if h!=hlast{hseq.push((k,op.kind,op.q_target.0,op.q_control1.0,op.q_control2.0,h&0xff));hlast=h;}
            }
            eprintln!("Q792_R01_DIFF ha_write_seq_3h={:?}",hseq.iter().map(|&(k,k2,t,q1,q2,b)|(k,format!("{k2:?}"),t,q1,q2,b)).collect::<Vec<_>>());
        }
        let entry_snap={
            // full-state diff at the endpoints entry (lane 0)
            let ms=bounds.iter().position(|&(n,_)|n=="normal_guard_rev").map(|p|(bounds[p].1,bounds[p+1].1)).unwrap_or((0,0));
            let mut rng2=Fixed(0x51ef46b9ac287d03u64);
            let mut sim2=Simulator::new(owned,0,&mut rng2);
            sim2.qubits=mkstate(0,owned);sim2.phase=0;
            sim2.apply_iter(b.ops[..ms.1].iter());
            sim2.qubits.clone()
        };
        let mut states=Vec::new();
        for lane in 0..rows{
            sim.qubits=mkstate(lane,owned);
            sim.phase=0;
            sim.apply_iter(b.ops.iter());
            let mut row:Vec<u64>=rank.iter().chain(&a).chain(&c).chain(&sm).chain([&p1,&p2,&iter]).chain(&w2).chain(&helpers).chain(&w1[..255]).map(|q|sim.qubits[q.id()as usize]).collect();
            row.push(sim.phase);
            states.push(row);
        }
        out.push((four,states,bounds,trace,entry_snap));
    }
    let (s3,s4)=(&out[0].1,&out[1].1);
    let mut first=None;
    'outer: for lane in 0..rows{
        for i in 0..s3[lane].len(){
            if s3[lane][i]!=s4[lane][i]{first=Some((lane,i,s3[lane][i],s4[lane][i]));break 'outer;}
        }
    }
    eprintln!("Q792_R01_DIFF bounds_3h={:?}",out[0].2.iter().map(|&(n,i)|(n,i)).collect::<Vec<_>>());
    eprintln!("Q792_R01_DIFF bounds_4h={:?}",out[1].2.iter().map(|&(n,i)|(n,i)).collect::<Vec<_>>());
    let fmt=|t:&Vec<(&'static str,u64,u64,u64,u64)>|t.iter().map(|&(n,mask,sm0,sm1,ha)|(n,format!("mask={mask:#018x} sm0={sm0:#018x} sm1={sm1:#018x} ha={ha:#018x}"))).collect::<Vec<_>>();
    eprintln!("Q792_R01_DIFF lane0_trace_3h={:?}",fmt(&out[0].3));
    eprintln!("Q792_R01_DIFF lane0_trace_4h={:?}",fmt(&out[1].3));
    match first{
        Some((lane,i,v3,v4))=>eprintln!("Q792_R01_DIFF first_divergence lane={lane} rail={i} (0..24 meta,24..283 w2,283..306 helpers,306.. w1[0..255],last phase) 3h={v3:#018x} 4h={v4:#018x}"),
        None=>eprintln!("Q792_R01_DIFF all rows identical"),
    }
    let mut diffs=Vec::new();
    for i in 0..out[0].4.len().min(out[1].4.len()){
        if out[0].4[i]!=out[1].4[i]{diffs.push((i,out[0].4[i],out[1].4[i]));}
    }
    eprintln!("Q792_R01_DIFF endpoints_entry_diffs={:?}",diffs.iter().take(12).map(|&(i,a,b)|(i,format!("{a:#018x}"),format!("{b:#018x}"))).collect::<Vec<_>>());
}

/// Full-step differential: simulate template(block,j) (the whole step incl.
/// T10/R00/cargo/entry/sign/exit) in both geometries on identical logical
/// states and diff every rail except the geometry-dependent w1.
pub fn run_step_diff(){
    use crate::sim::Simulator;
    let block:usize=std::env::var("Q792_STEPDIFF_BLOCK").ok().map(|v|v.parse().unwrap()).unwrap_or(0);
    let j:usize=std::env::var("Q792_STEPDIFF_J").ok().map(|v|v.parse().unwrap()).unwrap_or(2);
    let mut ops:Vec<(bool,Vec<crate::circuit::Op>)>=Vec::new();
    for four in [false,true]{
        std::env::set_var("LOWQ_Q792_EEA",if four{"1"}else{"0"});
        ops.push((four,template(block,j)));
    }
    let owned=565+2; // template logical: 24 + 259 + 259 + 23
    let mut first=None;
    for lane in 0..512{
        let mut state=vec![0u64;owned];
        let mut seed=0x793_6015eedu64^((lane as u64)<<48);
        for q in 0..owned{state[q]=rnd(&mut seed);}
        state[24+255]=u64::MAX; // w1[255] = the omitted p-bit-3 constant
        let mut outs=Vec::new();
        for (four,o) in &ops{
            let mut rng=Fixed(0x51ef46b9ac287d03u64);
            let mut sim=Simulator::new(owned,0,&mut rng);
            sim.qubits=state.clone();sim.phase=0;
            sim.apply_iter(o.iter());
            // meta(24) + w2(259) + helpers(23) + phase
            let mut row:Vec<u64>=(0..24).map(|q|sim.qubits[q]).collect();
            row.extend((283..542).map(|q|sim.qubits[q]));
            row.extend((542..565).map(|q|sim.qubits[q]));
            row.push(sim.phase);
            let _=four;
            outs.push(row);
        }
        for i in 0..outs[0].len(){
            if outs[0][i]!=outs[1][i]{first=Some((lane,i,outs[0][i],outs[1][i]));break;}
        }
        if first.is_some(){break;}
    }
    match first{
        Some((lane,i,v3,v4))=>eprintln!("Q792_STEP_DIFF block={block} j={j} first_divergence lane={lane} rail={i} (0..24 meta,24..283 w2,283..306 helpers,306 phase) 3h={v3:#018x} 4h={v4:#018x}"),
        None=>eprintln!("Q792_STEP_DIFF block={block} j={j} all states identical"),
    }
    // full rail diff for lane 0
    {
        let mut state=vec![0u64;owned];
        let mut seed=0x793_6015eedu64;
        for q in 0..owned{state[q]=rnd(&mut seed);}
        state[24+255]=u64::MAX;
        let mut outs=Vec::new();
        for (_four,o) in &ops{
            let mut rng=Fixed(0x51ef46b9ac287d03u64);
            let mut sim=Simulator::new(owned,0,&mut rng);
            sim.qubits=state.clone();sim.phase=0;
            sim.apply_iter(o.iter());
            outs.push(sim.qubits.clone());
        }
        let mut diffs=Vec::new();
        for q in 0..owned{
            if outs[0][q]!=outs[1][q]{diffs.push((q,outs[0][q],outs[1][q]));}
        }
        eprintln!("Q792_STEP_DIFF lane0_diffs={:?}",diffs.iter().map(|&(q,a,b)|(q,format!("{a:#018x}"),format!("{b:#018x}"))).collect::<Vec<_>>());
    }
}

/// Production-state stage bisect: run the real forward walk to step 4, then
/// apply the step-5 template stage by stage (no-cancel emission keeps the
/// stage marks aligned) in both geometries and report the first stage whose
/// work2 output diverges.
pub fn run_step_bisect(){
    std::env::set_var("POINT_ADD_COUNT_ONLY","1");
    std::env::set_var("Q792_NO_CANCEL","1");
    std::env::set_var("Q793_FRAME","0");
    std::env::set_var("Q794_TFACTOR","0");
    std::env::set_var("Q795_STAGE_CENSUS","1");
    use alloy_primitives::U256;
    let p=U256::from_le_bytes(crate::point_add::trailmix_port::mod_arith::SECP256K1_P_LE);
    let inv=|a:U256|->U256{a.pow_mod(p.wrapping_sub(U256::from(2)),p)};
    let mut rows:Vec<(Vec<u8>,Vec<u8>,Vec<u8>)>=Vec::new();
    let mut s0=0x51ef46b9ac287d03u64;
    for _ in 0..4{
        let mut x=[0u8;32];for b in x.iter_mut(){*b=rnd(&mut s0)as u8;}x[31]&=0x7f;
        let mut y=[0u8;32];for b in y.iter_mut(){*b=rnd(&mut s0)as u8;}y[31]&=0x7f;
        let xu=U256::from_le_bytes(x);let yu=U256::from_le_bytes(y);
        let l=inv(xu).mul_mod(yu,p);let lo:[u8;32]=l.to_le_bytes();
        rows.push((x.to_vec(),y.to_vec(),lo.to_vec()));
    }
    let block:usize=std::env::var("Q792_STEPBISECT_BLOCK").ok().map(|v|v.parse().unwrap()).unwrap_or(0);
    let step:usize=std::env::var("Q792_STEPBISECT_STEP").ok().map(|v|v.parse().unwrap()).unwrap_or(5);
    let tj=(step+1)%4;
    let mut out:Vec<(bool,Vec<(&'static str,U256,u64,u64,u64,u64,u64,u64,u64)>,Vec<(&'static str,usize)>,Vec<Vec<u64>>,Vec<Vec<u64>>,Vec<Op>)>=Vec::new();
    for four in [false,true]{
        std::env::set_var("LOWQ_Q792_EEA",if four{"1"}else{"0"});
        std::env::set_var("Q792_QUOTIENT_TOP_BORROW","0");
        let mut circ=Circuit::new();
        let dx=circ.alloc_qreg_bits("input",257);
        let mut dy=circ.alloc_qreg_bits("passenger",257);
        let initial_ops=circ.b.counted_ops;
        circ.b.sprint_sim=Some(crate::point_add::sprint_stream_check::Check::new_divide(&dx,&dy,initial_ops,&rows));
        let released=loan_canonical_top(&mut circ,&mut dy,"step-bisect dy");
        let core=initialize(&mut circ,dx,&dy[0],&dy[1]);
        let mapping=ids(&core);
        let mut step_snaps:Vec<Vec<u64>>=Vec::new();
        for st in 0..step{
            let ops=remap(template(block,(st+1)%4),&mapping,&dy,false);
            if let Some(check)=&mut circ.b.sprint_sim{
                check.apply(&ops);
                let snap=check.snapshot();
                let mut words:Vec<u64>=core.rank.iter().chain(&core.a).chain(&core.c).chain(&core.sm).map(|q|snap[q.id()as usize]).collect();
                words.push(snap[core.phase1.id()as usize]);
                words.push(snap[core.phase2.id()as usize]);
                words.extend(core.work2.iter().map(|q|snap[q.id()as usize]));
                step_snaps.push(words);
            }
        }
        let logical=template(block,tj);
        let ops=remap(logical.clone(),&mapping,&dy,false);
        let marks=super::super::q793_step_r03::marks();
        if std::env::var("Q792_STEPBISECT_DUMP_SPAN").ok().as_deref()==Some("1"){
            let lo=marks.iter().find(|&(n,_)|*n=="counter").unwrap().1;
            let hi=marks.iter().find(|&(n,_)|*n=="entry_transfer").unwrap().1;
            for (k,o) in logical[lo..hi].iter().enumerate(){
                eprintln!("SPANLOG four={four} {k} k{} t{} q1{} q2{}",o.kind as u8,o.q_target.0,o.q_control1.0,o.q_control2.0);
            }
        }
        {
            // dump the entry_transfer span ops (between entry_transfer and newborn marks)
            let p1=marks.iter().position(|&(n,_)|n=="counter");
            let p2=marks.iter().position(|&(n,_)|n=="entry_transfer");
            if let (Some(a),Some(b))=(p1,p2){
                let span=&ops[marks[a].1..marks[b].1];
                eprintln!("Q792_STEP_BISECT four={four} entry_transfer_span ops={} first10={:?}",span.len(),span.iter().take(10).map(|o|(format!("{:?}",o.kind),o.q_target.0,o.q_control1.0,o.q_control2.0)).collect::<Vec<_>>());
                // c[1] write sequence over the span (lane 2)
                let mut rng4=Fixed(0x51ef46b9ac287d03u64);
                let mut sim4=Simulator::new(circ.b.next_qubit as usize,0,&mut rng4);
                sim4.qubits=circ.b.sprint_sim.as_ref().unwrap().snapshot();
                sim4.apply_iter(ops[..marks[a].1].iter());
                let mut seq=Vec::new();let mut last=sim4.qubits[core.c[1].id()as usize];
                for (k,op) in span.iter().enumerate(){
                    sim4.apply_iter(std::slice::from_ref(op).iter());
                    let cur=sim4.qubits[core.c[1].id()as usize];
                    if cur!=last{seq.push((k,op.kind as u8,op.q_target.0,op.q_control1.0,op.q_control2.0,(cur>>2)&1));last=cur;}
                }
                eprintln!("Q792_STEP_BISECT four={four} c1_write_seq={:?}",seq.iter().map(|&(k,k2,t,q1,q2,b)|(k,k2,t,q1,q2,b)).collect::<Vec<_>>());
                // c[0] full-word write sequence over the same span
                let mut rng7=Fixed(0x51ef46b9ac287d03u64);
                let mut sim7=Simulator::new(circ.b.next_qubit as usize,0,&mut rng7);
                sim7.qubits=circ.b.sprint_sim.as_ref().unwrap().snapshot();
                sim7.apply_iter(ops[..marks[a].1].iter());
                let mut seq0=Vec::new();let mut last0=sim7.qubits[core.c[0].id()as usize];
                for (k,op) in span.iter().enumerate(){
                    sim7.apply_iter(std::slice::from_ref(op).iter());
                    let cur=sim7.qubits[core.c[0].id()as usize];
                    if cur!=last0{seq0.push((k,op.kind as u8,op.q_target.0,op.q_control1.0,op.q_control2.0,cur));last0=cur;}
                }
                eprintln!("Q792_STEP_BISECT four={four} c0_write_seq={:?}",seq0.iter().map(|&(k,k2,t,q1,q2,w)|(k,k2,t,q1,q2,format!("{w:#018x}"))).collect::<Vec<_>>());
                {
                    let mut rng9=Fixed(0x51ef46b9ac287d03u64);
                    let mut sim9=Simulator::new(circ.b.next_qubit as usize,0,&mut rng9);
                    sim9.qubits=circ.b.sprint_sim.as_ref().unwrap().snapshot();
                    sim9.apply_iter(ops[..marks[a].1].iter());
                    let mut seqa=Vec::new();let mut lasta=sim9.qubits[core.a[1].id()as usize];
                    for (k,op) in span.iter().enumerate(){
                        sim9.apply_iter(std::slice::from_ref(op).iter());
                        let cur=sim9.qubits[core.a[1].id()as usize];
                        if cur!=lasta{seqa.push((k,op.kind as u8,op.q_target.0,op.q_control1.0,op.q_control2.0,cur));lasta=cur;}
                    }
                    eprintln!("Q792_STEP_BISECT four={four} a1_write_seq={:?}",seqa.iter().map(|&(k,k2,t,q1,q2,w)|(k,k2,t,q1,q2,format!("{w:#018x}"))).collect::<Vec<_>>());
                }
                for r in [1usize,2,3,4,5]{
                    let mut rng8=Fixed(0x51ef46b9ac287d03u64);
                    let mut sim8=Simulator::new(circ.b.next_qubit as usize,0,&mut rng8);
                    sim8.qubits=circ.b.sprint_sim.as_ref().unwrap().snapshot();
                    sim8.apply_iter(ops[..marks[a].1].iter());
                    let mut seqr=Vec::new();let mut lastr=sim8.qubits[core.c[r].id()as usize];
                    for (k,op) in span.iter().enumerate(){
                        sim8.apply_iter(std::slice::from_ref(op).iter());
                        let cur=sim8.qubits[core.c[r].id()as usize];
                        if cur!=lastr{seqr.push((k,op.kind as u8,op.q_target.0,op.q_control1.0,op.q_control2.0,cur));lastr=cur;}
                    }
                    eprintln!("Q792_STEP_BISECT four={four} c{r}_write_seq={:?}",seqr.iter().map(|&(k,k2,t,q1,q2,w)|(k,k2,t,q1,q2,format!("{w:#018x}"))).collect::<Vec<_>>());
                }
                if seq.len()>=19{
                    let (fi,_,_,_,_,_)=seq[18];
                    eprintln!("Q792_STEP_BISECT four={four} flip18_idx={fi} context={:?}",span[fi.saturating_sub(5)..(fi+4).min(span.len())].iter().enumerate().map(|(k,o)|(fi+k-5,o.kind as u8,o.q_target.0,o.q_control1.0,o.q_control2.0)).collect::<Vec<_>>());
                    // value-level dump: every control/target word (lanes 0..3 = rows 1..4)
                    // across the flip-18 context window, before each op is applied
                    let mut rng5=Fixed(0x51ef46b9ac287d03u64);
                    let mut sim5=Simulator::new(circ.b.next_qubit as usize,0,&mut rng5);
                    sim5.qubits=circ.b.sprint_sim.as_ref().unwrap().snapshot();
                    sim5.apply_iter(ops[..marks[a].1].iter());
                    let lo=fi.saturating_sub(5);let hi=(fi+4).min(span.len());
                    for (k,op) in span.iter().enumerate(){
                        if k>=lo&&k<hi{
                            let v1=if op.q_control1!=NO_QUBIT{sim5.qubits[op.q_control1.0 as usize]}else{u64::MAX};
                            let v2=if op.q_control2!=NO_QUBIT{sim5.qubits[op.q_control2.0 as usize]}else{u64::MAX};
                            let vt=if op.q_target!=NO_QUBIT{sim5.qubits[op.q_target.0 as usize]}else{u64::MAX};
                            eprintln!("Q792_STEP_BISECT four={four} ctl k={k} kind={:?} t={} q1={} q2={} lanes_t={:#06x} lanes_q1={:#06x} lanes_q2={:#06x} c0={:#06x} c1={:#06x}",op.kind,op.q_target.0,op.q_control1.0,op.q_control2.0,vt&0xf,v1&0xf,v2&0xf,sim5.qubits[core.c[0].id()as usize]&0xf,sim5.qubits[core.c[1].id()as usize]&0xf);
                        }
                        sim5.apply_iter(std::slice::from_ref(op).iter());
                    }
                }
            }
        }
        let mut boundaries:Vec<(&'static str,usize)>=marks.iter().filter(|&&(n,_)|n!="start").map(|&(n,i)|(n,i)).collect();
        boundaries.push(("end",ops.len()));
        let mut prev=0;let mut trace=Vec::new();let mut snaps:Vec<Vec<u64>>=Vec::new();
        if let Some(check)=&circ.b.sprint_sim{
            let snap=check.snapshot();
            let mut words:Vec<u64>=core.rank.iter().chain(&core.a).chain(&core.c).chain(&core.sm).map(|q|snap[q.id()as usize]).collect();
            words.push(snap[core.phase1.id()as usize]);
            words.push(snap[core.phase2.id()as usize]);
            words.extend(core.work2.iter().map(|q|snap[q.id()as usize]));
            snaps.push(words);
        }
        {
            // rank[0] full-word write sequence across the T10 stage
            let t10=marks.iter().position(|&(n,_)|n=="T10").unwrap();
            let span=&ops[..marks[t10].1];
            let mut rng6=Fixed(0x51ef46b9ac287d03u64);
            let mut sim6=Simulator::new(circ.b.next_qubit as usize,0,&mut rng6);
            sim6.qubits=circ.b.sprint_sim.as_ref().unwrap().snapshot();
            let mut seq=Vec::new();let mut last=sim6.qubits[core.rank[0].id()as usize];
            for (k,op) in span.iter().enumerate(){
                sim6.apply_iter(std::slice::from_ref(op).iter());
                let cur=sim6.qubits[core.rank[0].id()as usize];
                if cur!=last{seq.push((k,op.kind as u8,op.q_target.0,op.q_control1.0,op.q_control2.0,cur));last=cur;}
            }
            eprintln!("Q792_STEP_BISECT four={four} rank0_write_seq={:?}",seq.iter().map(|&(k,k2,t,q1,q2,w)|(k,k2,t,q1,q2,format!("{w:#018x}"))).collect::<Vec<_>>());
            let mut rngr=Fixed(0x51ef46b9ac287d03u64);
            let mut simr=Simulator::new(circ.b.next_qubit as usize,0,&mut rngr);
            simr.qubits=circ.b.sprint_sim.as_ref().unwrap().snapshot();
            let mut seqs=Vec::new();let mut lasts=simr.qubits[core.sm[3].id()as usize];
            for (k,op) in span.iter().enumerate(){
                simr.apply_iter(std::slice::from_ref(op).iter());
                let cur=simr.qubits[core.sm[3].id()as usize];
                if cur!=lasts{seqs.push((k,op.kind as u8,op.q_target.0,op.q_control1.0,op.q_control2.0,cur));lasts=cur;}
            }
            eprintln!("Q792_STEP_BISECT four={four} sm3_write_seq={:?}",seqs.iter().map(|&(k,k2,t,q1,q2,w)|(k,k2,t,q1,q2,format!("{w:#018x}"))).collect::<Vec<_>>());
        }
        for &(name,idx) in &boundaries{
            if idx>prev{if let Some(check)=&mut circ.b.sprint_sim{check.apply(&ops[prev..idx]);}}
            if let Some(check)=&circ.b.sprint_sim{
                let snap=check.snapshot();
                let mut words:Vec<u64>=core.rank.iter().chain(&core.a).chain(&core.c).chain(&core.sm).map(|q|snap[q.id()as usize]).collect();
                words.push(snap[core.phase1.id()as usize]);
                words.push(snap[core.phase2.id()as usize]);
                words.extend(core.work2.iter().map(|q|snap[q.id()as usize]));
                snaps.push(words);
                let mut meta=0u64;
                let mut sm=0u64;
                for i in 0..6{if check.read_qubit(&core.c[i],2){meta|=1<<i;}}
                for i in 0..4{if check.read_qubit(&core.sm[i],2){sm|=1<<i;}}
                let mut rk=0u64;let mut av=0u64;
                for i in 0..5{if check.read_qubit(&core.rank[i],2){rk|=1<<i;}}
                for i in 0..6{if check.read_qubit(&core.a[i],2){av|=1<<i;}}
                let mut pp=0u64;
                if check.read_qubit(&core.phase1,2){pp|=1;}
                if check.read_qubit(&core.phase2,2){pp|=2;}
                let w12=if check.read_qubit(&core.work1[2],2){1}else{0};
                let sign=if check.read_qubit(&dy[2],2){1}else{0};
                trace.push((name,check.read_w2(&core.work2[..257],2),meta,sm,rk,av,pp,w12,sign));
            }
            prev=idx;
        }
        restore_canonical_top(&mut circ,&mut dy,released);
        out.push((four,trace,boundaries,snaps,step_snaps,logical));
    }
    let (t3,t4)=(&out[0].1,&out[1].1);
    eprintln!("Q792_STEP_BISECT marks_3h={:?} marks_4h={:?}",out[0].2,out[1].2);
    for ((n3,v3,m3,s3,r3,a3,p3,w3,g3),(n4,v4,m4,s4,r4,a4,p4,w4,g4)) in t3.iter().zip(t4.iter()){
        eprintln!("Q792_STEP_BISECT stage_{n3} lane2 match={} c3h={m3:#x} c4h={m4:#x} p3h={p3:#x} p4h={p4:#x} w12_3h={w3:#x} w12_4h={w4:#x} sign3h={g3:#x} sign4h={g4:#x}",v3==v4&&m3==m4&&s3==s4&&r3==r4&&a3==a4&&p3==p4&&w3==w4&&g3==g4);
    }
    if let Some(((n,_,_,_,_,_,_,_,_),(&_,v4,_,_,_,_,_,_,_)))=t3.iter().zip(t4.iter()).find(|((n3,v3,_,_,_,_,_,_,_),(n4,v4,_,_,_,_,_,_,_))|n3==n4&&v3!=v4){
        eprintln!("Q792_STEP_BISECT first_divergent_stage={n} 4h={v4}");
    }
    // all-lane, all-register stage diff (word 0..5 rank, 6..11 a, 12..17 c, 18..21 sm,
    // 22 phase1, 23 phase2, 24.. work2 rail = word-24)
    let s3=&out[0].3;let s4=&out[1].3;
    if let Some((stage,(wi,lane,va,vb)))=(0..s3.len().min(s4.len())).find_map(|stage|{
        s3[stage].iter().zip(&s4[stage]).enumerate().find_map(|(wi,(a,b))|{
            let x=a^b;(0..64).find(|&lane|(x>>lane)&1!=0).map(|lane|(wi,lane,a,b))
        }).map(|r|(stage,r))
    }){
        let name=if stage==0{"step5_entry"}else{out[0].2[stage-1].0};
        let rail=if wi>=24{format!("w2[{}]",wi-24)}else{match wi{22=>"phase1".to_string(),23=>"phase2".to_string(),w if w>=18=>format!("sm[{}]",w-18),w if w>=12=>format!("c[{}]",w-12),w if w>=6=>format!("a[{}]",w-6),_=>format!("rank[{wi}]")}};
        eprintln!("Q792_STEP_BISECT first_any_lane_divergence stage={name} rail={rail} lane={lane} 3h_bit={} 4h_bit={}",(va>>lane)&1,(vb>>lane)&1);
    }else{
        eprintln!("Q792_STEP_BISECT all_lanes_all_registers_match");
    }
    eprintln!("Q792_STEP_BISECT entry3h rank={:?} a={:?} c={:?} sm={:?}",s3[0][0..5].iter().map(|w|format!("{w:#06x}")).collect::<Vec<_>>(),s3[0][6..12].iter().map(|w|format!("{w:#06x}")).collect::<Vec<_>>(),s3[0][12..18].iter().map(|w|format!("{w:#06x}")).collect::<Vec<_>>(),s3[0][18..22].iter().map(|w|format!("{w:#06x}")).collect::<Vec<_>>());
    eprintln!("Q792_STEP_BISECT entry4h rank={:?} a={:?} c={:?} sm={:?}",s4[0][0..5].iter().map(|w|format!("{w:#06x}")).collect::<Vec<_>>(),s4[0][6..12].iter().map(|w|format!("{w:#06x}")).collect::<Vec<_>>(),s4[0][12..18].iter().map(|w|format!("{w:#06x}")).collect::<Vec<_>>(),s4[0][18..22].iter().map(|w|format!("{w:#06x}")).collect::<Vec<_>>());
    // per-step (0..4) all-register diff: which step first diverges
    let steps3=&out[0].4;let steps4=&out[1].4;
    for st in 0..steps3.len(){
        let mut diffs:Vec<(usize,usize)>=Vec::new();
        for (wi,(a,b)) in steps3[st].iter().zip(&steps4[st]).enumerate(){
            let x=a^b;
            if x!=0{for lane in 0..4{if (x>>lane)&1!=0{diffs.push((wi,lane));if diffs.len()>=10{break;}}}}
            if diffs.len()>=10{break;}
        }
        let railname=|wi:usize|->String{if wi>=24{format!("w2[{}]",wi-24)}else{match wi{22=>"phase1".to_string(),23=>"phase2".to_string(),w if w>=18=>format!("sm[{}]",w-18),w if w>=12=>format!("c[{}]",w-12),w if w>=6=>format!("a[{}]",w-6),_=>format!("rank[{wi}]")}}};
        eprintln!("Q792_STEP_BISECT after_step{} j={} diffs={:?}",st,(st+1)%4,diffs.iter().map(|&(wi,lane)|(railname(wi),lane)).collect::<Vec<_>>());
    }
    // structural diff of the LOGICAL template streams (pre-remap): the first
    // index where kind or any qubit id differs is the geometry-dependent branch
    let l3=&out[0].5;let l4=&out[1].5;
    eprintln!("Q792_STEP_BISECT logical_len 3h={} 4h={}",l3.len(),l4.len());
    let first=(0..l3.len().min(l4.len())).find(|&i|l3[i].kind!=l4[i].kind||l3[i].q_target!=l4[i].q_target||l3[i].q_control1!=l4[i].q_control1||l3[i].q_control2!=l4[i].q_control2);
    match first{
        Some(i)=>{
            let lo=i.saturating_sub(4);let hi=(i+8).min(l3.len().min(l4.len()));
            let fmt=|o:&Op|(o.kind as u8,o.q_target.0,o.q_control1.0,o.q_control2.0);
            eprintln!("Q792_STEP_BISECT logical_first_diff idx={i} 3h={:?}",l3[lo..hi].iter().map(fmt).collect::<Vec<_>>());
            eprintln!("Q792_STEP_BISECT logical_first_diff idx={i} 4h={:?}",l4[lo..hi].iter().map(fmt).collect::<Vec<_>>());
        },
        None=>eprintln!("Q792_STEP_BISECT logical_streams_identical_upto={}",l3.len().min(l4.len())),
    }
}
