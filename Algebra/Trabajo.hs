funcionModulo :: Integer -> Integer
funcionModulo x | x >= 0 = x 
                | x < 0 = (-x)

maximoComunDivisor :: Integer -> Integer -> Integer
maximoComunDivisor x y | y == 0 = funcionModulo x 
                       | otherwise = maximoComunDivisor y (mod x y)

sonCoprimos :: Integer -> Integer -> Bool
sonCoprimos x y | maximoComunDivisor x y == 1 = True
                | otherwise = False

es2Pseudoprimo n = mod (2^n-1) n == 1 
                 
                 
menorDivisorDesde :: Integer -> Integer -> Integer
menorDivisorDesde n k | mod n k == 0 = k
                      | otherwise = menorDivisorDesde n (k+1) 
                      
                      
esPrimo :: Integer -> Bool 
esPrimo n | n == 1 = False
          | menorDivisorDesde n 2 == n = True
          | otherwise = False               
                   
es3Pseudoprimo :: Integer -> Bool
es3Pseudoprimo n | not(esPrimo n) && mod (3^(n-1)) n == 1 = True
                 | otherwise = False                   
 
cantidad3PseudoprimoEntre :: Integer -> Integer -> Integer                 
cantidad3PseudoprimoEntre n m | n > m = 0
                              | es3Pseudoprimo n == True = 1 + cantidad3PseudoprimoEntre (n+1) m
                              | otherwise = cantidad3PseudoprimoEntre (n+1) m          
                   
cantidad3Pseudoprimos :: Integer -> Integer
cantidad3Pseudoprimos m = cantidad3PseudoprimoEntre 1 m                  

es2y3Pseudoprimo :: Integer -> Bool
es2y3Pseudoprimo n = es2Pseudoprimo n && es3Pseudoprimo n 
                    
                                      
kesimo2y3PseudoprimoDesde :: Integer -> Integer -> Integer
kesimo2y3PseudoprimoDesde n k | n == 0 = k
                              | es2y3Pseudoprimo (k+1) = kesimo2y3PseudoprimoDesde (n-1) (k+1)
                              | otherwise = kesimo2y3PseudoprimoDesde n (k+1)

kesimo2y3Pseudoprimo :: Integer -> Integer
kesimo2y3Pseudoprimo k | k == 1 = 1105
                       | otherwise = kesimo2y3PseudoprimoDesde k 1  
                                            
esPseudoprimoGen :: Integer -> Integer -> Bool       
esPseudoprimoGen a n = not(esPrimo n) && mod (a^(n-1)) n == 1 
                       
                       
esCoprimoYPseudoprimo :: Integer -> Integer -> Bool
esCoprimoYPseudoprimo a n = sonCoprimos a n && esPseudoprimoGen a n