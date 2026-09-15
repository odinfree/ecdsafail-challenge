//! R02 adds A253/shift2 cargo correction. t>=2^253, r<8 and 2v<=r imply v2=0.
//! R00 low3 reader in the post-pre-rotation production physical frame.
//! Required contract supplied by the root boundary/cargo audit; no allocation.
use crate::point_add::trailmix_port::circuit::{Circuit,QReg};
use super::length_recompute::mixed_mcx;

fn gate(circ:&mut Circuit,controls:&[(&QReg,bool)],out:&QReg,dirty:&[QReg]) {
    let mut unique:Vec<(&QReg,bool)>=Vec::new();
    for &(q,v)in controls{assert_ne!(q.id(),out.id());
        if let Some(&(_,old))=unique.iter().find(|&&(p,_)|p.id()==q.id()){
            if old!=v{return;}
        }else{unique.push((q,v));}
    }mixed_mcx(circ,&unique,out,dirty);
}

/// Only bit2's active mask can select S0 (j0) or S1 (j1); C=0 then.
/// Other j have no low seed. Thus flag A0/A1/A2 uses exact rank0, and A254
/// uses exact rank29. Those selectors are exact on the required active
/// domain; outside it this is a pure carry-XOR extension undone by W^-1.
///
/// Normalization contract in this R00 internal frame:
/// A0: logical t=1,b=0; A1: t1=1,t2=0; A2: t2=1.
/// A254/shift1: v2=0; A254/shift2: v1=v2=0 (v=1).
/// Raw shortword/cargo bits remain untouched, even when they contain loans.
pub(super) fn emit(circ:&mut Circuit,rank:&[QReg],a:&[QReg],w1:&[QReg],w2:&[QReg],mask:&QReg,carry:&QReg,dirty:&[QReg],j:usize) {
    assert!(j<4);if j>=2{return;}let shift=j+1;
    assert_eq!(rank.len(),5);assert_eq!(a.len(),6);assert_eq!(w1.len(),259);assert_eq!(w2.len(),259);
    // `Q793_R00_SEED_LOW_MOD8` keeps the *low* comparison at the three-hole
    // (mod8) form even inside the four-hole geometry, for the structure in
    // which a dedicated bit-3 callback covers the deleted index-3 chain step.
    let four=super::q793_lifecycle_r03::four_hole()&&std::env::var("Q793_R00_SEED_LOW_MOD8").ok().as_deref()!=Some("1");
    let (chart,anf,flag_bits,flag_shift):(Vec<&QReg>,Vec<bool>,usize,usize)=if four{
        // 4-hole (mod16) low-borrow reader: 4-bit t/b/v charts, the mod16
        // cycle arithmetic with INV16, and the top-A v masks widened by one
        // bit (A254: v3=0; A253/shift2: v3=0) because the walk's modulus is 16.
        let chart=vec![&w1[0],&w1[1],&w1[2],&w1[3],
            &w2[(259-shift)%259],&w2[(260-shift)%259],&w2[(261-shift)%259],&w2[(262-shift)%259],
            &w2[258-shift],&w2[257-shift],&w2[256-shift],&w2[255-shift]];
        let mut anf:Vec<_>=(0..1<<17).map(|z|{
            let mut t=z&15;let mut b=(z>>4)&15;let mut v=(z>>8)&15;
            if z>>12&1!=0{t=1;b=0;}else if z>>13&1!=0{t=(t&1)|2;}else if z>>14&1!=0{t=(t&3)|4;}
            if z>>15&1!=0{v&=if shift==1{7}else{3};} // A254 cargo
            if shift==2&&z>>16&1!=0{v&=7;}           // A253 second cargo occupies raw v3
            let r=if t&1!=0{(15usize.wrapping_sub(b*v).wrapping_mul(super::q793_exit_low::INV16[t]))&15}else{b};
            (r>>shift)<(v&((1usize<<(4-shift))-1))
        }).collect();
        for bit in 0..17{for m in 0..1<<17{if m>>bit&1!=0{anf[m]^=anf[m^(1<<bit)];}}}
        (chart,anf,12,5)
    }else{
        let chart=vec![&w1[0],&w1[1],&w1[2],
            &w2[(259-shift)%259],&w2[(260-shift)%259],&w2[(261-shift)%259],
            &w2[258-shift],&w2[257-shift],&w2[256-shift]];
        let mut anf:Vec<_>=(0..16384).map(|z|{
            let mut t=z&7;let mut b=(z>>3)&7;let mut v=(z>>6)&7;
            if z>>9&1!=0{t=1;b=0;}else if z>>10&1!=0{t=(t&1)|2;}else if z>>11&1!=0{t=(t&3)|4;}
            if z>>12&1!=0{v&=if shift==1{3}else{1};}
            if shift==2&&z>>13&1!=0{v&=3;} // A253 second cargo occupies raw v2.
            let r=if t&1!=0{(7usize.wrapping_sub(b*v).wrapping_mul(t))&7}else{b};
            (r>>shift)<(v&((1usize<<(3-shift))-1))
        }).collect();
        for bit in 0..14{for m in 0..16384{if m>>bit&1!=0{anf[m]^=anf[m^(1<<bit)];}}}
        (chart,anf,9,5)
    };
    let owned=circ.b.next_qubit;let start=circ.b.ops.len();
    for(m,on)in anf.into_iter().enumerate(){
        if !on||(m>>flag_bits).count_ones()>1{continue;}
        let mut cs=vec![(mask,true)];
        cs.extend((0..flag_bits).filter(|&i|m>>i&1!=0).map(|i|(chart[i],true)));
        for f in 0..flag_shift{if m>>(flag_bits+f)&1!=0{
            let av=[0usize,1,2,254,253][f];let rv=if f>=3{29}else{0};
            cs.extend((0..5).map(|i|(&rank[i],rv>>i&1!=0)));
            cs.extend((0..6).map(|i|(&a[i],av>>i&1!=0)));
        }}gate(circ,&cs,carry,dirty);
    }
    assert_eq!(circ.b.next_qubit,owned);
    for op in &circ.b.ops[start..]{for &h in if four{[255usize,256,257,258].as_slice()}else{[256usize,257,258].as_slice()}{let q=w1[h].id()as u64;
        assert!(op.q_target.0!=q&&op.q_control1.0!=q&&op.q_control2.0!=q,"dynamic R00 seed touched hole{h}");
    }}
}

