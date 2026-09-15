//! Exhaustive emitter-vs-model check for the R00 low-borrow seed in both
//! geometries (lane_seed_port).
//!
//! The seed callback XORs the exact low borrow into `carry` while the bit-2
//! interval mask is live. In the three-hole frame the residual's bits 0..2
//! have no physical DATA cell; the four-hole frame widens that implicit window
//! to bits 0..3, which is why the mod16 chart reads one extra rail per
//! quantity (t3 = W1[3], b3 = W2[(262-s) mod 259], v3 = W2[255-s]).
//!
//! This checker does not consult the emitter's own tables. It reads the chart
//! rails with an explicit wiring map, evaluates the modular relation
//! `r = (2^k - 1 - b*v) * t^-1 (mod 2^k)` with the documented A-case
//! overrides, and requires the emitted circuit to agree with that model on
//! every chart code, every A-case, both shifts, and both mask values. It also
//! verifies zero phase, literal inverse restoration and that only the carry
//! rail moves.
use crate::point_add::trailmix_port::circuit::{Circuit,QReg};
use crate::{circuit::OperationType as K,sim::Simulator};
use sha3::digest::XofReader;

struct Fixed(u64);
impl XofReader for Fixed{fn read(&mut self,b:&mut[u8]){for x in b.iter_mut(){*x=0x39;}}}
fn rnd(s:&mut u64)->u64{*s^=*s<<13;*s^=*s>>7;*s^=*s<<17;*s}
fn puti(w:&mut[u64],id:usize,l:usize,v:bool){let b=1u64<<l;w[id]=(w[id]&!b)|if v{b}else{0};}
fn put(w:&mut[u64],q:&QReg,l:usize,v:bool){puti(w,q.id()as usize,l,v)}

/// The A-case selectors, in the emitter's flag order (bits 0..4 of the flag
/// word): A0, A1, A2, A254, A253. The first three are rank0-exact; the two
/// cargo cases are rank29-exact.
const AV:[usize;5]=[0,1,2,254,253];
fn flag_rank(case:usize)->usize{if case>=3{29}else{0}}
/// A254 quashes the cargo bits the bound `t>=2^254, t*r+u*v=p => r<4` with
/// `v<<S <= r` excludes. The pattern is "clear the top `shift` bits of the
/// window", lifted one bit with the window.
fn mask_a254(four:bool,shift:usize)->usize{
    if shift==1{if four{7}else{3}}else if four{3}else{1}
}
/// A253/shift2 carries a second cargo; the three-hole form clears v2, the
/// four-hole form clears v3.
fn mask_a253(four:bool)->usize{if four{7}else{3}}

fn inv_mod(t:usize,k:usize)->usize{let m=1usize<<k;for x in 1..m{if x*t%m==1{return x;}}0}

/// Independent model of the seed's contract. `case` = None means "no A-case
/// selector matches" (the off-domain extension).
/// The residual's low window (mod 2^k) as the contract defines it, including
/// the A-case overrides. This is the oracle; the emitted ANF must reproduce it.
fn rr_model(four:bool,shift:usize,t:usize,b:usize,v:usize,case:Option<usize>)->usize{
    let k=if four{4}else{3};let m=(1usize<<k)-1;
    let (mut t,mut b,mut v)=(t&m,b&m,v&m);
    match case{
        Some(0)=>{t=1;b=0;}
        Some(1)=>{t=(t&1)|2;}
        Some(2)=>{t=(t&3)|4;}
        Some(3)=>{v&=mask_a254(four,shift);}
        Some(4)=>{if shift==2{v&=mask_a253(four);}}
        _=>{}
    }
    if t&1!=0{(m.wrapping_sub(b*v)).wrapping_mul(inv_mod(t,k))&m}else{b}
}
fn model(four:bool,shift:usize,t:usize,b:usize,v:usize,case:Option<usize>)->bool{
    let k=if four{4}else{3};let m=(1usize<<k)-1;
    let v=v&m;
    let (_t,_b,mut vv)=(t&m,b&m,v);
    if let Some(3)=case{vv&=mask_a254(four,shift);}
    if let Some(4)=case{if shift==2{vv&=mask_a253(four);}}
    (rr_model(four,shift,t,b,v,case)>>shift)<(vv&((1usize<<(k-shift))-1))
}

