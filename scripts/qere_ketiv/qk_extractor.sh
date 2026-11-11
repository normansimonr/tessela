#!/usr/bin/env bash
# qk_extractor.sh — extract the Qere/Ketiv rows and the lemma index from the
# STEPBible TAHOT files.
#
# Usage:
#   scripts/qere_ketiv/qk_extractor.sh <tahot-dir> <out-dir>
#
# Inputs:
#   Four STEPBible "Translators Amalgamated Hebrew OT" (TAHOT) files, CC BY 4.0,
#   named exactly as STEPBible publishes them:
#     <tahot-dir>/TAHOT Gen-Deu - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt
#     <tahot-dir>/TAHOT Jos-Est - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt
#     <tahot-dir>/TAHOT Job-Sng - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt
#     <tahot-dir>/TAHOT Isa-Mal - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt
#
# Outputs:
#   <out-dir>/extracted/{Gen-Deu,Jos-Est,Job-Sng,Isa-Mal}.tsv — the matching lines
#     of each source file, verbatim apart from trimmed trailing padding
#     (intermediates).
#   <out-dir>/OT-QK.tsv — the four extractions concatenated, in the same order.
#   <out-dir>/lemmas.tsv — Strong's tag to pointed lemma, one pair per line,
#     taken from TAHOT's expanded tags and sorted by tag. It lets the analyser
#     give the root of a reading without re-reading the 68 MB sources.
#
# Each kept line carries a Qere whose only variant is the plain Ketiv, marked
# "=Q(K)" in the reference column (TAHOT also marks composite variants such as
# "=Q(K+B)"; those are deliberately not matched, because the ")" must follow
# the "K").
#
# This is stage 1 of 3; run scripts/qere-ketiv to run the whole pipeline.

set -euo pipefail

usage() {
    awk 'NR == 1 { next } /^#/ { sub(/^# ?/, ""); print; next } { exit }' "$0"
    exit 0
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" || $# -ne 2 ]]; then
    usage
fi

tahot_dir=$1
out_dir=$2

ranges=(Gen-Deu Jos-Est Job-Sng Isa-Mal)
mkdir -p "${out_dir}/extracted"

lemma_raw="${out_dir}/.lemmas.raw"
trap 'rm -f "${lemma_raw}"' EXIT
: > "${lemma_raw}"

for range in "${ranges[@]}"; do
    src="${tahot_dir}/TAHOT ${range} - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt"
    if [[ ! -f "${src}" ]]; then
        echo "qk_extractor.sh: missing TAHOT source file: ${src}" >&2
        exit 1
    fi
    dst="${out_dir}/extracted/${range}.tsv"
    # Keep only the plain Q(K) lines, with LF endings and without the tab
    # padding that TAHOT leaves at the end of some lines (it carries no data
    # and would trip the repository's trailing-whitespace guardrail).
    if ! grep "=Q(K)" "${src}" | sed -e 's/\r$//' -e 's/[[:blank:]]*$//' > "${dst}"; then
        echo "qk_extractor.sh: no Qere/Ketiv rows found in: ${src}" >&2
        exit 1
    fi
    if [[ ! -s "${dst}" ]]; then
        echo "qk_extractor.sh: no Qere/Ketiv rows found in: ${src}" >&2
        exit 1
    fi
    printf 'extracted %s rows from %s\n' "$(wc -l < "${dst}")" "${range}"

    # Expanded tags look like '{H0168G=אֹ֫הֶל=: tent...', so the lemma sits
    # between the first and second '='.
    grep -hoE '\{[HG][0-9]+[A-Z]?=[^=]+\=' "${src}" >> "${lemma_raw}"
done

cat "${out_dir}/extracted/Gen-Deu.tsv" \
    "${out_dir}/extracted/Jos-Est.tsv" \
    "${out_dir}/extracted/Job-Sng.tsv" \
    "${out_dir}/extracted/Isa-Mal.tsv" > "${out_dir}/OT-QK.tsv"

sed -e 's/^{//' -e 's/=$//' "${lemma_raw}" \
    | sort -u \
    | awk -F'=' '!seen[$1]++ { print $1 "\t" $2 }' \
    | sort > "${out_dir}/lemmas.tsv"

printf 'wrote %s Qere/Ketiv rows to %s\n' "$(wc -l < "${out_dir}/OT-QK.tsv")" "${out_dir}/OT-QK.tsv"
printf 'indexed %s lemmas in %s\n' "$(wc -l < "${out_dir}/lemmas.tsv")" "${out_dir}/lemmas.tsv"
