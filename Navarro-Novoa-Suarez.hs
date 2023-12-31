--Navarro Solana solanan3@gmail.com 
--Novoa Shule Joaquin nojoaco2003@gmail.com
--Suarez Ines ine.suarez@hotmail.es

type Complejo = (Float, Float)  

-- Ejercicio 1.1        
re :: Complejo -> Float
re (a,b)= a            

-- Ejercicio 1.2
im :: Complejo -> Float
im (a,b) = b

-- Ejercicio 1.3
suma :: Complejo -> Complejo -> Complejo
suma (a,b) (c,d)= ((a+c),(b+d))

-- Ejercicio 1.4
producto :: Complejo -> Complejo -> Complejo
producto (a,b) (c,d) = (a*c - b*d, a*d + b*c)

-- Ejercicio 1.5
conjugado :: Complejo -> Complejo
conjugado (a,b) = (a, (-b))

-- Ejercicio 1.6
inverso :: Complejo -> Complejo
inverso (a,b) = (a/(a**2 +b**2),-b/(a**2 +b**2))

-- Ejercicio 1.7
cociente :: Complejo -> Complejo -> Complejo
cociente (a,b) (c,d) = producto (a,b) (inverso (c,d))

-- Ejercicio 1.8
potencia :: Complejo -> Integer -> Complejo
potencia (a,b) k | k == 0 = (1,0)
                 | otherwise = producto (a,b) (potencia (a,b) (k-1))

-- Ejercicio 1.9
discriminante :: Float -> Float -> Float -> Float
discriminante a b c = b**2 - (4*a*c)

raicesCuadratica :: Float -> Float -> Float -> (Complejo, Complejo)
raicesCuadratica a b c | (discriminante a b c) >= 0 = (((-b)/(2*a) + (sqrt (discriminante a b c))/(2*a), 0), ((-b)/(2*a) - (sqrt (discriminante a b c))/(2*a), 0))
                       | otherwise = (((-b)/(2*a), (sqrt (abs (discriminante a b c)))/(2*a)), ((-b)/(2*a), (-(sqrt (abs (discriminante a b c)))/(2*a))))
                                               
-- Ejercicio 2.1
modulo :: Complejo -> Float
modulo (a,b) = sqrt (a**2 + b**2)

-- Ejercicio 2.2
distancia:: Complejo -> Complejo -> Float
distancia (a,b) (c,d) = sqrt ((c-a)**2 + (d-b)**2)

-- Ejercicio 2.3
positivoa :: Complejo -> Bool
positivoa (a, b) = a >= 0

negativoa :: Complejo -> Bool
negativoa (a, b) = a < 0

positivob :: Complejo -> Bool
positivob (a, b) = b >= 0

negativob :: Complejo -> Bool
negativob (a, b) = b < 0

cuadrante :: Complejo -> Int
cuadrante (a,b) |positivoa (a,b) && positivob (a,b) = 1
                |negativoa (a,b) && positivob (a,b) = 2
                |negativoa (a,b) && negativob (a,b) = 3
                |positivoa (a,b) && negativob (a,b) = 4
   

argumento :: Complejo -> Float
argumento (a,b) |a == 0 && positivob (a,b) = pi/2
                |a == 0 && negativob (a,b) = (3*pi)/2 
                |cuadrante (a,b) == 1 = atan (b/a)
                |cuadrante (a,b) == 2 = pi + (atan (b/a))
                |cuadrante (a,b) == 3 = pi + (atan (b/a))
                |otherwise = 2*pi + (atan (b/a))
           
-- Ejercicio 2.4
pasarACartesianas :: Float -> Float -> Complejo
pasarACartesianas r tita = (r*(cos (tita)),r*(sin (tita)))

-- Ejercicio 2.5
r:: Complejo -> Float
r (a,b)= sqrt (modulo (a,b))

tita :: Complejo -> Float
tita (a,b)= (argumento (a,b))/2

raizCuadrada :: Complejo -> (Complejo,Complejo)
raizCuadrada (a,b) = ((pasarACartesianas (r (a,b)) (tita (a,b))) ,(pasarACartesianas (r (a,b)) ((tita (a,b))+pi)))
             
-- Ejercicio 2.6

resta :: Complejo -> Complejo -> Complejo
resta (a,b) (c,d) = ((a-c), (b-d))

raicesCuadraticaCompleja :: Complejo -> Complejo -> Complejo -> (Complejo,Complejo)
raicesCuadraticaCompleja (a,b) (c,d) (e,f) = (cociente (suma (-c,-d) (raiz1)) (producto2a) , cociente (suma (-c,-d) raiz2) (producto2a))
                                            where (raiz1,raiz2) = raizCuadrada (resta (potencia (c,d) (2))  (producto (producto (a,b) (e,f)) (4,0)))
                                                  producto2a = producto (a,b) (2,0)

-- Ejercicio 3.1
kesimaRaiz :: Integer -> Integer -> Complejo
kesimaRaiz k n = (cos (2*(fromInteger k)*pi/(fromInteger n)) , sin ((2*(fromInteger k)*pi)/(fromInteger n)))

raicesNEsimasDesde :: Integer -> Integer -> [Complejo]
raicesNEsimasDesde k n | k>= n = []
                       |otherwise =((kesimaRaiz k n):(raicesNEsimasDesde (k+1) n))

raicesNEsimas :: Integer -> [Complejo]
raicesNEsimas n = raicesNEsimasDesde 0 n

-- Ejercicio 3.2
sonRaicesNEsimas :: Integer -> [Complejo] -> Float -> Bool
sonRaicesNEsimas n [] e      = True
sonRaicesNEsimas n (x: xs) e | distancia (1,0) (potencia (x) n) >= e = False
                             | otherwise = sonRaicesNEsimas n (xs) e




