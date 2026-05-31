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
color_green <- "#0CC800"
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
      plot.title = element_text(
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

# set up data for neuron firing rates
n = 30
mean_A <- 50
sd_A <- 7

mean_B <- 54
sd_B <- 7

set.seed(42)

dat_A <- data.frame(value = rnorm(n, mean_A, sd_A))
dat_B <- data.frame(value = rnorm(n, mean_B, sd_B))

## make plots ----
make_neuron_panel <- function(df, dpi = view_dpi, 
                              dot_color = color_purple, 
                              title_text = "Group A")
{
  mean_val <- mean(df$value)
  out <- df %>%
    ggplot(aes(x = value)) +
    geom_dotplot(binwidth = 1.5, method = "histodot", 
                 dotsize = 0.8, fill = dot_color) + 
    geom_vline(xintercept = mean_val, linewidth = 1.5) + 
    annotate("text",
             x = mean_val,
             y = 0.95,
             label = sprintf("Mean = %.1f Hz", mean_val),
             family = "JetBrains Mono",
             hjust = -0.1, 
             size = 14 * dpi / 96 / .pt, 
             color = color_dk_grey) + 
    theme_c4r(plot_dpi = dpi) + 
    coord_cartesian(xlim = c(25, 75)) + 
    ggtitle(title_text) + 
    xlab("Firing Rate (Hz)") + 
    theme(axis.text.y = element_blank(),
          axis.ticks.y = element_blank())
  
  out
}

neuron_A <- make_neuron_panel(dat_A, dpi = plot_dpi, 
                              dot_color = color_blue)
plot_width <- 5 # inches
plot_height <- 2.2 # inches

ggsave(
  "plot_neuron_A.png",
  neuron_A, 
  width = plot_width,
  height = plot_height,
  units = "in",
  dpi = plot_dpi
)


neuron_B <- make_neuron_panel(dat_B, dpi = plot_dpi, 
                              dot_color = color_green, 
                              title_text = "Group B")
plot_width <- 5 # inches
plot_height <- 2.2 # inches

ggsave(
  "plot_neuron_B.png",
  neuron_B, 
  width = plot_width,
  height = plot_height,
  units = "in",
  dpi = plot_dpi
)
