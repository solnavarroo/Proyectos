-- Completar con los datos del grupo
--
-- Nombre de Grupo: xx
-- Integrante 1: Nombre Apellido, email, LU
-- Integrante 2: Nombre Apellido, email, LU
-- Integrante 3: Nombre Apellido, email, LU
-- Integrante 4: Nombre Apellido, email, LU


type Usuario = (Integer, String) -- (id, nombre)
type Relacion = (Usuario, Usuario) -- usuarios que se relacionan
type Publicacion = (Usuario, String, [Usuario]) -- (usuario que publica, texto publicacion, likes)
type RedSocial = ([Usuario], [Relacion], [Publicacion])

-- Funciones basicas

usuarios :: RedSocial -> [Usuario]
usuarios (us, _, _) = us

relaciones :: RedSocial -> [Relacion]
relaciones (_, rs, _) = rs

publicaciones :: RedSocial -> [Publicacion]
publicaciones (_, _, ps) = ps

idDeUsuario :: Usuario -> Integer
idDeUsuario (id, _) = id

nombreDeUsuario :: Usuario -> String
nombreDeUsuario (_, nombre) = nombre

usuarioDePublicacion :: Publicacion -> Usuario
usuarioDePublicacion (u, _, _) = u

likesDePublicacion :: Publicacion -> [Usuario]
likesDePublicacion (_, _, us) = us

-- Predicados auxiliares
-- Decidimos generar las funciones pertenece, eliminarRepetidos y mismosElementos de una forma general, asi lo podiamos utilizar cuando los necesitabamos.

pertenece :: (Eq t) => t -> [t] -> Bool
pertenece t [] = False
pertenece t (h:hs) | t == h = True
                   | otherwise = pertenece t hs

eliminarRepetidos :: (Eq t) => [t] -> [t]
eliminarRepetidos [] = []
eliminarRepetidos (h:hs) | pertenece h hs == False = h : eliminarRepetidos hs
                         | otherwise = eliminarRepetidos hs

mismosElementos :: (Eq t) => [t] -> [t] -> Bool
mismosElementos [] (x:xs) = False
mismosElementos (h:hs) [] = False
mismosElementos (h:hs) (x:xs) | pertenece h (x:xs) = True
                              | otherwise = mismosElementos hs (x:xs)


-- Ejercicio 1
-- En primer lugar generamos una funcion donde elimina los usuarios repetidos y una que forma una lista con los nombres de los usuarios. 
-- En proyectarNombres juntamos ambas funciones (listaDeNombres y listaDeUsuarios) y nos hace una lista de nombres sin repetir. 
-- Por ultimo, en nombresDeUsuarios, le pedimos que utilice la funcion proyectarNombres para hacer una lista con todos los usuarios de esa RedSocial.
                       
listaDeUsuarios :: [Usuario] -> [Usuario]
listaDeUsuarios (u:us) =  eliminarRepetidos(u:us)

listaDeNombres :: [Usuario] -> [String]
listaDeNombres [] = []
listaDeNombres (u:us) = nombreDeUsuario u : listaDeNombres us

proyectarNombres :: [Usuario] -> [String]
proyectarNombres [] = []
proyectarNombres (u:us) = listaDeNombres (listaDeUsuarios (u:us))

nombresDeUsuarios :: RedSocial -> [String]
nombresDeUsuarios red = proyectarNombres (usuarios(red))


-- Ejercicio 2
-- Generamos dos funciones que toman una relación, donde una devuelve el primer usuario y la otra el segundo usuario de esa relación. 
-- En estaIncluido determina si un usuario está incluido en una relación. Devuelve un valor entero dependiendo en qué posición se encuentre el usuario. 
-- La función amigos toma un usuario y una lista de relaciones. Recorre la lista de relaciones y, para cada relación, verifica si el usuario está incluido en ella. Si está incluido y es el primer usuario, agrega el segundo usuario a una lista de amigos. Si está incluido y es el segundo usuario, agrega el primer usuario a la lista de amigos. Esto devuelve la lista de amigos encontrados. 
-- Por último, amigosDe, utiliza la función amigos para encontrar los amigos del usuario en la lista de relaciones de la red social.

relacion1 :: Relacion-> Usuario
relacion1 (us1,_) = us1

relacion2 :: Relacion-> Usuario
relacion2 (_, us2) = us2

