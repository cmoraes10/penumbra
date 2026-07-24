// Escala de cor unica da Penumbra, compartilhada entre o mapa, o ranking e a
// ficha, para que a mesma nota tenha sempre a mesma cor em todo o site.
//
// A ideia visual segue o nome. Notas baixas, municipios menos esquecidos,
// aparecem claras. Conforme a nota sobe e o municipio afunda na penumbra, a cor
// escurece rumo ao vermelho profundo.

export type Classe = { limite: number; cor: string; rotulo: string };

// seis classes por faixa de indice, do menos ao mais esquecido
export const CLASSES: Classe[] = [
  { limite: 20, cor: "#fde68a", rotulo: "0 a 20" },
  { limite: 40, cor: "#fbbf24", rotulo: "20 a 40" },
  { limite: 55, cor: "#f97316", rotulo: "40 a 55" },
  { limite: 70, cor: "#ea580c", rotulo: "55 a 70" },
  { limite: 85, cor: "#b91c1c", rotulo: "70 a 85" },
  { limite: 100.01, cor: "#7f1d1d", rotulo: "85 a 100" },
];

export function corDoIndice(indice: number): string {
  for (const classe of CLASSES) {
    if (indice < classe.limite) return classe.cor;
  }
  return CLASSES[CLASSES.length - 1].cor;
}
