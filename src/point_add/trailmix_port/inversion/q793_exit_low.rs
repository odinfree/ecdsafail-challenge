//! Logical low-three-bit readers for the q=0 cycle exit.
//! No clean allocations. Physical coefficient heads may carry passengers.
use crate::point_add::trailmix_port::circuit::{Circuit,QReg};
use super::length_recompute::mixed_mcx;

fn gate(circ:&mut Circuit,controls:&[(&QReg,bool)],target:&QReg,dirty:&[QReg]) {
    let mut cs:Vec<(&QReg,bool)>=Vec::new();
    for &(q,v) in controls {
        assert_ne!(q.id(),target.id());
        if let Some(&(_,old))=cs.iter().find(|&&(p,_)|p.id()==q.id()) {
            if old!=v{return;}
        }else{cs.push((q,v));}
    }
    mixed_mcx(circ,&cs,target,dirty);
}

/// chart=[t0,t1,t2,b0,b1,b2,v0,v1,v2], before head cargo is inserted.
pub(super) fn xor_u(circ:&mut Circuit,chart:[&QReg;9],bit:usize,controls:&[(&QReg,bool)],target:&QReg,dirty:&[QReg]) {
    assert!((1..=2).contains(&bit));
    let [t0,t1,t2,b0,b1,b2,_v0,v1,v2]=chart;
    let terms=if bit==1 {
        vec![vec![(t0,true),(b1,true)],vec![(t0,false)],vec![(t0,false),(v1,true)],vec![(t0,false),(t1,true),(b0,true)]]
    } else {
        vec![vec![(t0,true),(b2,true)],vec![(t0,false)],vec![(t0,false),(v2,true)],vec![(t0,false),(t2,true),(b0,true)],vec![(t0,false),(t1,true),(b1,true)]]
    };
    for term in terms{let mut cs=controls.to_vec();cs.extend(term);gate(circ,&cs,target,dirty);}
}

/// Decode r1/r2 after the new t head has received an arbitrary passenger.
/// A254 implies r<4 and A255 implies r<2, so affected charts are ignored.
pub(super) fn xor_r(circ:&mut Circuit,chart:[&QReg;9],a_bits:&[&QReg],bit:usize,controls:&[(&QReg,bool)],target:&QReg,dirty:&[QReg]) {
    assert_eq!(a_bits.len(),8);assert!((1..=2).contains(&bit));
    let mut anf:Vec<bool>=(0..4096).map(|z|{
        let mut t=z&7;let b=z>>3&7;let v=z>>6&7;
        if z>>9&1!=0{t=1;}else if z>>10&1!=0{t=(t&1)|2;}else if z>>11&1!=0{t|=4;}
        let r=if t&1!=0{7usize.wrapping_sub(b*v).wrapping_mul(t)&7}else{b};
        r>>bit&1!=0
    }).collect();
    for k in 0..12{for z in 0..4096{if z>>k&1!=0{anf[z]^=anf[z^(1<<k)];}}}
    for(z,on) in anf.into_iter().enumerate(){
        if !on || (z>>9).count_ones()>1{continue;}
        let mut cs=controls.to_vec();
        cs.extend((0..9).filter(|&i|z>>i&1!=0).map(|i|(chart[i],true)));
        for value in 0..3{if z>>(9+value)&1!=0{cs.extend(a_bits.iter().enumerate().map(|(i,&q)|(q,value>>i&1!=0)));}}
        gate(circ,&cs,target,dirty);
        // Exact zero cofactor from t*r<=p, not a data-specific exception.
        cs.extend(a_bits[if bit==1{0}else{1}..].iter().map(|&q|(q,true)));
        gate(circ,&cs,target,dirty);
    }
}

// ─── 4-hole (mod16) readers ────────────────────────────────────────────────
//
// Raw full-cube ANF of the mod16 cycle's u-bit over the twelve chart wires
// [t0..t3,b0..b3,v0..v3] (z bit i = chart[i]). Exact on every state, which is
// a safe superset of the reachable domain the factored 3-hole form exploits.
// Derived with the fast Möbius transform (runtime/pro-k4-chart-derivation.md).

const U16_TERMS:&[&[u16]]=&[
    &[0x2,0x3,0x21,0x100,0x101,0x102,0x103,0x112,0x113,0x300,0x301],
    &[0x4,0x5,0x41,0x100,0x101,0x104,0x105,0x114,0x115,0x122,0x123,0x500,0x501],
    &[0x8,0x9,0x81,0x100,0x101,0x108,0x109,0x118,0x119,0x124,0x125,0x136,0x137,0x142,0x143,0x300,0x301,0x312,0x313,0x314,0x315,0x322,0x323,0x500,0x501,0x512,0x513,0x514,0x515,0x522,0x523,0x900,0x901],
];

pub(super) fn xor_u16(circ:&mut Circuit,chart:[&QReg;12],bit:usize,controls:&[(&QReg,bool)],target:&QReg,dirty:&[QReg]) {
    assert!((1..=3).contains(&bit));
    for &m in U16_TERMS[bit-1] {
        let mut cs=controls.to_vec();
        cs.extend((0..12).filter(|&i|m>>i&1!=0).map(|i|(chart[i],true)));
        gate(circ,&cs,target,dirty);
    }
}

const INV16:[usize;16]=[0,1,9,11,13,5,3,7,0,9,13,3,5,11,7,15];

pub(super) fn xor_r16(circ:&mut Circuit,chart:[&QReg;12],a_bits:&[&QReg],bit:usize,controls:&[(&QReg,bool)],target:&QReg,dirty:&[QReg]) {
    assert_eq!(a_bits.len(),8);assert!((1..=3).contains(&bit));
    // Same structure as the 3-hole xor_r: t may be forced by one of four
    // mutually exclusive A-side conditions (A==255..252), the r-bit is read
    // from the mod16 cycle, and the exact ANF is built with the fast Möbius
    // transform over 16 inputs (12 chart + 4 flags).
    let mut anf:Vec<bool>=(0..1<<16).map(|z|{
        let mut t=z&15;let b=z>>4&15;let v=z>>8&15;
        if z>>12&1!=0{t=1;}else if z>>13&1!=0{t=(t&1)|2;}else if z>>14&1!=0{t=(t&3)|4;}else if z>>15&1!=0{t|=8;}
        let r=if t&1!=0{15usize.wrapping_sub(b*v).wrapping_mul(INV16[t])&15}else{b};
        r>>bit&1!=0
    }).collect();
    for k in 0..16{for z in 0..1<<16{if z>>k&1!=0{anf[z]^=anf[z^(1<<k)];}}}
    for(z,on) in anf.into_iter().enumerate(){
        if !on || (z>>12).count_ones()>1{continue;}
        let mut cs=controls.to_vec();
        cs.extend((0..12).filter(|&i|z>>i&1!=0).map(|i|(chart[i],true)));
        for value in 0..4{if z>>(12+value)&1!=0{cs.extend(a_bits.iter().enumerate().map(|(i,&q)|(q,value>>i&1!=0)));}}
        gate(circ,&cs,target,dirty);
        cs.extend(a_bits[bit-1..].iter().map(|&q|(q,true)));
        gate(circ,&cs,target,dirty);
    }
}
