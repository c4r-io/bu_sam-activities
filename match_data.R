# read in both datasets
pilot <- read.csv("pilot.csv")
orig <- read.csv("sample_size.csv")

# target correlation to match previous activity example data
target_rho <- cor(pilot$biomarker, pilot$lifespan)

# target correlation for bu-sam-01 activity
target_rho <- 0.1

idx <- seq_len(NROW(orig))

best_r <- 1

set.seed(42)
num_runs <- 10000
for(i in 1:num_runs)
{
  d <- orig[sample(idx, 20),]
  r <- cor(d[,1], d[,2])
  if(abs(r - target_rho) < abs(best_r - target_rho))
  {
    best_d <- d
    best_r <- r
  }
}
# write.csv(best_d, "new_pilot.csv", row.names = FALSE)

## define plotting styles ----
library(tidyverse)
library(ggpattern)
library(showtext)

view_dpi <- 144
plot_dpi <- 300
options(rstudio.plots.dpi = plot_dpi)
font_add_google("JetBrains Mono", "JetBrains Mono")
showtext_auto()

color_purple <- "#6F00FF"
color_blue <- "#008FFF"
color_dk_grey <- "#333132"
color_int_lt_grey <- "#A2A2A2"
color_int_dk_grey <- "#E0E0E0"
color_lt_grey <- "#F3F3F3"

theme_c4r <- function(
    fontsize = 14,
    plot_dpi = 300,
    solid_axis = FALSE,
    legend.fontsize = 10
) {
  theme_grey() +
    theme(
      # Panel
      panel.background = element_rect(fill = "white", colour = NA),
      panel.border = element_blank(),
      panel.grid = element_line(color = color_int_dk_grey),
      panel.grid.minor = element_blank(),
      
      # axes
      axis.line = element_line(
        color = color_dk_grey,
        linewidth = ifelse(solid_axis, 0.5, 0)
      ),
      axis.ticks = element_blank(),
      axis.text = element_text(
        family = "JetBrains Mono",
        size = fontsize * plot_dpi / 96
      ),
      axis.title = element_text(
        family = "JetBrains Mono",
        size = fontsize * plot_dpi / 96
      ),
      
      # Strip (facets)
      strip.background = element_rect(
        fill = color_int_lt_grey,
        colour = "grey20"
      ),
      
      # Legend
      legend.key = element_rect(fill = "white", colour = NA),
      legend.text = element_text(
        family = "JetBrains Mono",
        size = legend.fontsize * plot_dpi / 96
      ),
      legend.title = element_text(
        family = "JetBrains Mono",
        size = legend.fontsize * plot_dpi / 96
      ),
      
      # Complete theme
      complete = TRUE
    )
}

c4r_geom_textsize <- function(fontsize = 14, plot_dpi = 300) {
  (fontsize * plot_dpi / 96) / 2.835
}

## make plots ----
names(best_d) <- c("Biomarker", "Lifespan")

make_lifespan_biomarker_panel <- function(df, dpi = view_dpi, 
                                          include_regression = FALSE)
{
  out <- df %>%
    ggplot(aes(x = Biomarker, y = Lifespan)) + 
    geom_point(size = 3, alpha = 0.8, color = color_purple) + 
    theme_c4r(plot_dpi = dpi) + 
    scale_x_continuous(limits = c(-2.5, 2.5)) +
    coord_cartesian(xlim = c(-2.5, 2.5), ylim = c(55, 95))
  
  if (include_regression)
  {
    out <- out + geom_smooth(method = "lm", color = "black", se = FALSE, 
                             fullrange = TRUE)
  }
  out
}

make_lifespan_biomarker_panel(best_d)
p <- make_lifespan_biomarker_panel(best_d, dpi = plot_dpi)
plot_width <- 5 # inches
plot_height <- 4 # inches

ggsave(
  "plot_lifespan_biomarker_n-20_r-0.1.png",
  p,
  width = plot_width,
  height = plot_height,
  units = "in",
  dpi = plot_dpi
)

p <- make_lifespan_biomarker_panel(best_d, dpi = plot_dpi, include_regression = TRUE)
plot_width <- 5 # inches
plot_height <- 4 # inches

ggsave(
  "plot_lifespan_biomarker_n-20_r-0.1_line.png",
  p,
  width = plot_width,
  height = plot_height,
  units = "in",
  dpi = plot_dpi
)

df_100 <- orig[1:100,]
names(df_100) <- c("Biomarker", "Lifespan")
make_lifespan_biomarker_panel(df_100)

p <- make_lifespan_biomarker_panel(df_100, dpi = plot_dpi)
plot_width <- 5 # inches
plot_height <- 4 # inches

ggsave(
  "plot_lifespan_biomarker_n-100.png",
  p,
  width = plot_width,
  height = plot_height,
  units = "in",
  dpi = plot_dpi
)
