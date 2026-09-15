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
fn model(four:bool,shift:usize,t:usize,b:usize,v:usize,case:Option<usize>)->bool{
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
    let r=if t&1!=0{(m.wrapping_sub(b*v)).wrapping_mul(inv_mod(t,k))&m}else{b};
    (r>>shift)<(v&((1usize<<(k-shift))-1))
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
