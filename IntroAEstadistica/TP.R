## Funciones utilizadas

armar <- function(n, tita) {
  p <- 1/6 + (2/3) * tita
  rbinom(n, size = 1, prob = p)
}

emv_corregido <- function(y) {
  est <- (3/2) * (mean(y) - 1/6)
  if (est < 0) {
    est <- 0
  } else if (est > 1) {
    est <- 1
  } 
  return(est)
}

calcula_sesgos_ECMs <- function(N_es, B, tita, pi, armar) {
  sesgos <- numeric(length(N_es))
  varianzas <- numeric(length(N_es))
  ecms <- numeric(length(N_es))
  ecm_clasico <- numeric(length(N_es))
  
  for (j in seq_along(N_es)) {
    n <- N_es[j]
    emvs <- numeric(B)
    
    for (b in 1:B) {
      muestra <- armar(n, tita)
      emvs[b] <- emv_corregido(muestra)
    }
    
    promedio_emv <- mean(emvs)
    sesgos[j] <- promedio_emv - theta
    varianzas[j] <- var(emvs)
    ecms[j] <- varianzas[j] + sesgos[j]^2
    
    q <- tita * (1 - pi)
    sesgos_clasico <- -tita * pi
    var_clasico <- q * (1 - q) / n
    ecm_clasico[j] <- var_clasico + sesgos_clasico^2
  }
  
  return(list(
    sesgos = sesgos,
    ecms = ecms,
    ecm_clasico = ecm_clasico
  ))
}

boot.metodo <- function(nivel = 0.95, B = 1000, x) {
  n <- length(x)
  alpha <- 1 - nivel
  
  emvs_boot <- numeric(B)
  
  for (b in 1:B) {
    muestra_b <- sample(x, size = n, replace = TRUE)
    emvs_boot[b] <- emv_corregido(muestra_b)
  }
  
  limites <- quantile(emvs_boot, probs = c(alpha / 2, 1 - alpha / 2))
  return(as.numeric(limites))
}

log_veros <- function(y, tita) {
  p <- 1/6 + (2/3) * tita
  sum(y * log(p) + (1 - y) * log(1 - p))
}

proporcion_rechazos <- function(B, n, tita_0, tita_verdadero, armar, log_veros, emv_corregido, alpha = 0.05) {
  rechazos <- 0
  for (b in 1:B) {
    muestra <- armar(n, tita_verdadero)
    tita_estim <- emv_corregido(muestra)
    
    ll0 <- log_veros(muestra, tita_0)
    ll1 <- log_veros(muestra, tita_estim)
    valor <- -2 * (ll0 - ll1)
    
    if (valor > qchisq(1 - alpha, df = 1)) {
      rechazos <- rechazos + 1
    }
  }
  return(rechazos / B)
}

## Parametros

set.seed(890)
tita_0 <- 1/4
N_es <- 1:1000
pi <- 1/3
B <- 1000
B_boot <- 200
nivel <- 0.95

## Informacion necesaria

resultados <- calcula_sesgos_ECMs(N_es, B, tita_0, pi, armar)

sesgos <- resultados$sesgos
ecms <- resultados$ecms
ecm_clasico <- resultados$ecm_clasico

## Ejercicio D
plot(N_es, sesgos, type = "l", col = "blue", lwd = 2,
     xlab = "Tamaño muestral (n)", ylab = "Sesgo del EMV corregido",
     main = expression(paste("Sesgo del EMV corregido cuando ", tita == 1/4)), 
     xlim = c(0, 100))
abline(h = 0, col = "red", lty = 2)

## Ejercicio E
plot(N_es, ecms, type = "l", col = "blue", lwd = 2,
     ylim = range(c(ecms, ecm_clasico)),
     xlab = "Tamaño muestral (n)", ylab = "ECM",
     main = expression(paste("ECM del EMV corregido vs clásico (", pi == 1/3, ")")),
     xlim = c(0, 300))
lines(N_es, ecm_clasico, col = "red", lwd = 2, lty = 1)
legend("topright", legend = c("EMV corregido (aleatorizado)", "Clásico con pi = 1/3"),
       col = c("blue", "red"), lty = c(1, 1), lwd = 2)

## Ejercicio G
valores_n <- which(N_es %in% c(10, 100, 1000))
tabla_ecm <- data.frame(
  n = N_es[valores_n],
  ECM_aleatorizado = round(ecms[valores_n], 6),
  ECM_clasico = round(ecm_clasico[valores_n], 6)
)
print(tabla_ecm, row.names = FALSE)

## Ejercicio H

datos <- armar(100, tita = 1/4)

IC <- boot.metodo(nivel = 0.95, B = 1000, x = datos)
cat("IC bootstrap para theta con n =", 100, ":\n")
print(round(IC, 4))

## Ejercicio I

N_es <- seq(10, 100, by = 5)
nivel_significancia <- numeric(length(N_es))

for (j in seq_along(N_es)) {
  n <- N_es[j]
  nivel_significancia[j] <- proporcion_rechazos(B, n, tita_0, tita_0, armar, log_veros, emv_corregido)
}

plot(N_es, nivel_significancia, type = "l", lwd = 2, col = "blue",
     ylim = c(0, 0.3),
     xlab = "Tamaño muestral (n)",
     ylab = "Nivel de significación empírico",
     main = "Nivel empírico vs. tamaño muestral")
abline(h = 0.05, col = "red", lty = 2)
legend("topright", legend = c("Nivel empírico", "Nivel teórico (0.05)"),
       col = c("blue", "red"), lty = c(1, 2), lwd = 2)


## Ejercicio J

valores_tita <- seq(0, 1, by = 0.02)
potencia <- numeric(length(valores_tita))

for (i in seq_along(valores_tita)) {
  tita_actual <- valores_tita[i]
  potencia[i] <- proporcion_rechazos(B, n = 100, tita_0, tita_actual, armar, log_veros, emv_corregido)
}

plot(valores_tita, potencia, type = "l", lwd = 2, col = "blue",
     xlab = expression(tita_0), ylab = "Potencia",
     main = expression(paste("Función de potencia para ", n == 100)))
abline(v = tita_0, col = "red", lty = 2)
abline(h = 0.05, col = "darkgray", lty = 2)



