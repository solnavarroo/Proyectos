// Solana Navarro
// 906/22

// Idea: Me di cuenta de que podia usar el algoritmo de Dantzig y aprovechar su invariante a mi favor.
// El invariante del algoritmo establece que, en la k-esima iteracion, se consideran todos los caminos intermedios
// que incluyen unicamente los nodos añadidos hasta el momento. Por lo tanto, decidi preparar la matriz de distancias
// en el orden en el que Tomas quiere estudiar la conectividad. Luego, en cada iteracion de Dantzig, calculo la suma
// de todas las distancias entre los pares de nodos presentes hasta ese momento.
// De esta forma, voy añadiendo vertices al grafo siguiendo el orden inverso al que se eliminaran (es decir,
// reconstruyendo el grafo de atrás hacia adelante) y evaluando como evoluciona la conectividad de la ciudad.

// Imports
#include <iostream>
#include <vector>
#include <climits>
#include <numeric>
#include <limits>
#include <algorithm>

using namespace std;


// Funcion Dantzig donde se genera la respuesta
vector<long long> dantzig(vector<vector<int>> matriz) {
    int n = matriz.size();
    vector<long long> res;
    
    for (int k = 0; k < n - 1; ++k) {
        
        for (int i = 0; i <= k; ++i) {
            int res1 = numeric_limits<int>::max();
            int res2 = numeric_limits<int>::max();
            for (int j = 0; j <= k; ++j) {
                res1 = min(res1, matriz[i][j] + matriz[j][k + 1]);
                res2 = min(res2, matriz[k + 1][j] + matriz[j][i]);
            }
            matriz[i][k + 1] = res1;
            matriz[k + 1][i] = res2;
        }

        for (int i = 0; i <= k; ++i) {
            for (int j = 0; j <= k; ++j) {
                matriz[i][j] = min(matriz[i][j], matriz[i][k + 1] + matriz[k + 1][j]);
            }
        }
        
        long long suma = 0;
        // Suma de lo que hay hasta el momento
        for (int i = 0; i <= k + 1; ++i) {
            for (int j = 0; j <= k + 1; ++j) {
                if (matriz[i][j] != numeric_limits<int>::max()) {
                    suma += matriz[i][j];
                }
            }
        }
        res.push_back(suma);
        
    }
    

    return res;
}

// Ordeno matriz en el orden que Tomas quiere
vector<vector<int>> ordenarmatriz(vector<vector<int>> matriz, vector<int> orden){
    int n = matriz.size();
    vector<vector<int>> res(n, vector<int>(n));

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            res[i][j] = matriz[orden[i]][orden[j]];
        }
    }
    return res;
}

// Input y devolver respuesta
int main() {
    int n;
    cin >> n;
    vector<vector<int>> matriz;
    for (int i = 0; i < n; ++i) {
        vector<int> iesimo(n);
        for (int j = 0; j < n; ++j) {
            cin >> iesimo[j];
        }
        matriz.push_back(iesimo);
    }

    vector<int> orden(n);
    for (int i = 0; i < n; ++i) {
        int x;
        cin >> x;
        orden[i] = x - 1;
    }

    reverse(orden.begin(), orden.end());
    
    
    vector<vector<int>> matrizordenada = ordenarmatriz(matriz, orden);
    vector<long long> caminosmin = dantzig(matrizordenada);
    
    reverse(caminosmin.begin(), caminosmin.end());
    
    caminosmin.push_back(0);

    for (int i = 0; i < caminosmin.size(); ++i) {
        cout << caminosmin[i];
        cout << " ";
    }
    cout << endl;

    return 0;
}