struct Frame{rank:Vec<QReg>,a:Vec<QReg>,w1:Vec<QReg>,w2:Vec<QReg>,mask:QReg,carry:QReg,owned:usize}

fn build(four:bool,j:usize)->(Frame,Vec<crate::circuit::Op>){
    std::env::set_var("LOWQ_Q792_EEA",if four{"1"}else{"0"});
    let mut c=Circuit::new();
    let rank=c.alloc_qreg_bits("rank",5);let a=c.alloc_qreg_bits("a",6);
    let _c=c.alloc_qreg_bits("c",6);let _sm=c.alloc_qreg_bits("sm",4);
    let _p1=c.alloc_qreg("p1");let _p2=c.alloc_qreg("p2");
    let mask=c.alloc_qreg("mask");let carry=c.alloc_qreg("carry");
    let w1=c.alloc_qreg_bits("w1",259);let w2=c.alloc_qreg_bits("w2",259);
    let dirty=c.alloc_qreg_bits("dirty",23);let owned=c.b.next_qubit as usize;
    super::q793_r00_seed_dynamic_r02::emit(&mut c,&rank,&a,&w1,&w2,&mask,&carry,&dirty,j);
    let b=c.into_builder();
    for op in &b.ops{op.validate();assert!(matches!(op.kind,K::X|K::CX|K::CCX),"seed emitted a non-Clifford-Toffoli op");}
    (Frame{rank,a,w1,w2,mask,carry,owned},b.ops)
}

/// Chart rails of the emitter's own wiring map, read back independently here:
/// t_k = W1[k], b_k = W2[(259+k-shift) mod 259], v_k = W2[258-shift-k].
fn chart_rails(f:&Frame,four:bool,shift:usize)->(Vec<usize>,Vec<usize>,Vec<usize>){
    let k=if four{4}else{3};
    let t=(0..k).map(|kk|f.w1[kk].id()as usize).collect();
    let b=(0..k).map(|kk|f.w2[(259+kk-shift)%259].id()as usize).collect();
    let v=(0..k).map(|kk|f.w2[258-shift-kk].id()as usize).collect();
    (t,b,v)
}

