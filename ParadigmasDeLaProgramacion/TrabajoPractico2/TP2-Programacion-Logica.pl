% Melli, Tomás Felipe, 371/22, tomas.melli1@gmail.com
% Lourdes Wittmund Montero, 1103/22, lourdesmonterochiara@gmail.com
% Marco Romano Fina, 1712/21, marcoromanofinaa@gmail.com
% Solana Navarro, 906/22, solanan3@gmail.com

% Modulos
:- use_module(piezas).
:- use_module(library(lists)).

% Ejercicio 1
% sublista(+Descartar, +Tomar, +L, -R)
sublista(D,T,L,R) :- append(A,B,L), length(A,D), append(R,_,B), length(R,T).


% Ejercicio 2
% tablero(+K, -T)
longitud_k_lista(K,L) :- length(L,K).
tablero(K,T) :- length(T,5), maplist(longitud_k_lista(K),T).


% Ejercicio 3
%tamaño(+M, -F, -C)
tamano(M,F,C) :- length(M,F), maplist(longitud_k_lista(C),M).


% Ejercicio 4
% coordenadas(+T, -IJ)
coordenadas(T,(I,J)) :- tamano(T,A,B), between(1,A,I), between(1,B,J).


% Ejercicio 5
% kPiezas(+K, -PS)
kPiezas(K,PS) :- nombrePiezas(L),generar_klistas(K,L,PS).

generar_klistas(0,[],[]).
generar_klistas(K,[X|XS],[X|LS]) :- K > 0, P is K - 1, length(XS,W), W >= P, generar_klistas(P,XS,LS).
generar_klistas(K,[_|XS],L) :- length(XS,W), W >= K, generar_klistas(K,XS,L).


% Ejercicio 6
% seccionTablero(+T,+ALTO, +ANCHO, +coordenada(I,J), ?ST)
seccionTablero(T,ALTO,ANCHO,(I,J),ST) :- K is (I-1), sublista(K,ALTO,T,R), Q is (J-1), maplist(sublista(Q,ANCHO),R,ST).


% Ejercicio 7
% ubicarPieza(+Tablero, +Identificador)
ubicarPieza(T,I) :- pieza(I,E), tamano(E,F,C), coordenadas(T,IJ), seccionTablero(T,F,C,IJ,E).


% Ejercicio 8
% ubicarPiezas(+Tablero, +Poda, +Identificadores)
ubicarPiezas(T, P, I) :- maplist(ubicar_con_poda(P, T), I).

ubicar_con_poda(P,T,I) :- ubicarPieza(T,I), poda(P,T).


% Ejercicio 9
% llenarTablero(+Poda, +Columnas, -Tablero)
llenarTablero(P,C,T) :- tablero(C,T), kPiezas(C,PS), ubicarPiezas(T,P,PS).


% Ejercicio 10
poda(sinPoda, _).
poda(podaMod5, T) :- todosGruposLibresModulo5(T).


cantSoluciones(Poda, Columnas, N) :- findall(T, llenarTablero(Poda, Columnas, T), TS), length(TS, N).


% Obtuvimos lo siguientes resultados:
% 1 ?- tiempos(sinPoda, N).
% 37,958,869 inferences, 1.922 CPU in 1.928 seconds (100% CPU, 19750001 Lips)
%N = 28 ;
% 1,485,726,353 inferences, 77.268 CPU in 77.476 seconds (100% CPU, 19228252 Lips)
%N = 200.

% Ejercicio 11

grupoMod5(T) :- length(T,M), 0 is M mod 5.

libre(T,(I,J)) :- nth1(I, T, K), nth1(J, K, M),var(M).   

todosGruposLibresModulo5(T) :- findall((I,J), libre(T,(I,J)), K), agrupar(K, R), maplist(grupoMod5, R).
        

% Obtuvimos lo siguientes resultados con podaMod5:
% 1 ?- tiempos(podaMod5, N).
% 16,181,606 inferences, 0.901 CPU in 0.934 seconds (96% CPU, 17959089 Lips)
%N = 28 ;
% 329,335,525 inferences, 18.441 CPU in 19.551 seconds (94% CPU, 17858846 Lips)
%N = 200.


