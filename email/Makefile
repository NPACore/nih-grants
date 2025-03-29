.PHONY: all
all: nih_emails.db

contactpi_emails_2022v2024.csv: 2022-pi-email-report.xlsx ../FY2024_PI-repeat.csv
	./01_merge_emails2022.R

webid_missing_contacts.txt: ../FY2024_PI-repeat.csv contactpi_emails_2022v2024.csv
	./02_webid_of_emailmissing.R

nih_emails.db: webid_missing_contacts.txt
	./03_create_db.bash
