best_d %>%
  ggplot(aes(x = Biomarker, y = Lifespan)) + 
  geom_point(size = 3, alpha = 0.8, color = color_purple) + 
  geom_smooth(method = "lm") + 
  theme_c4r(plot_dpi = 144) + 
  scale_x_continuous(limits = c(-2.5, 2.5)) +
  coord_cartesian(xlim = c(-2.5, 2.5), ylim = c(55, 95))