% Ejercicio 12: Reversibilidad del predicado sublista/4
%
% Analizamos si el predicado funciona correctamente cuando se lo llama con el primer parámetro
% sin instanciar y los otros tres instanciados: sublista(-D, +T, +L, +R).
%
% Lo que queremos ver es si se pueden generar correctamente todos los valores posibles de D
% tales que, descartando D elementos de L, se obtenga una sublista R de longitud T.
%
% Para eso analizamos cómo se comporta el predicado para distintos casos:

% CASO 1: Esperamos cero soluciones
% En este caso, no debería haber forma de obtener R de L tomando T elementos, por lo tanto debe fallar.
% Ejemplo:
% ?- sublista(D, 5, [1,2,3,4], [1,2,3,4]).
% false.
% En el ejemplo, no es posible tomar 5 elementos de una lista de solo 4.

% CASO 2: Esperamos una única solución
% Ejemplo:
% ?- sublista(D, 4, [1,2,3,4], [1,2,3,4]).
% D = 0.
% La única respuesta valida se forma de obtener la sublista R es sin descartar elementos, es decir D=0.

% CASO 3: Esperamos multiples soluciones
% Ejemplo:
% ?- sublista(D, 2, [1,2,3,1,2], [1,2]).
% D = 0 ;
% D = 3 ;
% false.
% Ahora tenemos dos formas distintas de obtener la sublista [1,2] de longitud 2,
% desde la posición 0 o desde la 3.

% ANÁLISIS:
%
% Ahora queremos ver el comportamiento del predicado cuando se lo llama como sublista(-D, +T, +L, +R).
%
% En primer lugar analicemos la reversibilidad de append/3 y length/2:
% - append/3 es completamente reversible, ya que puede usarse para generar partes, unir listas o encontrar prefijos/sufijos.
% - length/2 también es reversible cuando uno de los argumentos está instanciado.
%
% En sublista, el orden de los predicados está cuidadosamente elegido para evitar caminos infinitos:
%
% - Se parte la lista L con append(A, B, L). En este punto, A y B son desconocidos, y se generan
% todas las posibles formas de partir L en un prefijo A y un sufijo B.
%
% - Luego, length(A, D) restringe el tamaño de A. Este orden es clave, ya que si pusiéramos length(A, D) antes que append(A, B, L),
% y A no estuviera instanciada, podríamos caer en caminos infinitos, ya que Prolog intentaría generar listas arbitrarias para A
% sin saber si se ajustan a L. En cambio, con este orden, append/3 produce candidatos A y B consistentes con L, y luego
% length(A, D) simplemente calcula su longitud.
%
% - Después, volvemos a partir B con append(R, _, B), lo que intenta encontrar un prefijo R dentro de B.
% Como T está instanciado, length(R, T) restringe qué sublistas se consideran. Con este paso garantizamos que se consideren todas
% las sublistas de longitud T dentro de L, y en conjunto con el paso anterior, cada valor posible de D tal que R aparece en L
% como una sublista de longitud T luego de descartar D elementos.
%
% Entonces vimos que:
% - El predicado explora todas las combinaciones válidas de (A,B) tales que L = A ++ B,
%  y dentro de cada B, todas las sublistas R posibles de longitud T.
% - No se generan soluciones repetidas, cada valor de D corresponde a una unica ubicación de R dentro de L.
% - No se generan soluciones incorrectas, R siempre es sublista de L, y D cuenta con precisión los elementos descartados.
% - El orden de las cláusulas evita caminos infinitos, cada uso de append/3 y length/2 se realiza sobre listas acotadas.
%
% Por lo tanto, el comportamiento del predicado en este modo es:
% - Declarativo ya que no depende de la dirección de ejecución.
% - Completo ya que encuentra todos los D posibles para los que R aparece como sublista de T elementos dentro de L.
% - Correcto ya que todas las soluciones satisfacen la definición de sublista esperada.
% - Eficiente ya que evita caminos infinitos al ordenar correctamente las llamadas a append/3 y length/2.
%
% Concluimos que el predicado sublista/4 es reversible en el modo (-D, +T, +L, +R),
% y puede usarse para encontrar todas las posiciones posibles de una sublista R dentro de L.