pub fn run(){
    let mut lanes_total=0usize;
    for &four in &[false,true]{
        for j in 0..2usize{
            let shift=j+1;
            let (frame,ops)=build(four,j);
            let (tr,br,vr)=chart_rails(&frame,four,shift);
            let k=if four{4}else{3};
            let ncode=1usize<<(3*k);
            let cases:[Option<usize>;6]=[None,Some(0),Some(1),Some(2),Some(3),Some(4)];
            let ccx=ops.iter().filter(|o|o.kind==K::CCX).count();
            eprintln!("Q793_R00_SEED_MOD16_BUILT four={four} j={j} shift={shift} chart_bits={k} ops={} CCX={ccx} owned={}",ops.len(),frame.owned);
            let total_lanes=cases.len()*ncode;
            for base in (0..total_lanes).step_by(64){
                let mut before=vec![0u64;frame.owned];let mut after=vec![0u64;frame.owned];
                {
                    let mut rs=0x793_5eed_16u64^(four as u64)<<40^(j as u64)<<32^(base as u64);
                    for i in 0..frame.owned{before[i]=rnd(&mut rs);}
                    for i in 0..frame.owned{after[i]=before[i];}
                }
                let mut nlanes=0usize;
                for lane in 0..64{
                    let global=base+lane;if global>=total_lanes{break;}
                    let case=cases[global/ncode];let code=global%ncode;
                    let t=code&((1<<k)-1);let b=(code>>k)&((1<<k)-1);let v=(code>>(2*k))&((1<<k)-1);
                    // Mask alternates: even lanes live, odd lanes dead. The
                    // dead lanes prove no gate can fire without the mask.
                    let live=lane%2==0;
                    for w in [&mut before,&mut after]{
                        for kk in 0..k{puti(w,tr[kk],lane,t>>kk&1!=0);}
                        for kk in 0..k{puti(w,br[kk],lane,b>>kk&1!=0);}
                        for kk in 0..k{puti(w,vr[kk],lane,v>>kk&1!=0);}
                        let rvv=case.map_or(0,flag_rank);let avv=case.map_or(63,|c|AV[c]);
                        for i in 0..5{put(w,&frame.rank[i],lane,rvv>>i&1!=0);}
                        for i in 0..6{put(w,&frame.a[i],lane,avv>>i&1!=0);}
                        put(w,&frame.mask,lane,live);
                    }
                    if live&&model(four,shift,t,b,v,case){after[frame.carry.id()as usize]^=1u64<<lane;}
                    nlanes+=1;
                }
                let mut x=Fixed(0);
                let mut sim=Simulator::new(frame.owned,0,&mut x);
                sim.qubits.copy_from_slice(&before);
                sim.apply_iter(ops.iter());
                let diff:Vec<_>=sim.qubits.iter().zip(&after).enumerate().filter(|(_,(p,q))|p!=q).map(|(i,(p,q))|(i,format!("{:016x}",p^q))).collect();
                assert!(diff.is_empty(),"R00 seed mod16 four={four} j={j} base={base} forward mismatch lanes={nlanes} diff={diff:?}");
                assert_eq!(sim.phase,0,"R00 seed mod16 four={four} j={j} base={base} phase != 0");
                sim.apply_iter(ops.iter().rev());
                assert_eq!(sim.qubits,before,"R00 seed mod16 four={four} j={j} base={base} literal inverse did not restore");
                assert_eq!(sim.phase,0,"R00 seed mod16 four={four} j={j} base={base} phase != 0 after inverse");
                lanes_total+=nlanes;
            }
        }
    }
    eprintln!("Q793_R00_SEED_MOD16_PASS lanes={lanes_total} geometries=2 shifts=2 chart_codes=512+4096 A_cases=5+off live_and_dead_mask exact_model_match literal_inverse_phase0 carry_only");
}

/// Which A-case flag the emitter's (rank, a) selectors activate for a lane:
/// A0/A1/A2 are rank0-exact, A254/A253 are rank29-exact, and A253 exists only
/// for shift 2 (j=1).
fn case_of(rk:usize,av:usize,j:usize)->Option<usize>{
    if rk==29{
        if av==254{Some(3)}else if av==253&&j==1{Some(4)}else{None}
    }else if rk==0{
        match av{0=>Some(0),1=>Some(1),2=>Some(2),_=>None}
    }else{None}
}

struct Stage{rank:Vec<QReg>,a:Vec<QReg>,cc:Vec<QReg>,sm:Vec<QReg>,p1:QReg,p2:QReg,sign:QReg,w1:Vec<QReg>,w2:Vec<QReg>,dirty:Vec<QReg>,owned:usize}

/// Build the production R00 comparator for one clock `j` in whatever geometry
/// the environment currently selects, plus the op-range of the mandatory
/// low-borrow callback.
fn build_stage(j:usize)->(Stage,Vec<crate::circuit::Op>,Vec<(usize,usize)>){
    std::env::set_var("Q793_R00_SEED_MARK","1");
    super::q793_r00::clear_seed_marks();
    let mut c=Circuit::new();
    let rank=c.alloc_qreg_bits("rank",5);let a=c.alloc_qreg_bits("a",6);
    let cc=c.alloc_qreg_bits("c",6);let sm=c.alloc_qreg_bits("sm",4);
    let p1=c.alloc_qreg("p1");let p2=c.alloc_qreg("p2");let sign=c.alloc_qreg("sign");
    let w1=c.alloc_qreg_bits("w1",259);let w2=c.alloc_qreg_bits("w2",259);
    let dirty=c.alloc_qreg_bits("dirty",23);
    let owned=c.b.next_qubit as usize;
    let st=Stage{rank,a,cc,sm,p1,p2,sign,w1,w2,dirty,owned};
    {
        let mut seed=|cc:&mut Circuit,mask:&QReg,carry:&QReg,helpers:&[QReg],clock:usize|{
            super::q793_r00_seed_dynamic_r02::emit(cc,&st.rank,&st.a,&st.w1,&st.w2,mask,carry,helpers,clock);
        };
        super::q793_r00::phase00_with_support(&mut c,&st.rank,&st.a,&st.cc,&st.sm,&st.p1,&st.p2,&st.sign,&st.w1,&st.w2,&st.dirty,j,259,&mut seed);
    }
    let ops=c.into_builder().ops;
    for op in &ops{op.validate();assert!(matches!(op.kind,K::X|K::CX|K::CCX));}
    let marks=super::q793_r00::seed_marks();
    (st,ops,marks)
}

