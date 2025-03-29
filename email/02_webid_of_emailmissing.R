#!/usr/bin/env Rscript
pacman::p_load(dplyr)
# for web scraper, get a list of all missing an email and find their first project
grant_pis <- read.csv('FY2024_PI-repeat.csv')
grant_email_sub <- read.csv("./contactpi_emails_2022v2024.csv")

all_contacts <- grant_pis |>
    select(web_id, contact_pi) |>
    filter(!duplicated(contact_pi))

have_emails <- grant_email_sub$pi
missing <- all_contacts |> filter(!contact_pi %in% have_emails)

# save for reading in with sqlite3 '.import'
sink('webid_missing_contacts.txt')
cat(paste(collapse="\n", missing$web_id),"\n")
sink()
