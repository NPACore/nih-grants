#!/usr/bin/env Rscript
pacman::p_load(dplyr,readxl,readr)

gs <- \(x, pat, rep, ...) gsub(pat,rep,x,...)
harmonize_names <- function(nm) {
    gsub("^Type$", "Application Type", nm) |>
        gs("^Acti?v(ity)?$", "Activity Code") |>
        gs("^Conact", "Contact") |>
        gs("PI MI Name", "PI Middle Name") |>
        gs("^Project$","Project Number") |>
        gs("^Awa?r?d Tota?l?","Award Total") |>
        gs("Institution", "Organization") |>
        gs("^PI ([^N])","Contact PI \\1")
}

stem_contact <- function(x) gsub('^ | $','', gsub(' +', ' ', tolower(x)))
email_trans <- function(email_df) {
    email_df |> transmute(
        email=`Contact PI Email`,
        contact_pi=paste(sep=" ",
                         `Contact PI First Name`,
                         ifelse(is.na(`Contact PI Middle Name`),
                                "",`Contact PI Middle Name`),
                         `Contact PI Last Name`),
        contact_pi=stem_contact(contact_pi),
        project_num=`Project Number`,
        main_num=gsub('-.*','',project_num),
        org=`Organization`,
        all_pis=`PI Name(s) All`,
        award_type=`Application Type`,
        cost_email=`Award Total $`,
        data_from)
}

combine_emals <- function() {
  emails <- lapply(Sys.glob('xlsx/*csv.gz'),
                   \(f) read_csv(f, show_col_types=FALSE) |>
                        mutate(data_from=gsub('.csv.gz','',basename(f))))
  # # checkout all the ways names don't overlap
  # all_names <- lapply(emails, names)
  # all_names |> lapply(\(x) x |> t() |> data.frame()) %>% bind_rows

  # options(crayon.enabled = FALSE)
  emails_combined <-
      lapply(emails,
             \(x) x|>rename_with(harmonize_names)|>email_trans()) |>
      bind_rows()

  outname <- paste0("emails_FY",
                    min(emails_combined$data_from), ":",
                    max(emails_combined$data_from), ".csv.gz")
  write_csv(emails_combined, outname)
}
