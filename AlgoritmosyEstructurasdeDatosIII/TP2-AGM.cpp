// Solana Navarro
// 906/22

// Este trabajo practico tiene como objetivo categorizar todas las aristas de un grafo conexo, 
// determinando si pertenecen a ninguno, a al menos uno, o a todos los arboles generadores minimos (AGMs).

// Para abordar este problema, empece agrupando las aristas por peso y creando un subgrafo 
// donde cada nodo representa una componente conexa. Si existe una arista (u, v) en el grafo, 
// se transforma en (find(u), find(v)) en el subgrafo.

// Una vez que el subgrafo esta generado, es importante identificar cuales aristas son puentes. 
// Las aristas puentes son aquellas cuya eliminacion desconectaria el grafo, es decir, no pertenecen a ningun ciclo, 
// entonces se clasifica como "any". Por otro lado, si no es puente, se clasifica como "at least one". 
// Sin embargo, al reducir una componente conexa a un solo nodo, pueden surgir aristas repetidas, 
// resultando en un multigrafo. Como los algoritmos DFS y Cubren no manejan esta situacion por si mismos, 
// decidi implementar un diccionario que registre la cantidad de veces que aparece cada arista. 
// Asi, si el valor de una arista es mayor a 1, significa que pertenece a "at least one".

// Importaciones necesarias
#include <iostream>
#include <vector>
#include <algorithm>
#include <unordered_map>
#include <map>
#include <tuple>
#include <utility>

using namespace std;

// Clase DisjointSet para manejar componentes conexas (Practica)
class DisjointSet {
public:
    vector<int> rank, parent;

    DisjointSet(int n) {
        rank.resize(n + 1, 0);
        parent.resize(n + 1);
        for (int i = 0; i <= n; i++) {
            parent[i] = i; 
        }
    }

    int findSet(int node) {
        if (node == parent[node]) return node;
        return parent[node] = findSet(parent[node]); 
    }

    void unionByRank(int u, int v) {
        int uRepresentative = findSet(u);
        int vRepresentative = findSet(v);
        if (uRepresentative == vRepresentative) return; 
        if (rank[uRepresentative] < rank[vRepresentative]) {
            parent[vRepresentative] = uRepresentative;
        } else if (rank[uRepresentative] > rank[vRepresentative]) {
            parent[uRepresentative] = vRepresentative;
        } else {
            parent[vRepresentative] = uRepresentative;
            rank[uRepresentative]++;
        }
    }
};

// Estructura del grafo para facilitar las operaciones
struct grafo {
    map<tuple<int, int>, int> listadearistas;  // Lista de aristas con su cantidad
    unordered_map<int, vector<int>> ady;       // Lista de adyacencias
    unordered_map<int, int> backsup, backinf, padre, memo, empieza;
    unordered_map<int, vector<int>> tree_edges; // Almacena las aristas de arbol
    int tiempo;

    // Metodo de limpieza entre grupo y grupo
    void inicializar() {
        listadearistas.clear();
        ady.clear();
        backsup.clear();
        backinf.clear();
        padre.clear();
        memo.clear();
        empieza.clear();
        tree_edges.clear();
        tiempo = 0;
    }

    // DFS modificado para encontrar las Backward edges (Practica con algunas modificaciones)
    void dfs(int v, int p = -1) {
        empieza[v] = tiempo++;
        padre[v] = p;
        for (const auto& u : ady[v]) {
            if (empieza.find(u) == empieza.end()) {
                if(tree_edges[v].empty()){
                   tree_edges[v]= {u};
                }else{
                    tree_edges[v].push_back(u);
                }
                padre[u] = v;
                dfs(u, v);
            }
            else if (u != padre[v]) {
                if (empieza[u] < empieza[v]) {
                    backsup[v] ++;
                }
                else {
                    backinf[v] ++;
                }
            }
        }
    }

    // Cuenta cuantas aristas Backward edge cubren a un nodo (Practica)
    int cubren(int v, int p) {
        if (memo.find(v) != memo.end()) return memo[v];
        int res = 0;
        for (int hijo : tree_edges[v]) {
            if (hijo != p) {
                res += cubren(hijo, v);
            }
        }
        res += backsup[v];
        res -= backinf[v];
        memo[v] = res;
        return res;
    }

    // Metodo para encontrar aristas puentes en todas las componentes conexas
    void encontrarPuentes() {
        for (const auto& par : ady) {
            int u = par.first;
            const vector<int>& v = par.second;
            if (empieza.find(u) == empieza.end() && !v.empty()) {
                dfs(u);
                cubren(u, -1);
            }
        }
    }
};

