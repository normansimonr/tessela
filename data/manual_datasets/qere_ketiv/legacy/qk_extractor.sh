grep "=Q(K)" "TAHOT Gen-Deu - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt" \
  > "Gen-Deu.tsv"
  
grep "=Q(K)" "TAHOT Jos-Est - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt" \
  > "Jos-Est.tsv"
  
grep "=Q(K)" "TAHOT Job-Sng - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt" \
  > "Job-Sng.tsv"
  
grep "=Q(K)" "TAHOT Isa-Mal - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt" \
  > "Isa-Mal.tsv"
  
  
cat Gen-Deu.tsv Jos-Est.tsv Job-Sng.tsv Isa-Mal.tsv > OT-QK.tsv



