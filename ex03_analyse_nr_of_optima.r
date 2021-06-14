library(tidyverse)
library(ggplot2)
library(scales)
library(RColorBrewer)

# READ RAW OUTPUT FILES AND SAVE IN TABLE
# ===
# outfiles = list.files("data/output/raw", pattern = "csv$", full.names = TRUE)
# res = do.call(rbind, lapply(outfiles, function(of) {
#   readr::read_delim(of,
#     delim = ",",
#     col_names = c("generator", "L", "R", "n", "h", "run", "nsols")
#   )
# }))
# write.table(res, file = "data/output/ex01_nr_of_optima.csv", row.names = FALSE, col.names = TRUE, quote = TRUE)


# ANALYSIS
# ===

tbl = readr::read_delim("data/output/ex01_nr_of_optima.csv", delim = " ")

tbl = filter(tbl, generator != "usw") # , h == 2

tblaggr = tbl %>%
  group_by(generator, L, R, h, n) %>%
  dplyr::summarize(median = median(nsols), mean = mean(nsols), q01 = quantile(nsols, probs = 0.1), q09 = quantile(nsols, probs = 0.9)) %>%
  ungroup()

# ordering
tbl$generator = factor(tbl$generator, levels = c("uncorr", "wcorr", "ascorr", "scorr", "ss", "invscorr"), ordered = TRUE)

# Show knapsack capacity as percentange of sum of weights
H = 11
tbl$hperc = paste0(round((tbl$h / (H + 1)) * 100, digits = 0), "%")
tbl$hperc = factor(tbl$hperc, levels = c("8%", "17%", "25%", "33%", "42%", "50%", "58%", "67%", "75%", "83%", "92%"), ordered = TRUE)

# Define the number of colors you want
nb.cols = length(unique(tbl$hperc))
mycolors = colorRampPalette(brewer.pal(8, "Dark2"))(nb.cols)

# Combine (type, L, R)
tbl$R = factor(sprintf("R = %i", tbl$R), levels = c("R = 50", "R = 100", "R = 250"), ordered = TRUE)
#tbl$split = sprintf("%s, L=1, R=%s", tbl$generator, tbl$R)

#tbl = filter(tbl, generator == "ss", n <= 300)
g = ggplot(tbl, aes(x = as.factor(n), y = nsols))
g = g + geom_boxplot(aes(color = as.factor(hperc)), alpha=0.7)
g = g + facet_wrap(generator~R, scales = "free_y", ncol = 3)
# g = g + geom_point(data = tblaggr, aes(x = as.factor(n), y = mean), shape = 8, color = "blue", size = 2.5)
g = g + scale_y_continuous(trans = log2_trans(),
  breaks = trans_breaks("log2", function(x) 2^x),
  labels = trans_format("log2", math_format(2^.x)))
#g = g + annotation_logticks(sides = "l")
g = g + scale_color_manual(values = mycolors)
#g = g + scale_color_grey(end = 0.8)
g = g + theme_bw()
g = g + theme(legend.position = "top")#, axis.text.x = element_text(angle = 45))
g = g + guides(color = guide_legend(nrow = 1L))
g = g + labs(x = "n", y = "Nr. of optima (log-scaled)", color = "d / (D+1) (in percent of sum of weights)")
#print(g)
ggsave("figures/n_vs_nsols_all.pdf", width = 16, height = 20, device = cairo_pdf)
