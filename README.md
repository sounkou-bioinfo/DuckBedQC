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
- Canonical exon (protein-coding): `chrom`, `start`, `end`, `name`
- Canonical exon: `chrom`, `start`, `end`, `name`
- Canonical CDS: `chrom`, `start`, `end`, `name`

For canonical tracks, `name` is:

- gene locus: `GENE|TRANSCRIPT`
- exon rows: `GENE|TRANSCRIPT|exonN`
- CDS rows: `GENE|TRANSCRIPT|cdsN`

Coordinates use standard BED semantics: 0-based `start`, half-open `end`.

## Report export

For annotation overlap analyses, DuckBedQC can export:

- report HTML (`Download report HTML`)
- report PDF (`Export report PDF`, via browser print/save flow)

The report includes genome build, annotation track, interval/base coverage summary,
per-chromosome coverage table, and input BED interval length statistics.

## Live ClinVar for uncovered intervals

For overlap analyses, DuckBedQC can query live indexed ClinVar VCF over HTTPS to
prioritize uncovered intervals with potential medical relevance.

- Genome-specific sources:
  - hg38: `https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz`
  - hg19: `https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/clinvar.vcf.gz`
- Click `Analyze uncovered with live ClinVar` in the overlap results panel.
- Download outputs:
  - `*_uncovered_with_clinvar.tsv`
  - `*_clinvar_summary.tsv`

Live mode depends on runtime HTTPS access and indexed range retrieval in the browser.

ClinVar INFO fields can be scalar or list-typed depending on source headers; the
live query path normalizes key ClinVar fields to `VARCHAR` text before
pathogenicity matching to keep browser DuckDB binding stable.

To avoid one-query-per-interval overhead, the live ClinVar loader groups uncovered
contig windows into batched region queries and appends results incrementally.

## Canonical annotation assets

Canonical assets in `data/GRCh37_*.bed` and `data/GRCh38_*.bed` are generated from
UCSC tables:

- `knownCanonical` for canonical transcript membership
- `knownGene` for transcript/exon/CDS intervals
- `knownAttrs` for transcript type (`protein_coding` filtering)
- `kgXref` for gene symbols

Regenerate with:

```bash
python3 data/build_canonical_annotations.py
```

## CMRG benchmark annotations

DuckBedQC includes CMRG gene coordinate BEDs for both hg19/GRCh37 and hg38/GRCh38:

- `CMRG benchmark genes`
- `CMRG full genes`
- `CMRG full exons`
- `CMRG genes + flank`

Source repository:

- `https://github.com/usnistgov/cmrg-benchmarkset-manuscript`
- Path used: `data/gene_coords/unsorted/*.bed`

Paper citation:

- Wagner J, Olson ND, Harris L, et al. *Towards a Comprehensive Variation
  Benchmark for Challenging Medically-Relevant Autosomal Genes*. bioRxiv.
  2021.06.07.444885. doi: `10.1101/2021.06.07.444885`.

## Illumina Emedgene ROI annotations

DuckBedQC includes default Illumina Emedgene ROI BEDs (v100.39.0+) for both hg19
and hg38:

- `Illumina Clinical Regions (v100.39.0+)`
- `Illumina Full Genes (v100.39.0+)`

Files are sourced from Illumina help documentation page:

- `https://help.emg.illumina.com/emedgene-analyze-manual/launching-analysis/creating_a_single_case/case-type-and-region-of-interest/genomic_regions_by_case_type#clinical-regions`

Bundled filenames:

- `data/GRCh37_illumina_clinical_regions_v100.39.0.bed`
- `data/GRCh38_illumina_clinical_regions_v100.39.0.bed`
- `data/GRCh37_illumina_full_genes_v100.39.0.bed`
- `data/GRCh38_illumina_full_genes_v100.39.0.bed`

[BED file specification](https://samtools.github.io/hts-specs/BEDv1.pdf).

The browser SQL backend uses:

- [webR](https://docs.r-wasm.org/webr/latest/)
- [DuckDB](https://duckdb.org/)
- [Rduckhts](https://github.com/RGenomicsETL/duckhts)