// Funcion de Kruskal modificada
vector<tuple<int, string>> kruskal(vector<tuple<int, int, int, int>>& E, int n) {
    sort(E.begin(), E.end());  // Ordena las aristas por peso
    DisjointSet dsu(n);
    grafo subgrafo;
    vector<tuple<int, string>> res(E.size(), make_tuple(-1, "none")); // Inicializa la respuesta

    if (E.empty()) return res;

    int aristas = 0; // Contador de aristas en el AGM
    int i = 0; // Posicion actual en las aristas 

    while (i < E.size() && aristas < n - 1) {
        const int peso = get<0>(E[i]);
        vector<tuple<int, int, int, int>> grupo;

        // Agrupa aristas del mismo peso
        while (i < E.size() && get<0>(E[i]) == peso) {
            grupo.push_back(E[i]);
            i++;
        }

        // Limpia el subgrafo para generar uno nuevo
        subgrafo.inicializar();

        // Genera la lista de aristas contando cuantas veces aparece cada una
        for(int k = 0; k < grupo.size(); k ++){
            int u = get<1>(grupo[k]);
            int v = get<2>(grupo[k]);
            int indice = get<3>(grupo[k]);
            int repu = dsu.findSet(u);
            int repv = dsu.findSet(v);
            if(repu > repv) swap(repu, repv);
            if(repu != repv){
                if(subgrafo.listadearistas.find({repu, repv}) == subgrafo.listadearistas.end()){
                    subgrafo.listadearistas[{repu, repv}] = 1;
                }else{
                    subgrafo.listadearistas[{repu, repv}]++;
                }
            }else{ // Arista invalida, pertenece a la misma componente. La marca como None
                res[indice] = make_tuple(indice, "none");
            }
        }

        // Genera la lista de adyacencias para el subgrafo
        for(const auto& par : subgrafo.listadearistas){
            int repu = get<0>(par.first);
            int repv = get<1>(par.first);
            if(subgrafo.ady.find(repu) == subgrafo.ady.end()){
                subgrafo.ady[repu] = {repv};
            }else{
                subgrafo.ady[repu].push_back(repv);
            }
            if(subgrafo.ady.find(repv) == subgrafo.ady.end()){
                subgrafo.ady[repv] = {repu};
            }else{
                subgrafo.ady[repv].push_back(repu);
            }
        }

        // Ejecuta los algoritmos para encontrar aristas puentes
        subgrafo.encontrarPuentes();

        vector<tuple<int, int, int>> aristas_any;          // Aristas que son puentes
        vector<tuple<int, int, int>> aristas_atleastone;   // Aristas que son "at least one"
        for(int k = 0; k < grupo.size(); k ++){
                int u = get<1>(grupo[k]);
                int v = get<2>(grupo[k]);
                int indice = get<3>(grupo[k]);
                int repu = dsu.findSet(u);
                int repv = dsu.findSet(v);
                if(repu > repv) swap(repu, repv);
                int cantidad = subgrafo.listadearistas[{repu, repv}];
               
                if (repu != repv){
                    if (subgrafo.empieza[repu] > subgrafo.empieza[repv]) swap(repu, repv);
                    if(subgrafo.memo[repv] == 0) {
                        // Si no hay backedge cubriendo, entonces es puente
                        bool es_unica = (cantidad == 1);// Verifica si es unica
                        if (es_unica) {
                            aristas_any.push_back({u, v, indice});
                            continue;
                        }
                    }
                    aristas_atleastone.push_back({u, v, indice});
                    continue;
                }
                aristas_atleastone.push_back({u, v, indice});
            }


        // Union de aristas "any"
        for (const auto& [u, v, indice] : aristas_any) {
            res[indice] = make_tuple(indice, "any");
            dsu.unionByRank(u, v);
            aristas++;
        }
            
        // Union de aristas "at least one" necesarias. No agrego todas ya que generan ciclos entre ellas.
        for (const auto& [u, v, indice] : aristas_atleastone) {
            int nuevou = dsu.findSet(u);
            int nuevov = dsu.findSet(v);
            if (nuevou == nuevov) {
                // Si forman un ciclo y no las marque antes como none:
                if (res[indice] == make_tuple(-1, "none")) {
                    res[indice] = make_tuple(indice, "at least one");
                }
            // Si no forman ciclo y puedo seguir agregando aristas
            } else if (aristas < n - 1) {
                res[indice] = make_tuple(indice, "at least one");
                dsu.unionByRank(u, v);
                aristas++;
            }
        }
    }
    return res;
}

// Input

int main() {
    vector<tuple<int, int, int, int>> E; // (peso, u, v, indice)
    int n; // Cantidad de nodos
    int m; // Cantidad de aristas

    cin >> n >> m;
    for (int i = 0; i < m; i++) {
        int u, v, peso;
        cin >> u >> v >> peso;
        E.push_back(make_tuple(peso, u, v, i)); 
    }

    vector<tuple<int, string>> res = kruskal(E, n);

    // Imprime los resultados
    for(int j = 0; j < res.size(); j++) {
        cout << get<1>(res[j]) << '\n';
    }

    return 0;
}