estaIncluido :: Usuario-> Relacion -> Int
estaIncluido u r | u == relacion1(r)= 1
                 | u == relacion2(r)= 2
                 | otherwise= 0

amigos :: Usuario-> [Relacion]->[Usuario]
amigos u [] = []
amigos u (r:rs) | estaIncluido u r == 1 = relacion2(r) : amigos u rs
                | estaIncluido u r == 2 = relacion1(r) : amigos u rs
                | otherwise = amigos u rs

amigosDe :: RedSocial -> Usuario -> [Usuario]
amigosDe red u = amigos u (relaciones red)


-- Ejercicio 3
-- Generamos longdeLista que toma una lista de usuarios y devuelve la longitud de esa lista. Si la lista está vacía, devuelve 0. Pero si la lista tiene al menos un elemento, suma 1 y hace recursion con el resto de la lista. 
-- En cantidadDeAmigos, utilizamos la función amigosDe para obtener la lista de amigos del usuario y luego llamamos a longdeLista para que se fije cuantos amigos tiene.

longdeLista :: [Usuario] -> Integer
longdeLista [] = 0
longdeLista (u:us) = 1 + longdeLista us

cantidadDeAmigos :: RedSocial -> Usuario -> Integer
cantidadDeAmigos red u = longdeLista (amigosDe red u)

--Ejercicio 4
-- La funcion mayorNumero compara la cantidad de amigos del primer usuario (u1) con la cantidad de amigos del siguiente usuario (u2). Si la cantidad de amigos de u1 es mayor que la de u2, se llama recursivamente a mayorNumero con u1 y el resto de la lista de usuarios (us). Si la cantidad de amigos de u1 es menor a la de u2, hace recursión con u2 y el resto de la lista de usuarios (us). El proceso continúa hasta que solo quede un usuario en la lista, y ese usuario sera el que tiene mayor número de amigos. 
-- usuarioConMasAmigos busca al usuario con el mayor número de amigos entre todos los usuarios de la red social.

mayorNumero ::  RedSocial-> [Usuario]-> Usuario
mayorNumero red (u1:[])= u1
mayorNumero red (u1:u2:us)|cantidadDeAmigos red u1 > cantidadDeAmigos red u2 = mayorNumero red  (u1:us)
                          |otherwise = mayorNumero red (u2:us)

                       
usuarioConMasAmigos :: RedSocial -> Usuario
usuarioConMasAmigos red = mayorNumero red (usuarios(red))                  

--Ejercicio 5
-- describir qué hace la función: .....

mayorA10 :: RedSocial-> [Usuario]-> Bool
mayorA10 red [] = False
mayorA10 red (u:us) |cantidadDeAmigos red u > 10 = True
                    |otherwise = mayorA10 red us

estaRobertoCarlos :: RedSocial -> Bool
estaRobertoCarlos red = mayorA10 red (usuarios(red))

--Ejercicio 6
-- textoPublicado toma una publicación y devuelve el texto de esa publicación. 
-- publicacionesUsuario recorre la lista de publicaciones y compara el usuario de cada publicación con el usuario dado. Si la publicación es del usuario, agrega esa publicación a una lista y hace recursión con el resto de la lista de publicaciones. Si no es del usuario, continúa con la siguiente publicación. La función devuelve la lista de publicaciones del usuario encontradas. 
-- publicacionesDe llama a publicacionesUsuario con la lista de publicaciones de una red social y el usuario dado. Además, aplicamos la función eliminarRepetidos para eliminar posibles duplicados en la lista de publicaciones. 

textoPublicado :: Publicacion -> String
textoPublicado (_,txt,_) = txt
                               
publicacionesUsuario :: [Publicacion]-> Usuario -> [Publicacion]
publicacionesUsuario [] u = []
publicacionesUsuario (p:ps) u | usuarioDePublicacion p == u = p : publicacionesUsuario ps u    
                              | otherwise = publicacionesUsuario ps u                

publicacionesDe :: RedSocial -> Usuario -> [Publicacion]
publicacionesDe red u = publicacionesUsuario (eliminarRepetidos(publicaciones(red))) u