/// Four-hole only: the chain step at residual index 3 has no DATA cell in this
/// geometry (`w1[255]` is an omitted marker), so its net carry contribution has
/// to be emitted here instead. With `x` the residual's bit 3 and `y` the paired
/// v-rail (`w2[255]`, i.e. the chart's v bit `3-shift`), the accepted
/// three-hole step contributes `y ^ (mask & (x^y) & y)` to the carry, which is
/// `x & y` while the interval mask is live and `y` while it is not. `x = x_3`
/// is the mod16 reconstruction's bit 3 (a function of the chart and the A-case
/// selectors), so this is again a Möbius ANF over chart + flags, with the mask
/// used only as a control polarity.
pub(super) fn emit_bit3(circ:&mut Circuit,rank:&[QReg],a:&[QReg],w1:&[QReg],w2:&[QReg],mask:&QReg,carry:&QReg,dirty:&[QReg],j:usize) {
    assert!(j<2);let shift=j+1;
    assert_eq!(rank.len(),5);assert_eq!(a.len(),6);assert_eq!(w1.len(),259);assert_eq!(w2.len(),259);
    let chart=vec![&w1[0],&w1[1],&w1[2],&w1[3],
        &w2[(259-shift)%259],&w2[(260-shift)%259],&w2[(261-shift)%259],&w2[(262-shift)%259],
        &w2[258-shift],&w2[257-shift],&w2[256-shift],&w2[255-shift]];
    let y_index=8+(3-shift);
    let mut anf:Vec<_>=(0..1<<17).map(|z|{
        let mut t=z&15;let mut b=(z>>4)&15;let mut v=(z>>8)&15;
        if z>>12&1!=0{t=1;b=0;}else if z>>13&1!=0{t=(t&1)|2;}else if z>>14&1!=0{t=(t&3)|4;}
        if z>>15&1!=0{v&=if shift==1{7}else{3};}
        if shift==2&&z>>16&1!=0{v&=7;}
        let r=if t&1!=0{(15usize.wrapping_sub(b*v).wrapping_mul(super::q793_exit_low::INV16[t]))&15}else{b};
        (r>>3&1!=0)&&(z>>y_index&1!=0)
    }).collect();
    for bit in 0..17{for m in 0..1<<17{if m>>bit&1!=0{anf[m]^=anf[m^(1<<bit)];}}}
    let owned=circ.b.next_qubit;let start=circ.b.ops.len();
    for(m,on)in anf.into_iter().enumerate(){
        if !on||(m>>12).count_ones()>1{continue;}
        let mut cs=vec![(mask,true)];
        cs.extend((0..12).filter(|&i|m>>i&1!=0).map(|i|(chart[i],true)));
        for f in 0..5{if m>>(12+f)&1!=0{
            let av=[0usize,1,2,254,253][f];let rv=if f>=3{29}else{0};
            cs.extend((0..5).map(|i|(&rank[i],rv>>i&1!=0)));
            cs.extend((0..6).map(|i|(&a[i],av>>i&1!=0)));
        }}gate(circ,&cs,carry,dirty);
    }
    // Dead mask: the accepted step still toggles the carry by `y` alone.
    gate(circ,&[(mask,false),(chart[y_index],true)],carry,dirty);
    assert_eq!(circ.b.next_qubit,owned);
    for op in &circ.b.ops[start..]{for &h in [255usize,256,257,258].as_slice(){let q=w1[h].id()as u64;
        assert!(op.q_target.0!=q&&op.q_control1.0!=q&&op.q_control2.0!=q,"R00 bit3 callback touched hole{h}");
    }}
}
