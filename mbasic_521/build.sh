#!/bin/bash
# Build mbasic from sources

mkdir -p out

# Assemble all modules
for f in bintrp f4 biptrg biedit biprtu bio bimisc bistrs binlin fiveo dskcom dcpm fivdsk init; do
    echo "Assembling $f.mac..."
    python3 -m um80.um80 mbasic_src/$f.mac -o out/$f.rel 2>&1 | grep -v "^$"
done

# Link with symbol output
echo "Linking..."
python3 -m um80.ul80 -o out/mbasic_go.com -s \
  out/bintrp.rel out/f4.rel out/biptrg.rel out/biedit.rel \
  out/biprtu.rel out/bio.rel out/bimisc.rel out/bistrs.rel \
  out/binlin.rel out/fiveo.rel out/dskcom.rel out/dcpm.rel \
  out/fivdsk.rel out/init.rel 2>&1

echo "Done: out/mbasic_go.com"
ls -la out/mbasic_go.com out/mbasic_go.sym 2>/dev/null
