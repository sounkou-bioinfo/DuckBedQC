#!/usr/bin/env python3
"""Build canonical-transcript BED assets for DuckBedQC.

Sources (UCSC public tables):
  - knownCanonical.txt.gz (canonical transcript IDs)
  - knownGene.txt.gz      (transcript coordinates and exon structures)
  - kgXref.txt.gz         (gene symbols)

Outputs (BED4):
  - GRCh37_gene_loci.bed
  - GRCh37_exons.bed
  - GRCh37_exons_protein_coding.bed
  - GRCh37_cds.bed
  - GRCh38_gene_loci.bed
  - GRCh38_exons.bed
  - GRCh38_exons_protein_coding.bed
  - GRCh38_cds.bed
"""

from __future__ import annotations

import gzip
import urllib.request
from pathlib import Path


UCSC_BASE = "https://hgdownload.soe.ucsc.edu/goldenPath/{db}/database/{table}.txt.gz"
BUILD_TO_DB = {
    "GRCh37": "hg19",
    "GRCh38": "hg38",
}


def load_table(db: str, table: str) -> list[list[str]]:
    url = UCSC_BASE.format(db=db, table=table)
    with urllib.request.urlopen(url, timeout=120) as response:
        raw = response.read()
    text = gzip.decompress(raw).decode("utf-8")
    return [line.split("\t") for line in text.splitlines() if line]


def chrom_sort_key(chrom: str) -> tuple[int, int | str]:
    if chrom.startswith("chr"):
        tail = chrom[3:]
        if tail.isdigit():
            return (0, int(tail))
        special = {"X": 23, "Y": 24, "M": 25, "MT": 25}
        if tail in special:
            return (0, special[tail])
        return (1, tail)
    return (2, chrom)


def write_bed(path: Path, rows: list[tuple[str, int, int, str]]) -> None:
    rows.sort(key=lambda r: (chrom_sort_key(r[0]), r[1], r[2], r[3]))
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for chrom, start, end, name in rows:
            handle.write(f"{chrom}\t{start}\t{end}\t{name}\n")


def build_for_db(build_label: str, db: str, out_dir: Path) -> None:
    canonical_rows = load_table(db, "knownCanonical")
    canonical_ids = {row[4] for row in canonical_rows if len(row) >= 5}

    kgxref_rows = load_table(db, "kgXref")
    gene_by_transcript = {
        row[0]: row[4] for row in kgxref_rows if len(row) >= 5 and row[4]
    }

    known_attrs_rows = load_table(db, "knownAttrs")
    protein_coding_transcripts = {
        row[0]
        for row in known_attrs_rows
        if len(row) >= 4 and row[3] == "protein_coding"
    }

    known_gene_rows = load_table(db, "knownGene")

    gene_rows: list[tuple[str, int, int, str]] = []
    exon_rows: list[tuple[str, int, int, str]] = []
    exon_rows_protein_coding: list[tuple[str, int, int, str]] = []
    cds_rows: list[tuple[str, int, int, str]] = []

    for row in known_gene_rows:
        if len(row) < 12:
            continue

        tx_id = row[0]
        if tx_id not in canonical_ids:
            continue

        chrom = row[1]
        tx_start = int(row[3])
        tx_end = int(row[4])
        cds_start = int(row[5])
        cds_end = int(row[6])
        exon_starts = [int(x) for x in row[8].split(",") if x]
        exon_ends = [int(x) for x in row[9].split(",") if x]

        gene_symbol = gene_by_transcript.get(tx_id, "")
        base_name = f"{gene_symbol}|{tx_id}" if gene_symbol else tx_id

        gene_rows.append((chrom, tx_start, tx_end, base_name))

        cds_index = 0
        for exon_index, (exon_start, exon_end) in enumerate(
            zip(exon_starts, exon_ends), start=1
        ):
            exon_name = f"{base_name}|exon{exon_index}"
            exon_rows.append((chrom, exon_start, exon_end, exon_name))
            if tx_id in protein_coding_transcripts:
                exon_rows_protein_coding.append(
                    (chrom, exon_start, exon_end, exon_name)
                )

            overlap_start = max(exon_start, cds_start)
            overlap_end = min(exon_end, cds_end)
            if overlap_start < overlap_end:
                cds_index += 1
                cds_rows.append(
                    (chrom, overlap_start, overlap_end, f"{base_name}|cds{cds_index}")
                )

    write_bed(out_dir / f"{build_label}_gene_loci.bed", gene_rows)
    write_bed(out_dir / f"{build_label}_exons.bed", exon_rows)
    write_bed(
        out_dir / f"{build_label}_exons_protein_coding.bed",
        exon_rows_protein_coding,
    )
    write_bed(out_dir / f"{build_label}_cds.bed", cds_rows)

    print(
        f"{build_label}: "
        f"{len(gene_rows)} loci, {len(exon_rows)} exons "
        f"({len(exon_rows_protein_coding)} protein-coding), {len(cds_rows)} CDS segments"
    )


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    for build_label, db in BUILD_TO_DB.items():
        build_for_db(build_label, db, out_dir)


if __name__ == "__main__":
    main()
