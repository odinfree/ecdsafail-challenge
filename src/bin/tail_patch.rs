//! Local nonce tooling; not part of the submission.
use std::fs::File;
use std::io::{BufReader, BufWriter, Read, Write};
use std::path::Path;

const MAGIC: &[u8; 8] = b"QECCOPSZ";
const OP_BYTES: usize = 56;

fn main() -> std::io::Result<()> {
    let nonce: u64 = std::env::args().nth(1).and_then(|s| s.parse().ok())
        .expect("usage: tail_patch NONCE OUTDIR");
    let outdir = std::env::args().nth(2).expect("usage: tail_patch NONCE OUTDIR");
    let mut f = BufReader::new(File::open("ops.bin")?);
    let mut magic = [0u8; 8];
    f.read_exact(&mut magic)?;
    assert_eq!(&magic, MAGIC);
    let mut cntb = [0u8; 8];
    f.read_exact(&mut cntb)?;
    let count = u64::from_le_bytes(cntb);
    let tail_start = count.checked_sub(96).expect("op stream too short");
    std::fs::create_dir_all(&outdir)?;
    let mut w = BufWriter::new(File::create(Path::new(&outdir).join("ops.bin"))?);
    w.write_all(MAGIC)?;
    w.write_all(&cntb)?;
    let mut dec = zstd::stream::read::Decoder::new(f)?;
    let mut enc = zstd::stream::write::Encoder::new(w, 3)?;
    let mut rec = [0u8; OP_BYTES];
    for idx in 0..count {
        dec.read_exact(&mut rec)?;
        if idx >= tail_start {
            let bit = ((idx - tail_start) / 2) as u32;
            let target = (nonce >> bit) & 1;
            rec[24..32].copy_from_slice(&target.to_le_bytes());
        }
        enc.write_all(&rec)?;
    }
    enc.finish()?;
    Ok(())
}
