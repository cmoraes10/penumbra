// Single colour scale for Penumbra, shared across the map, ranking, and
// municipality profile so the same score always maps to the same colour.
//
// The visual idea follows the name. Low scores (less forgotten) appear light.
// As the score rises and the municipality sinks into the penumbra, the colour
// darkens toward deep red.

export type Classe = { limite: number; cor: string; rotulo: string };

// six classes by index range, from least to most forgotten
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
