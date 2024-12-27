package aed;

public class SistemaCNE {
    private String[] nombresxPartido;
    private String[] nombresxDistrito;
    private int[] bancasPorDistrito;
    private int[] rangoMesasDistritos;
    private VotosPartido[] votos;
    private int[][] votosDiputados; 
    private int cantVotosFst;
    private int cantVotosSec;
    private int votosTotales;
    private dHondt[] votosDipPorDistrito;

    // |nombresxPartido| >= 2 &&L |nombresxPartido| == |votos| && (forall i : Z)(0 <= i < |votosDiputados| -> |votosDiputados[i]| == |nombresxPartido|)
    // |nombresxDistrito| == |bancasporDistrito| && |bancasporDistrito| == |rangoMesasDistritos|&& |rangoMesasDistritos| == |votosDiputados| && |votosDiputados| == |votosDipPorDistrito| 
    // 0 <= cantVotosSec <= cantVotosFst <= votosTotales
    // sum (i = 0) ^(|votos|-1) (votos[i].presidenciales) == votosTotales
    // sum (i = 0) ^(|votos|-1) (votos[i].diputados) == votosTotales
    // sum (i = 0) ^(|votosDiputados|-1) sum (j = 0) ^(|votosDiputados[i]|-1) (votosDiputados[i][j]) == votosTotales
    // (forall i: Z) :: (0 <= i < |rangoMesasDistritos| − 1) ==>L rangoMesasDistritos[i] < rangoMesasDistritos[i + 1]
    // (forall i: Z) :: (0 <= i < |votosDipPorDistrito|)  ==>L sum (j = 0) ^(|votosDipPorDistrito[i]|-1) (votosDipPorDistrito[i].heap2array[j].valorInicial) == votosTotales
    // (forall i: Z):: (0 <= i < |votosDipPorDistrito|) && forall j: Z :: (0 <= j < |votosDipPorDistrito[i]|) ==>L (0 <= votosDipPorDistrito[i].heap2array[j].partido < |nombresxPartido|)


    public class VotosPartido{
        private int presidente;
        private int diputados;
        VotosPartido(int presidente, int diputados){this.presidente = presidente; this.diputados = diputados;}
        public int votosPresidente(){return presidente;}
        public int votosDiputados(){return diputados;}
    }

    public SistemaCNE(String[] nombresDistritos, int[] diputadosPorDistrito, String[] nombresPartidos, int[] ultimasMesasDistritos) {
        int P = nombresPartidos.length;                                          // El primer for al tener cosas O(1) es O(P)
        int D = nombresDistritos.length;                                         // CrearHeap tiene un for con cosas O(1) y votosDiputados[i] es de tamaño P   
        nombresxPartido = nombresPartidos;                                       // por eso en este caso la funcion es O(P). 
        nombresxDistrito = nombresDistritos;                                     // El segundo for como tiene O(P) adentro y es recorrido D veces es O(D*P)
        bancasPorDistrito = diputadosPorDistrito;                                // Entonces O(P) + O(D*P) es O(D*P) 
        rangoMesasDistritos = ultimasMesasDistritos;
        votos = new VotosPartido[P];
        votosDiputados = new int[D][P];
        votosDipPorDistrito = new dHondt[D];
        for (int i = 0; i < P; i++){
            votos[i] = new VotosPartido(0,0);
        }
        for (int i = 0; i < D; i++) {
            votosDipPorDistrito[i] = new dHondt(P);
            votosDipPorDistrito[i].crearHeap(votosDiputados[i]);
        }
        cantVotosFst = 0;
        cantVotosSec = 0;
        votosTotales = 0;
    }

    public String nombrePartido(int idPartido) {   //acceder a una posicion en un array es O(1)
        return nombresxPartido[idPartido];
    }

    public String nombreDistrito(int idDistrito) { //acceder a una posicion en un array es O(1)
        return nombresxDistrito[idDistrito];
    }

    public int diputadosEnDisputa(int idDistrito) { //acceder a una posicion en un array es O(1)
        return bancasPorDistrito[idDistrito];
    }

    public String distritoDeMesa(int idMesa) {  //como sabemos que rangoMesasDistritos esta ordenada crecientemente aplicamos el algoritmo 
        int n = rangoMesasDistritos.length;    //de busqueda binaria que es O(log(n)). n siendo D en nuestro caso ya que es la longitud de rangoMesasDistritos
        int i = 0;                             //en busqueda binaria voy fijandome en el elemento de la mitad si es mayor o menor a mi elemento asi
        int j = n - 1;                         //puedo descartar la otra mitad y asi sucesivamente voy descartando 
        while (i != j){                        //como las otras cosas son asignaciones O(1) me queda O(log(D))
            int m = (i + j)/2;
            if (rangoMesasDistritos[m] > idMesa) {
                j = m;                
            } else{
                i = m + 1;
            }
        }
        return nombresxDistrito[j];
    }

