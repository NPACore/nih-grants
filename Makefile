.PHONY: all
.SUFFIXES: 
all: data/abstracts.csv.zip data/abstract_srg_summary.tsv

data/2025.pkl:
	./get_grants.py

# TODO: per year files? adding a year requires reparsing all years
data/abstracts.csv: $(wildcard data/*.pkl) ./get_abstracts.py data/2025.pkl
	./get_abstracts.py
data/abstracts.csv.zip: data/abstracts.csv 
	zip $@ $<
	du -h data/abstracts.csv*
data/abstract_srg_summary.tsv: data/abstracts.csv
	duckdb -csv -separator $$'\t' $< "select srg, count(*) as n, group_concat(distinct year) as years from abstracts group by srg order by n desc;" > $@

grants_PI-repeat_FY-2001\:2025.csv.gz: data/2025.pkl
	./grants_to_csv.py

email/emails_FY2015\:2022.csv.gz:
	cd email && \
	./00_get_nih_foi_xlsx.pl && \
	./00.1_rm_header.bash && \
	./00.2_combine_emails.R
