#!/usr/bin/Rscript
# merge 2022 report w/emails to 2024 nih cost pull
# makes 'contactpi_emails_2022v2024.csv'
#
# limitations:
#  * emails only for contact pis
#  * only 28507/50563 (56%) match from 2022 to 2024 contact pis
#
# 2022 email dataframe 63560 rows long
# there are ~ 9,000 fewer contacts for 2022 as 2024?
#
#  length(unique(emails_all$`Contact PI Email`)) == 41585
#  length(unique(grant_pis$contact_pi))  == 50563
#
# 20250329WF - init
# 20250413WF - move to larger email inputsj
pacman::p_load(tidyr,dplyr,readxl, readr)
source('00.2_combine_emails.R') # stem_contact
emails_all <- read_csv('./emails_FY2015:2022.csv.gz') # ./00.2_combine_emails.R
grant_pis <- read_csv('../grants_PI-repeat_FY-2001:2025.csv.gz') |>
    filter(grepl("2024",pklsrc))


grant_contact <-
    grant_pis |>
    filter(contact_pi == pi, contact_pi != "") |>
    separate(contact_pi, c("contact_id", "contact_pi"),
             sep=":", fill="left") |>
    mutate(contact_pi = stem_contact(contact_pi))

grant_email <- merge(grant_contact, emails_all,
                     by="contact_pi",
                     suffixes=c(".grant",".email"))

grant_email_sub <- grant_email |>
    group_by(contact_pi, pi) |>
    summarise(emails=paste(email, collapse=", "), n=n())

write_csv(grant_email_sub, 'contactpi_emails_all.csv.gz')

length(unique(grant_pis$contact_pi)) # 50563
nrow(grant_email_sub) #  with all nih FoI: 34233 (previously 28507)