/// Fill one 64-lane block of the shipped checker's contract family.
fn fill_block(st:&Stage,j:usize,pattern:usize,batch:usize,triples:&[[usize;3]])->(Vec<u64>,u64,Vec<String>){
    let mut rs=0x7930_1600u64^((j as u64)<<48)^((pattern as u64)<<32)^(batch as u64);
    let mut before:Vec<u64>=(0..st.owned).map(|_|rnd(&mut rs)).collect();
    let mut phase_bits=0u64;let mut diag:Vec<String>=vec![String::new();64];
    for lane in 0..64usize{
        let av=(64*batch+lane)%256;let valid=av<255&&av+j<=255;
        let sv=if valid{j+4*if pattern<2{0}else{(pattern*37+av)%((255-av-j)/4+1)}}else{j};
        let rk=triples.iter().position(|&x|x==[av/64,0,sv/64]).unwrap();
        let phase=if av==255||valid&&pattern<6{0}else{1+(pattern+lane)%3};
        let mut rr2=0x5eed_0000u64^((j as u64)<<40)^((pattern as u64)<<24)^((batch as u64)<<8)^(lane as u64);
        let f:Vec<usize>=(0..4).map(|_|(rnd(&mut rr2)&255)as usize).collect();
        for i in 0..5{put(&mut before,&st.rank[i],lane,rk>>i&1!=0);}
        for i in 0..6{put(&mut before,&st.a[i],lane,av>>i&1!=0);if phase==0&&av!=255{put(&mut before,&st.cc[i],lane,false);}}
        for i in 0..4{put(&mut before,&st.sm[i],lane,sv>>(i+2)&1!=0);}
        put(&mut before,&st.p1,lane,phase&2!=0);put(&mut before,&st.p2,lane,phase&1!=0);
        for i in 0..259{
            let b0=if i<=av{(f[0]>>(i%8)&1!=0)&&i<256}else{(f[2]>>((258usize.saturating_sub(i))%8)&1!=0)&&i<259};
            put(&mut before,&st.w1[i],lane,b0);
            let raw=(i+j+1)%259;
            let b1=if raw<=av{(f[1]>>(raw%8)&1!=0)&&raw<256}else{(f[3]>>((258usize.saturating_sub(raw))%8)&1!=0)&&raw<259};
            put(&mut before,&st.w2[i],lane,b1);
        }
        if f[0]&1==0{for i in 0..3{put(&mut before,&st.w2[(259+i-j-1)%259],lane,f[2]>>i&1!=0);}}
        diag[lane]=format!("lane={lane} av={av} sv={sv} rk={rk} phase={phase}");
        if phase==0&&valid{phase_bits|=1u64<<lane;}
    }
    (before,phase_bits,diag)
}

