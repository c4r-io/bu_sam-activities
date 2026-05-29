lmp <- function (modelobject) {
  if (class(modelobject) != "lm") stop("Not an object of class 'lm' ")
  f <- summary(modelobject)$fstatistic
  p <- pf(f[1],f[2],f[3],lower.tail=F)
  attributes(p) <- NULL
  return(p)
}

orig <- read.csv("sample_size.csv", header = FALSE)
names(orig) <- c("Biomarker", "Lifespan")
df <- orig[1:99,]

p_val_from_cor <- function(df)
{
  r <- cor(df$Biomarker, df$Lifespan)
  t <- r * sqrt(NROW(df)-2)/sqrt(1-r^2)
  p <- 2*(1 - pt(t, NROW(df)-2))
  return(p)
}

p_val_from_lm <- function(df)
{
  fit <- lm(Lifespan ~ Biomarker, df)
  lmp(fit)
}

write.csv(orig[1:100,], "pilot_n-100.csv", row.names = FALSE, quote = FALSE)

xx <- read.csv("pilot_n-100.csv")
p_val_from_cor(xx)
p_val_from_lm(xx)

plot(df, Lifespan ~ Biomarker)

n <- 800
K <- 1000

set.seed(42)

p_vals <- numeric(K)

for(i in seq_len(K))
{
  idx <- sample(seq_len(NROW(df)), n, replace = TRUE)
  resample <- df[idx,]
  fit <- lm(Lifespan ~ Biomarker, resample)
  p_vals[i] <- lmp(fit)
}

power <- sum(p_vals < 0.05) / K