--Ejercicio 7
-- En listaDePublicaciones recorre la lista de publicaciones y verifica si el usuario pertenece a la lista de usuarios que les dieron me gusta a la publicación. Si el usuario pertenece, agrega la publicación a una lista de publicaciones y luego hace recursion con el resto de la lista de publicaciones y el mismo usuario. Si el usuario no pertenece, continúa con la siguiente publicación. 
-- Para publicacionesQueLeGustanA utilizamos la función listaDePublicaciones con un usuario y la lista de publicaciones de la red social. Además, aplicamos la función eliminarRepetidos para eliminar duplicados de la lista de publicaciones.

listaDePublicaciones :: Usuario -> [Publicacion]-> [Publicacion]
listaDePublicaciones u [] = []
listaDePublicaciones u (p:ps) | pertenece u (likesDePublicacion p) == True = p : listaDePublicaciones u ps
                              | otherwise = listaDePublicaciones u ps
                           
                             
publicacionesQueLeGustanA :: RedSocial -> Usuario -> [Publicacion]
publicacionesQueLeGustanA red u = eliminarRepetidos(listaDePublicaciones u (publicaciones(red)))

--Ejercicio 8
-- La función lesGustanLasMismasPublicaciones compara si las listas de publicaciones que les gustan a u1 y u2 son iguales utilizando la función mismosElementos. Si las listas de publicaciones son iguales, la función devuelve True. Si las listas de publicaciones son diferentes, devuelve False.

lesGustanLasMismasPublicaciones :: RedSocial -> Usuario -> Usuario -> Bool
lesGustanLasMismasPublicaciones red u1 u2 = mismosElementos (publicacionesQueLeGustanA red u1) (publicacionesQueLeGustanA red u2)

--Ejercicio 9
-- leGustaA verifica si el usuario le dio me gusta a esa publicación. Si el usuario pertenece, devuelve True. Sino, devuelve False.
-- leGustanTodas toma una lista de publicaciones y un usuario. Comprueba si el usuario le ha dado me gusta a todas las publicaciones de la lista. Utilizamos la recursión para verificar cada publicación. Si encuentra una publicación que no le haya dado me gusta, devuelve False.
-- existeLeGustanTodas toma una lista de publicaciones y una lista de usuarios. Comprueba si hay al menos un usuario de la lista de usuarios a los que les gusten todas las publicaciones de la lista de publicaciones. Utiliza la recursión para verificar cada usuario. Si al menos un usuario le gusta todas las publicaciones, devuelve True. Si no se encuentra ningún usuario que le gusten todas las publicaciones, devuelve False.
-- tieneUnSeguidorFiel llama a existeLeGustanTodas utilizando la lista de publicaciones del usuario en la red social y la lista de usuarios de la red social. Esto se hace para verificar si existe al menos un usuario que le gusten todas las publicaciones del usuario dado en la red social.

leGustaA :: Publicacion -> Usuario-> Bool
leGustaA pub u = pertenece u (likesDePublicacion pub)

leGustanTodas :: [Publicacion] -> Usuario -> Bool
leGustanTodas [] u = True
leGustanTodas (p:ps) u | leGustaA p u == True = leGustanTodas ps u
                       | otherwise = False


existeLeGustanTodas :: [Publicacion] -> [Usuario] -> Bool
existeLeGustanTodas (p:ps) [] = False
existeLeGustanTodas [] (u:us) = False
existeLeGustanTodas (p:ps) (u:us) | leGustanTodas (p:ps) u == True = True  
                                  | otherwise = existeLeGustanTodas (p:ps) us              


tieneUnSeguidorFiel :: RedSocial -> Usuario -> Bool
tieneUnSeguidorFiel red u = existeLeGustanTodas (publicacionesDe red u) (usuarios(red))


--Ejercicio 10

cadenaDeAmigos :: RedSocial -> Usuario -> [Usuario] -> [Usuario] -> Bool
cadenaDeAmigos red u2 [] (x:xs) = False
cadenaDeAmigos red u2 (u:us) (x:xs) | pertenece u (x:xs) == True = cadenaDeAmigos red u2 us (x:xs)
                                    | u == u2 = True 
                                    | otherwise = cadenaDeAmigos red u2 (amigosDe red u ++ us) ((x:xs) ++ [u])

existeSecuenciaDeAmigos :: RedSocial -> Usuario -> Usuario -> Bool
existeSecuenciaDeAmigos red u1 u2 = cadenaDeAmigos red u2 (amigosDe red u1) [u1]