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
library(pacman)
p_load(tidyr,dplyr,readxl)
emails_all <- read_excel('2022-pi-email-report.xlsx')
grant_pis <- read.csv('FY2024_PI-repeat.csv')

emails <- emails_all |>
    transmute(
        email=`Contact PI Email`,
        contact_pi=paste(sep=" ",
                         `Contact PI First Name`,
                         ifelse(is.na(`Contact PI Middle Name`),
                                "",`Contact PI Middle Name`),
                         `Contact PI Last Name`),
        contact_pi=tolower(contact_pi),
        project_num=`Project Number`,
        main_num=gsub('-.*','',project_num),
        org=`Organization`,
        all_pis=`PI Name(s) All`,
        award_type=`Application Type`,
        cost_email=`Award Total $`)

grant_contact <-
    grant_pis |>
    filter(contact_pi == pi) |>
    separate(contact_pi, c("contact_id", "contact_pi"), sep=":", fill="left") |>
    mutate(contact_pi = tolower(contact_pi))

grant_email <- merge(grant_contact,emails, by="contact_pi", suffixes=c(".grant",".email"))

grant_email_sub <- grant_email |> count(contact_pi, pi, email)
write.csv(grant_email_sub,'contactpi_emails_2022v2024.csv',row.names=F)

length(unique(grant_pis$contact_pi)) # 50563
nrow(grant_email_sub) # 28507

## for web scraper, get a list of all missing an email and find their first project
all_contacts <- grant_pis |> select(web_id, contact_pi) |>
              filter(!duplicated(contact_pi))
have_emails <- grant_email_sub$pi
missing <- all_contacts |> filter(!contact_pi %in% have_emails)
sink('webid_missing_contacts.txt')
