library(tidyverse)
library(dplyr)
library(lubridate)

ater <- read_csv('ater.csv') %>%
  mutate_at(vars(contains('date')), dmy) %>%
  arrange(date_cloture_cand, date_ouverture_cand)

# Nombres de postes
ater %>%
  group_by(etablissement, section1) %>%
  summarise(cloture = min(date_cloture_cand),
            postes = n()) %>%
  arrange(cloture) %>%
  print(n = Inf)

# Calendrier
ater %>%
  group_by(etablissement) %>%
  mutate(dossier = case_when(
          !is.na(dossier_email_adr) ~ dossier_email_adr,
          !is.na(dossier_appli_url) ~ dossier_appli_url,
          dossier_papier == "oui" ~ "papier",
          TRUE ~ "?")) %>%
  summarise(sections = paste(unique(str_extract(section1, "\\d{2}")), collapse = ", "),
            postes = n(),
            cloture = min(date_cloture_cand),
            dossier = min(dossier)
            ) %>%
  arrange(cloture)
