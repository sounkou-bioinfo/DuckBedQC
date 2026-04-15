# DuckBedQC

DuckBedQC is a browser tool to validate and profile genomic intervals in BED format.

Once you upload a file to DuckBedQC, it will automatically
compare your file to the BED specifications, including 
checking the delimiter and line endings. A count
of intervals and their lengths will also tabulated 
and presented. No data is transferred from your local environment.

Once a BED file is uploaded, you can choose to perform more complex tasks
on your BED file including calculating metrics based on the
intervals and intersecting your file with various other
annotations. This fork keeps the validation flow in JavaScript and runs overlap
queries in-browser through `webR`, `duckdb`, and `Rduckhts`, installing
`Rduckhts` from R-universe at runtime. Bundled centromere and canonical-transcript
gene locus/exon/CDS BED annotations are loaded into DuckDB for
annotation coverage views. For each annotation family, DuckBedQC reports the
fraction of annotation intervals hit by the uploaded BED, the fraction of
annotation bases covered by the BED, and exports overlapping or uncovered
annotation BED rows for kit-style review.

## Downloaded overlap BED columns

`*_overlapping.bed` and `*_uncovered.bed` keep the annotation row columns as loaded.

- Centromeres: `chrom`, `start`, `end`
- Canonical whole-gene: `chrom`, `start`, `end`, `name`
- Canonical exon: `chrom`, `start`, `end`, `name`
- Canonical CDS: `chrom`, `start`, `end`, `name`

For canonical tracks, `name` is:

- gene locus: `GENE|TRANSCRIPT`
- exon rows: `GENE|TRANSCRIPT|exonN`
- CDS rows: `GENE|TRANSCRIPT|cdsN`

Coordinates use standard BED semantics: 0-based `start`, half-open `end`.

## Canonical annotation assets

Canonical assets in `data/GRCh37_*.bed` and `data/GRCh38_*.bed` are generated from
UCSC tables:

- `knownCanonical` for canonical transcript membership
- `knownGene` for transcript/exon/CDS intervals
- `kgXref` for gene symbols

Regenerate with:

```bash
python3 data/build_canonical_annotations.py
```

[BED file specification](https://samtools.github.io/hts-specs/BEDv1.pdf).

The browser SQL backend uses:

- [webR](https://docs.r-wasm.org/webr/latest/)
- [DuckDB](https://duckdb.org/)
- [Rduckhts](https://github.com/RGenomicsETL/duckhts)
