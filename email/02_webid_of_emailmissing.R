#!/usr/bin/env Rscript
pacman::p_load(dplyr, readr)
# for web scraper, get a list of all missing an email and find their first project

grant_pis <- read_csv('../grants_PI-repeat_FY-2001:2025.csv.gz') |>
    filter(grepl("2024",pklsrc))
grant_email_sub <- read_csv("./contactpi_emails_all.csv.gz")

all_contacts <- grant_pis |>
    select(web_id, contact_pi) |>
    filter(!duplicated(contact_pi))

have_emails <- grant_email_sub$pi
missing <- all_contacts |> filter(!contact_pi %in% have_emails)

# save for reading in with sqlite3 '.import'
sink('webid_missing_contacts.txt')
cat(paste(collapse="\n", missing$web_id),"\n")
sink()