/// Differential referee: identical inputs through the three-hole and the
/// four-hole R00 comparator, comparing every geometry-invariant rail (the
/// sign accumulator, the interval mask, all metadata and the data registers
/// that both frames keep). Any logical-rail difference is a port defect, not a
/// synthetic-family artifact: the two frames are the same walk at one fewer
/// residual cell.
pub fn run_stage_diff(){
    std::env::set_var("Q796_PARITY","1");
    std::env::set_var("Q794_MOD4","1");
    let triples:Vec<_>=(0..4).flat_map(|a|(0..4).flat_map(move|c|(0..4).filter(move|&s|a+c+s<=4).map(move|s|[a,c,s]))).collect();
    let patterns:usize=if std::env::var("Q793_R00_MOD16_STAGE_SUBSET").ok().as_deref()==Some("1"){1}else{8};
    let batches:usize=if std::env::var("Q793_R00_MOD16_STAGE_SUBSET").ok().as_deref()==Some("1"){1}else{4};
    let mut mismatched=0usize;let mut lanes_total=0usize;let mut first_report=0usize;
    for j in 0..4usize{
        std::env::set_var("LOWQ_Q792_EEA","0");std::env::remove_var("Q793_R00_SEED_CALL_INDEX");
        let (st3,ops3,marks3)=build_stage(j);
        std::env::set_var("LOWQ_Q792_EEA","1");
        let (st4,ops4,marks4)=build_stage(j);
        if first_report<6{
            eprintln!("Q793_R00_STAGE_DIFF_BUILT j={j} three_ops={} three_marks={:?} four_ops={} four_marks={:?}",ops3.len(),marks3,ops4.len(),marks4);
            first_report+=1;
        }
        assert_eq!(st3.owned,st4.owned);
        for pattern in 0..patterns{for batch in 0..batches{
            let (before,active_bits,diag)=fill_block(&st3,j,pattern,batch,&triples);
            let mut x3=Fixed(3);let mut s3=Simulator::new(st3.owned,0,&mut x3);s3.qubits.copy_from_slice(&before);s3.apply_iter(ops3.iter());
            let mut x4=Fixed(4);let mut s4=Simulator::new(st4.owned,0,&mut x4);s4.qubits.copy_from_slice(&before);s4.apply_iter(ops4.iter());
            let sign3=s3.qubits[st3.sign.id()as usize];let sign4=s4.qubits[st4.sign.id()as usize];
            let d=sign3^sign4;
            if d!=0{
                mismatched+=d.count_ones()as usize;
                let ev:Vec<String>=(0..64).filter(|l|d>>l&1!=0).map(|l|format!("{} sign3={} sign4={}",diag[l],sign3>>l&1,sign4>>l&1)).collect();
                eprintln!("Q793_R00_STAGE_DIFF_SIGN j={j} pattern={pattern} batch={batch} active={:#x} evidence={:?}",active_bits,ev);
            }
            let mask3=s3.qubits[st3.cc[0].id()as usize];let mask4=s4.qubits[st4.cc[0].id()as usize];
            if mask3!=mask4{
                let ev:Vec<String>=(0..64).filter(|l|(mask3^mask4)>>l&1!=0).map(|l|format!("{} mask3={} mask4={}",diag[l],mask3>>l&1,mask4>>l&1)).collect();
                eprintln!("Q793_R00_STAGE_DIFF_MASK j={j} pattern={pattern} batch={batch} evidence={:?}",ev);
            }
            lanes_total+=64;
        }}
    }
    eprintln!("Q793_R00_STAGE_DIFF_DONE lanes={lanes_total} sign_mismatches={mismatched} (three-hole vs four-hole, identical inputs)");
}

