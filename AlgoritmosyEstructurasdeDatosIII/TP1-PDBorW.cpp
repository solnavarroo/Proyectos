// Solana Navarro
// 906/22


// El ejercicio "Black or White" lo pense con el método de Programación Dinámica.
// En primer lugar, diseñe la funcion recursiva manualmente y luego busque una forma adecuada de memorizacion.
// Me costó mucho encontrar la estrategia adecuada, pero después de MUCHOS intentos, opte por usar una matriz
// de (N + 1) x (N + 1) x (N), donde N es la longitud de la lista.

// La función recursiva que diseñé es la siguiente:
// 
// BorW(i, b, w) = 0                          si i == N
//               = min(BorW(i + 1, i, w),     // Pintar el elemento actual de negro
//                       BorW(i + 1, b, i),   // Pintar el elemento actual de blanco
//                       BorW(i + 1, b, w) + 1) // No pintar el elemento actual (sumando 1 al conteo de no pintados)

// Esta implementacion es una función de fuerza bruta, luego descubri que habia ciertas podas que podia aplicar.
// Por ejemplo, si el valor en la posición i es mayor que el último valor pintado de blanco, no es necesario realizar esa recursión.
// Lo mismo ocurre si el valor en la posición i es menor que el último valor pintado de negro.


#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;


// Funcion BorW utilizada para reaalizar lo previamente explicado, devuelve el minimo valor de numeros sin pintar.
int BorW(vector<int>& numeros, int cantidad, vector<vector<vector<int>>>& Memo, int i, int b, int w){
    if(i == cantidad){
        return(0);
    }
    if(Memo[i][b + 1][w + 1] == -1){
        
        int opcion1 = 1 + BorW(numeros, cantidad, Memo, i+1, b, w);
        
        if(numeros[i] > numeros[b] or b == -1){
            int opcion2 = BorW(numeros, cantidad, Memo, i+1, i, w);
            if(opcion1 > opcion2){
                opcion1 = opcion2;
            }
        }
        if(numeros[i] < numeros[w] or w == -1){
            int opcion3 = BorW(numeros, cantidad, Memo, i+1, b, i);
            if(opcion1 > opcion3){
                opcion1 = opcion3;
            }
        }
        
        Memo[i][b + 1][w + 1] = opcion1;
    }
    return(Memo[i][b + 1][w + 1]);
}


//Input

int main()
{
    bool haySiguiente = true;
    vector<int> res;
    
    while(haySiguiente){
        
        int cantidad;
        cin >> cantidad;
        
        if (cantidad == -1) {
            break;
        }
        
        vector<int> numeros(cantidad);
        for (int i = 0; i < cantidad; i++) {
            cin >> numeros[i];
        }
        
        int N = numeros.size();
        
        vector<vector<vector<int>>> Memo(N + 1, vector<vector<int>>(N + 1, vector<int>(N, -1)));
        
        
        res.push_back(BorW(numeros, N, Memo, 0, -1, -1));
        
    }
    
    for (int k = 0; k < res.size(); k++) {
        cout << res[k] << endl;
    }

    return 0;
}