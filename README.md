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
`Rduckhts` from R-universe at runtime. Bundled centromere, merged whole-gene
locus, merged exon, and merged CDS BED annotations are loaded into DuckDB for
annotation coverage views. For each annotation family, DuckBedQC reports the
fraction of annotation intervals hit by the uploaded BED, the fraction of
annotation bases covered by the BED, and exports overlapping or uncovered
annotation BED rows for kit-style review.

[BED file specification](https://samtools.github.io/hts-specs/BEDv1.pdf).

The browser SQL backend uses:

- [webR](https://docs.r-wasm.org/webr/latest/)
- [DuckDB](https://duckdb.org/)
- [Rduckhts](https://github.com/RGenomicsETL/duckhts)
