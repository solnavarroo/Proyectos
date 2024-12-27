// Solana Navarro
// 906/22

// Idea: Utilice el algoritmo de Dijkstra para calcular los caminos minimos
// desde el nodo 0 a todos los demas nodos y desde el nodo n−1 (ultimo nodo) a todos los demas. 
// Con estos resultados, identifique las aristas St-eficientes, que son aquellas aristas que, al sumarse,
// forman parte de un camino minimo entre el nodo 0 y el nodo n−1. 
// Posteriormente, se multiplican los costos de estas aristas por 2 y se suman para obtener el resultado final, 
// representando el doble del costo total de todas las aristas St-eficientes.


// Imports
#include <iostream>
#include <vector>
#include <algorithm>
#include <tuple>
#include <sstream>
#include <stdexcept>
#include <limits>
#include <unordered_map>
#include <queue>

using namespace std;


// Algoritmo Dijkstra 
unordered_map<int, int> Dijkstra(vector<vector<tuple<int, int>>> listadeady, int inicio){
    vector<int> S;
    unordered_map<int, int> pi;
    priority_queue<tuple<int, int>, vector<tuple<int, int>>, greater<tuple<int, int>>> cola;
    S.push_back(inicio);
    
    for (int i = 0; i < listadeady.size(); i ++){
        pi[i] = numeric_limits<int>::max();
    }
    pi[inicio] = 0;
    
    for (int i = 0; i < listadeady[inicio].size(); i ++){
        int v = get<0>(listadeady[inicio][i]);
        int c = get<1>(listadeady[inicio][i]);
        if (pi[v] == numeric_limits<int>::max()){
            pi[v] = c;
        }else{
            pi[v] = min(pi[v], c);
        }
    }
    unordered_map<int, bool> faltanporvisitar;
    for (int i = 0; i < listadeady.size(); ++i) {
        if(i != inicio){
            faltanporvisitar[i]= false; 
            if (pi[i] != numeric_limits<int>::max()){
                cola.push({pi[i], i});
            }
        }else{
            faltanporvisitar[i]= true;
        }
    }
    
    while(!cola.empty()){
        int w = get<1>(cola.top());
        cola.pop();
        S.push_back(w);
        for (int i = 0; i < listadeady[w].size(); i++) {
            int u = get<0>(listadeady[w][i]);
            bool pertenece = faltanporvisitar[u];
            if (!pertenece) {
                if (pi[u] > pi[w] + get<1>(listadeady[w][i])) {
                    pi[u] = pi[w] + get<1>(listadeady[w][i]);
                    cola.push({pi[u], u});
                    faltanporvisitar[u] = false; 
                }
            }
        }
        faltanporvisitar[w] = true;
    }
    return pi;
}

// Buscar St-eficientes
vector<int> buscarStEficientes(vector<tuple<int, int, int>> listaaristas, unordered_map<int, int> dijkstrade0, unordered_map<int, int> dijkstrademenos1, int n){
    vector<int> res;
    int caminominimo = dijkstrade0[n-1];
    for(int i = 0; i < listaaristas.size(); i ++){
        int v = min(get<0>(listaaristas[i]), get<1>(listaaristas[i]));
        int w = max(get<0>(listaaristas[i]), get<1>(listaaristas[i]));
        int c = get<2>(listaaristas[i]);
        if(caminominimo == dijkstrade0[v] + c + dijkstrademenos1[w] ||
           caminominimo == dijkstrade0[w] + c + dijkstrademenos1[v]) {
            res.push_back(c);
        }
    }
    return res;
}


int main(){
    int m, n;
    cin >> n;
    cin >> m;
    vector<tuple<int, int, int>> listaaristas;
    vector<vector<tuple<int, int>>> listadeady(n);
    for(int i = 0; i < m; i++){
        int v, w, c;
        cin >> v >> w >> c;
        listaaristas.push_back(make_tuple(v, w, c));
        if(v == w){
            listadeady[v].push_back(make_tuple(w, c));
        }else{
            listadeady[v].push_back(make_tuple(w, c));
            listadeady[w].push_back(make_tuple(v, c));
        }
    }
    
    // Corro Dijkstra desde 0
    unordered_map<int, int> dijkstrade0 = Dijkstra(listadeady, 0);
    // Corro Dijkstra desde n-1
    unordered_map<int, int> dijkstrademenos1 = Dijkstra(listadeady, n-1);
    
    vector<int> StEficientes = buscarStEficientes(listaaristas, dijkstrade0, dijkstrademenos1, n);
    
    int sumador = 0;
    if(StEficientes.size() == 0){
        sumador = numeric_limits<int>::max();
    }
    
    // Sumo o multiplico por 2 todas las aristas St-eficientes
    for(int j = 0; j < StEficientes.size(); j ++){
        sumador += StEficientes[j]*2;
    }
    
    cout << sumador << endl;

}