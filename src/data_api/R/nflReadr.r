# --- QUICK FIX: use a user-writable library on Windows ---
userlib <- file.path(Sys.getenv("USERPROFILE"), "Documents", "R", "win-library",
                     paste0(R.version$major, ".", sub("\\..*$","", R.version$minor)))
dir.create(userlib, recursive = TRUE, showWarnings = FALSE)

# Put user library first so installs & library() use it
.libPaths(c(userlib, .libPaths()))
Sys.setenv(R_LIBS_USER = userlib)

# Verify
print(.libPaths())

# Install needed packages into the user library
install.packages(c("nflverse","nflreadr","openxlsx"),
                 lib = userlib, repos = "https://cloud.r-project.org",
                 dependencies = TRUE)

# Load from user library
library(nflreadr, lib.loc = userlib)
library(openxlsx, lib.loc = userlib)

# --- your code ---
all_stats <- load_player_stats(seasons = TRUE)
openxlsx::write.xlsx(all_stats, "nfl_all_player_stats.xlsx", rowNames = FALSE)

depth <- load_depth_charts(seasons = TRUE)
openxlsx::write.xlsx(depth, "nfl_depth_charts.xlsx", rowNames = FALSE)

injuries <- load_injuries(seasons = TRUE)
openxlsx::write.xlsx(injuries, "nfl_injuries.xlsx", rowNames = FALSE)

team_stats <- load_team_stats(seasons = TRUE)
openxlsx::write.xlsx(team_stats, "nfl_team_stats.xlsx", rowNames = FALSE)
