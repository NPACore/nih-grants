data/2024.pkl:
	./get_grants.py

grants_PI-repeat_FY-2001\:2025.csv.gz: data/2020.pkl
	./grants_to_csv.py

email/emails_FY2015\:2022.csv.gz:
	cd email && \
	./00_get_nih_foi_xlsx.pl && \
	./00.1_rm_header.bash && \
	./00.2_combine_emails.R
