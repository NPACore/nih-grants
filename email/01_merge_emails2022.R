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
pacman::p_load(tidyr,dplyr,readxl,readr)
source('00.2_combine_emails.R') # stem_contact
emails_all <- read_csv('./emails_FY2015:2022.csv.gz') |> # ./00.2_combine_emails.R
    filter(grepl('@',email))|>
    # standard says local part is case-sensitive. but not in practice?
    mutate(email=tolower(email),
           email=gsub("[' \"\t]","", email))

# "email" "contact_pi"  "project_num" "main_num"    "org"         "all_pis"
# "award_type"  "cost_email" "data_from"

grant_pis <- read_csv('../grants_PI-repeat_FY-2001:2025.csv.gz') |>
    filter(grepl("2024",pklsrc))
# "pi"                 "contact_pi"         "project_num"        "award_type"         "award_amount"
# "project_start_date" "project_end_date"   "budget_start"       "budget_end"         "funding_mechanism"
# "direct_cost_amt"    "indirect_cost_amt"  "org"                "study_code"         "web_id"
# "pklsrc"


grant_contact <-
    grant_pis |>
    filter(contact_pi == pi, contact_pi != "") |>
    separate(contact_pi, c("contact_id", "contact_pi"),
             sep=":", fill="left") |>
    mutate(contact_pi = stem_contact(contact_pi))

grant_email <- merge(grant_contact, emails_all,
                     by="contact_pi",
                     suffixes=c(".grant",".email"))

# used by 02_webid_of_emailmissing.R (which isn't used anymore)
grant_email_sub <- grant_email |>
    group_by(contact_pi, pi) |>
    summarise(emails=paste(email, collapse=", "), n=n())

write_csv(grant_email_sub, 'contactpi_emails_all.csv.gz')

length(unique(grant_pis$contact_pi)) # 50563
nrow(grant_email_sub) #  with all nih FoI: 34233 (previously 28507)

## try to reduce (or at least understand) duplicated
# contact_pi isn't unique for
grant_email_byyear <-  grant_email |>
    group_by(contact_pi, pi) |>
    select(email, foi_year=data_from) |>
    unique() |>
    mutate(n=n()) |>
    arrange(-n, contact_pi, -foi_year)

# for inspecting repeats
grant_email_sub_reps <- grant_email_byyear |>
    select(email, foi_year) |>
    unique() |>
    summarise(emails=paste(email, collapse=", "), n_email=n(), year=max(foi_year)) |>
    ungroup()|>group_by(contact_pi) |> mutate(n_names=n())

# ~33k with unique name. but 100s with repeat names (
grant_email_sub_reps |> ungroup() |> count(n_names)
#  n_names     n
#    <int> <int>
#        1 32856
#        2   482
#        3   102
#        4    56
#        5    35
#        6    12
#        8     8
#        9     9
#       12    12

grant_email_sub_reps |> select(contact_pi, n_names) |> unique() |> arrange(-n_names)
# contact_pi       n_names
# <chr>              <int>
# ethan d*********      12
# jun w***               9
# barbara d*****         8

email_only <- grant_email_byyear |>
    filter(foi_year==max(foi_year)) |>
    ungroup() |>
    select(contact_pi, email) |>
    unique()
write_csv(email_only, '2024_pis_emails.csv.gz')

emails_all_smry <- emails_all |>
  select(email, foi_year=data_from) |>
  group_by(`email`) |>
  summarise(first_seen=min(foi_year),
            last_seen=max(foi_year),
            n=n())

write_csv(emails_all_smry, 'all_pi_emails.csv.gz')