    public int idDeDistrito(int idMesa) {
        int n = rangoMesasDistritos.length;
        int i = 0; 
        int j = n - 1;
        while (i != j){
            int m = (i + j)/2;
            if (rangoMesasDistritos[m] > idMesa) {
                j = m;                
            } else{
                i = m + 1;
            }
        }
        return j;
    }

    public int[] maximoySeg(VotosPartido[] list){
        int max = 0;
        int seg = 0;
        for (int i = 0; i < list.length; i++){
            if (list[i].presidente >= max){
                seg = max;
                max = list[i].presidente;
            }
            else if (list[i].presidente >= seg){
                seg = list[i].presidente;
            }
        }
        int[] res = new int[2];
        res[0] = max;
        res[1] = seg;
        return res;
    }

    public void registrarMesa(int idMesa, VotosPartido[] actaMesa) { // Al llamar a la funcion idDeDistrito tenemos O(log(D)) porque es busqueda binaria.  
        int P = nombresxPartido.length;                              // El for tiene todas cosas O(1) entonces es O(P).
        int idDistrito = idDeDistrito(idMesa);                       // La funcion maximoyseg es O(P) porque tiene un for con cosas O(1)
        for (int i = 0; i < P; i++){                                 // Entonces quedaria O(P) + O(P) + O(log(D)) que es O(P + log(D))
           votos[i].presidente += actaMesa[i].presidente;
           votos[i].diputados += actaMesa[i].diputados;
           votosDiputados[idDistrito][i] += actaMesa[i].diputados;
           votosTotales += actaMesa[i].presidente;
           if (votosDipPorDistrito[idDistrito].maxHeap[i].partido == i){
                votosDipPorDistrito[idDistrito].maxHeap[i].valorActual += actaMesa[i].diputados;
                votosDipPorDistrito[idDistrito].maxHeap[i].valorInicial += actaMesa[i].diputados;
           }
        }
        cantVotosFst = maximoySeg(votos)[0];
        cantVotosSec = maximoySeg(votos)[1];       
    }

    public int votosPresidenciales(int idPartido) { //acceder a una posicion en un array es O(1)
        return votos[idPartido].presidente;
    }

    public int votosDiputados(int idPartido, int idDistrito) { //acceder a una posicion en un array de arrays es O(1)
        return votosDiputados[idDistrito][idPartido];
    }

    public int porcentaje(int x, int y) {
        return (x*100)/y;
    }

    public boolean pasaElUmbral(int valor){
        return(porcentaje(valor, votosTotales) >= 3);
    }

    public int[] resultadosDiputados(int idDistrito){              // El primer for como tiene cosas O(1) es O(P)
        int bancas = 1;                                            // Llamar a la funcion floyd es O(P)
        int P = nombresxPartido.length;                            // La funcion ordenar es O(log(P)) y al estar dentro de un while que se recorre D veces es O(D*log(P)) 
        int[] res = new int[P];                                    // O(P) + O(P) + O(D*log(P)) es O(D*log(P))
        for (int i = 0; i < P; i++){
            votosDipPorDistrito[idDistrito].maxHeap[i].bancasAsignadas = 1;
            votosDipPorDistrito[idDistrito].maxHeap[i].valorActual = votosDipPorDistrito[idDistrito].maxHeap[i].valorInicial;
        }
        votosDipPorDistrito[idDistrito].floyd();
        while (bancas <= bancasPorDistrito[idDistrito]){
            int vI = votosDipPorDistrito[idDistrito].maxHeap[0].valorInicial;
            int bA = votosDipPorDistrito[idDistrito].maxHeap[0].bancasAsignadas;
            int pA = votosDipPorDistrito[idDistrito].maxHeap[0].partido;
            if (pA != P-1 && pasaElUmbral(votos[pA].diputados)){
               res[pA] += 1;
               votosDipPorDistrito[idDistrito].maxHeap[0].bancasAsignadas += 1;
               votosDipPorDistrito[idDistrito].maxHeap[0].valorActual = (vI)/(bA + 1);
               votosDipPorDistrito[idDistrito].ordenar(0);
               bancas ++;
            }
            else{
               votosDipPorDistrito[idDistrito].maxHeap[0].bancasAsignadas += 1;
               votosDipPorDistrito[idDistrito].maxHeap[0].valorActual = (vI)/(bA + 1);
               votosDipPorDistrito[idDistrito].ordenar(0);
            }
        }
        return res;
    }
 

    public boolean hayBallotage(){ //en el if se comparan cosas O(1) y se llama a una funcion O(1) tambien asi que es O(1) + O(1) = O(max{1,1})= O(1)
        boolean res = true;
        if ((porcentaje(cantVotosFst, votosTotales) >= 45) || ((porcentaje(cantVotosFst, votosTotales) >= 40) && (porcentaje(cantVotosFst, votosTotales) - porcentaje(cantVotosSec, votosTotales) >= 10))){
            res = false;
        }
        return res;
    }
}

