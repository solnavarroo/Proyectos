package aed;

public class dHondt {
    public Nodo[] maxHeap;
    private int longitud;

    //(forall i : Z):: (0 <= i < longitud-1 && ((2*i)+2 < longitud ==> maxHeap[i] > maxHeap[(2*i)+1] && maxHeap[i] > maxHeap[(2*i)+2])
    // && (forall j : Z)::((0 <= j < longitud-1 && ((2*j)+1 < longitud && (2*j)+2 > longitud)==> maxHeap[j] > maxHeap[(2*j)+1])
    // longitud == |maxHeap|
    // (forall i : Z):: (0 <= i < longitud) ==>L  (maxHeap[i].valorInicial / maxHeap[i].bancasAsignadas == maxHeap[i].valorActual)
    // (forall i : Z):: (0 <= i < longitud) ==>L  (maxHeap[i].valorInicial >= 0 && maxHeap[i].valorActual >= 0 && maxHeap[i].partido >= 0 && maxHeap[i].bancasAsignadas >= 1)

    public class Nodo {
        int valorInicial;
        int valorActual;
        int partido;
        int bancasAsignadas;

        Nodo(int v, int posicion){valorInicial= v; valorActual = v; partido = posicion; bancasAsignadas = 1;}
    }

    public dHondt(int maxSize) {
        longitud = 0;
        maxHeap = new Nodo[maxSize];
    }

    public void swap(int i, int j){
       Nodo swap = maxHeap[i];
       maxHeap[i] = maxHeap[j];
       maxHeap[j] = swap;
    }

    public Nodo crearNodo(int elem, int partido){
       Nodo nuevo = new Nodo(elem, partido);
       return nuevo;
    }

    public int posMayorHijo(int pos){
        if (maxHeap[pos*2 + 1].valorActual > maxHeap[pos*2 + 2].valorActual){
          return pos*2 + 1;
        }
        else {
          return pos*2 + 2;
        }
    }

    public void ordenar(int i){
      int n = longitud;
      int posMayor = 0;
      if ((2*i + 1) < n){
        if ((2*i + 2) < n){
            posMayor = posMayorHijo(i);
        }
        else {
            posMayor = 2*i + 1;
        }
        if (maxHeap[posMayor].valorActual > maxHeap[i].valorActual){
          swap(i, posMayor);
          ordenar(posMayor);
        }
      }
    }

    public void agregar(int elem, int partido){
        Nodo nodo = crearNodo(elem, partido);
        longitud += 1;
        maxHeap[longitud - 1] = nodo;
    }

    public void crearHeap(int[] list){
        for (int i = 0; i < list.length; i++){
           agregar(list[i], i);
        }
    }

    public void floyd(){
        int n = longitud;
        for(int i = n/2; i >=0 ; i--){
          ordenar(i);
        }
    }
}