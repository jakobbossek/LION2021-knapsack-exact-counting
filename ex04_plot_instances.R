library(ggplot2)
library(tidyverse)

infiles = list.files("data/example_instances/", full.names = TRUE)

tbl = do.call(rbind, lapply(infiles, function(f) {
  tmp = read.table(f, skip = 1L, header = FALSE, sep = " ")
  tmp$type = gsub(".csv", "", basename(f))
  return(tmp)
}))
colnames(tbl) = c("w", "v", "type")

tbl$type = factor(tbl$type, levels = c("uncorr", "wcorr", "ascorr", "scorr", "ss", "invscorr"))

g = ggplot(tbl)
g = g + geom_abline(slope = 1, color = "gray", linetype = "dashed")
g = g + geom_point(aes(x = w, y = v))
g = g + theme_bw()
g = g + labs(x = "Weight", y = "Value")
g = g + facet_grid(".~type",)
#print(g)
ggsave("figures/instances_1x6.pdf", plot = g, width = 16, height = 3.1, device = cairo_pdf)
g = g + facet_wrap(".~type", ncol = 2)
ggsave("figures/instances_3x2.pdf", plot = g, width = 5.5, height = 8, device = cairo_pdf)
g = g + facet_wrap(".~type", ncol = 3)
ggsave("figures/instances_2x3.pdf", plot = g, width = 8, height = 5.5, device = cairo_pdf)
