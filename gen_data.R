# bu-sam-03 Pilot Data Generator (seed 603)                                     
# Replicates the seeded RNG from app/shared/utils/bu-sam/statistics.js        

# LCG seeded RNG (matches JS implementation)                                    
make_rng <- function(seed) {                                                    
  state <- seed                                                                 
  function() {                                                                
    state <<- (state * 1664525 + 1013904223) %% 4294967296
    state / 4294967296                                                          
  }
}                                                                               

# Box-Muller transform                                                          
normal_random <- function(mean, sd, rng) {
  u1 <- rng()                                                                   
  u2 <- rng()                                                                 
  z0 <- sqrt(-2 * log(u1)) * cos(2 * pi * u2)
  mean + sd * z0                                                                
}

# Generate pilot data                                                         
generate_pilot_data <- function() {
  rng <- make_rng(603)
  data <- data.frame(biomarker = numeric(), lifespan =
                       numeric())                                                                      
  
  for (i in 0:19) {                                                             
    repeat {                                                                  
      biomarker <- normal_random(50, 20, rng)                                   
      if (biomarker >= 0 & biomarker <= 100) break
    }                                                                           
    noise <- normal_random(0, 8, rng)                                         
    lifespan <- 65 + biomarker * 0.12 + noise                                   
    
    data <- rbind(data, data.frame(                                             
      biomarker = biomarker,
      lifespan = lifespan                                     
    ))
  }                                                                             
  
  data[order(data$biomarker), ]
}

pilot <- generate_pilot_data()
print(pilot)
write.csv(pilot, "pilot.csv", row.names = FALSE)