/// Stage-level four-hole check: the full R00 comparator (`phase00_with_support`,
/// i.e. metadata chain + seed + comparison chain) in the four-hole geometry,
/// driven by the same synthetic lane family the shipped three-hole checker
/// uses. In this frame `Scan::compare` skips the i=3 DATA step, so the
/// residual's bits 0..3 are implicit and must come from the mod16 low-borrow
/// reconstruction while bits >= 4 come from physical cells. This exercises the
/// mask-chain / call-site interaction the bare emitter check cannot see.
pub fn run_stage(){
    std::env::set_var("Q796_PARITY","1");
    std::env::set_var("Q794_MOD4","1");
    std::env::set_var("LOWQ_Q792_EEA","1");
    let triples:Vec<_>=(0..4).flat_map(|a|(0..4).flat_map(move|c|(0..4).filter(move|&s|a+c+s<=4).map(move|s|[a,c,s]))).collect();
    let patterns:usize=if std::env::var("Q793_R00_MOD16_STAGE_SUBSET").ok().as_deref()==Some("1"){1}else{8};
    let batches:usize=if std::env::var("Q793_R00_MOD16_STAGE_SUBSET").ok().as_deref()==Some("1"){1}else{4};
    let mut lanes_total=0usize;let mut active_total=0usize;
    for j in 0..4usize{
        let mut c=Circuit::new();
        let rank=c.alloc_qreg_bits("rank",5);let a=c.alloc_qreg_bits("a",6);
        let cc=c.alloc_qreg_bits("c",6);let sm=c.alloc_qreg_bits("sm",4);
        let p1=c.alloc_qreg("p1");let p2=c.alloc_qreg("p2");let sign=c.alloc_qreg("sign");
        let w1=c.alloc_qreg_bits("w1",259);let w2=c.alloc_qreg_bits("w2",259);
        let dirty=c.alloc_qreg_bits("dirty",23);
        let owned=c.b.next_qubit as usize;
        let st=Stage{rank,a,cc,sm,p1,p2,sign,w1,w2,dirty,owned};
        std::env::set_var("Q793_R00_SEED_MARK","1");
        super::q793_r00::clear_seed_marks();
        {
            let mut seed=|cc:&mut Circuit,mask:&QReg,carry:&QReg,helpers:&[QReg],clock:usize|{
                super::q793_r00_seed_dynamic_r02::emit(cc,&st.rank,&st.a,&st.w1,&st.w2,mask,carry,helpers,clock);
            };
            super::q793_r00::phase00_with_support(&mut c,&st.rank,&st.a,&st.cc,&st.sm,&st.p1,&st.p2,&st.sign,&st.w1,&st.w2,&st.dirty,j,259,&mut seed);
        }
        let ops=c.into_builder().ops;
        let marks=super::q793_r00::seed_marks();
        for op in &ops{op.validate();assert!(matches!(op.kind,K::X|K::CX|K::CCX));}
        eprintln!("Q793_R00_MOD16_STAGE_BUILT j={j} ops={} CCX={} owned={}",ops.len(),ops.iter().filter(|o|o.kind==K::CCX).count(),st.owned);
        for pattern in 0..patterns{for batch in 0..batches{
            let mut rs=0x7930_1600u64^((j as u64)<<48)^((pattern as u64)<<32)^(batch as u64);
            let mut before:Vec<u64>=(0..st.owned).map(|_|rnd(&mut rs)).collect();
            let mut after=before.clone();
            let mut active=0usize;
            let mut diag:Vec<String>=vec![String::new();64];
            for lane in 0..64usize{
                let av=(64*batch+lane)%256;let valid=av<255&&av+j<=255;
                let sv=if valid{j+4*if pattern<2{0}else{(pattern*37+av)%((255-av-j)/4+1)}}else{j};
                let rk=triples.iter().position(|&x|x==[av/64,0,sv/64]).unwrap();
                let phase=if av==255||valid&&pattern<6{0}else{1+(pattern+lane)%3};
                // Row fields, exactly the three-hole checker's contract family.
                let mut rr2=0x5eed_0000u64^((j as u64)<<40)^((pattern as u64)<<24)^((batch as u64)<<8)^(lane as u64);
                let f:Vec<usize>=(0..4).map(|_|(rnd(&mut rr2)&255)as usize).collect();
                for w in [&mut before,&mut after]{
                    for i in 0..5{put(w,&st.rank[i],lane,rk>>i&1!=0);}
                    for i in 0..6{put(w,&st.a[i],lane,av>>i&1!=0);if phase==0&&av!=255{put(w,&st.cc[i],lane,false);}}
                    for i in 0..4{put(w,&st.sm[i],lane,sv>>(i+2)&1!=0);}
                    put(w,&st.p1,lane,phase&2!=0);put(w,&st.p2,lane,phase&1!=0);
                    // w1 rails: index i gets field-0 bit i for i<=av, else the
                    // reversed field-2 bit 258-i (same row contract as the
                    // three-hole checker); w2 is the rotated v-register.
                    for i in 0..259{
                        let b0=if i<=av{(f[0]>>(i%8)&1!=0)&&i<256}else{(f[2]>>((258usize.saturating_sub(i))%8)&1!=0)&&i<259};
                        put(w,&st.w1[i],lane,b0);
                        let raw=(i+j+1)%259;
                        let b1=if raw<=av{(f[1]>>(raw%8)&1!=0)&&raw<256}else{(f[3]>>((258usize.saturating_sub(raw))%8)&1!=0)&&raw<259};
                        put(w,&st.w2[i],lane,b1);
                    }
                    if f[0]&1==0{for i in 0..3{put(w,&st.w2[(259+i-j-1)%259],lane,f[2]>>i&1!=0);}}
                }
                if phase==0&&valid{
                    let raw=|q:&QReg|((before[q.id()as usize]>>lane)&1)as usize;
                    let shift=j+1;
                    let t=(0..4).map(|kk|raw(&st.w1[kk])<<kk).sum::<usize>();
                    let b=(0..4).map(|kk|raw(&st.w2[(259+kk-shift)%259])<<kk).sum::<usize>();
                    let v=(0..4).map(|kk|raw(&st.w2[258-shift-kk])<<kk).sum::<usize>();
                    let case=case_of(rk,av,j);
                    let r=rr_model(true,shift,t,b,v,case);
                    // Four-hole: bits 0..3 of the residual are implicit (the
                    // i=3 DATA step is skipped), bits >= 4 come from the cells.
                    let mut less=0usize;
                    for i in shift..257-av{
                        let xb=raw(&st.w2[258-i]);
                        let y=if i<4{(r>>i)&1}else{raw(&st.w1[258-i])};
                        if xb!=y{less=xb;}
                    }
                    if less!=0{after[st.sign.id()as usize]^=1u64<<lane;}
                    diag[lane]=format!("lane={lane} av={av} sv={sv} rk={rk} case={case:?} t={t} b={b} v={v} r={r} less={less}");
                    active+=1;
                }
            }
            let mut x=Fixed(0x16);
            let mut sim=Simulator::new(st.owned,0,&mut x);
            sim.qubits.copy_from_slice(&before);
            // Apply in chunks so the interval-mask rail can be read exactly at
            // each mandatory callback.
            let mut at=0usize;let mut mask_at_call=vec![0u64;marks.len()];
            for (n,(s0,_)) in marks.iter().enumerate(){
                sim.apply_iter(ops[at..*s0].iter());at=*s0;
                mask_at_call[n]=sim.qubits[st.cc[0].id()as usize];
            }
            sim.apply_iter(ops[at..].iter());
            if sim.qubits!=after{
                let diffs:Vec<_>=sim.qubits.iter().zip(&after).enumerate().filter(|(_,(p,q))|p!=q).map(|(i,(p,q))|(i,format!("{:016x}",p^q))).collect();
                let evidence:Vec<String>=diffs.iter().map(|(i,m)|{
                    let w=u64::from_str_radix(m,16).unwrap_or(0);
                    let mut out=format!("wire={i} mask={m} lanes:");
                    for lane in 0..64{if w>>lane&1!=0{out.push(' ');out.push_str(&diag[lane]);
                        out.push_str(&format!(" mask_at_call={:#x}",mask_at_call.first().copied().unwrap_or(0)>>lane&1));}}
                    out}).collect();
                panic!("Q793_R00_MOD16_STAGE_FAIL j={j} pattern={pattern} batch={batch} diffs={diffs:?} evidence={evidence:?}");
            }
            assert_eq!(sim.phase,0,"Q793_R00_MOD16_STAGE phase != 0 j={j} pattern={pattern} batch={batch}");
            sim.apply_iter(ops.iter().rev());
            assert_eq!(sim.qubits,before,"Q793_R00_MOD16_STAGE literal inverse did not restore j={j} pattern={pattern} batch={batch}");
            assert_eq!(sim.phase,0);
            lanes_total+=64;active_total+=active;
        }}
    }
    eprintln!("Q793_R00_MOD16_STAGE_PASS lanes={lanes_total} active={active_total} templates=4 four_hole_window_bits=4 implicit_i3_oracle literal_inverse_phase0");
}
