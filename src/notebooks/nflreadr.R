install.packages("nflverse")
install.packages("nflreadr")


library(nflreadr)
library(openxlsx)

all_stats <- load_player_stats(seasons = TRUE)

write.xlsx(all_stats, "nfl_all_player_stats.xlsx", rowNames = FALSE)

depth <- load_depth_charts(seasons = TRUE)

write.xlsx(depth, "nfl_depth_charts.xlsx", rowNames = FALSE)
