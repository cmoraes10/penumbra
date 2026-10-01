// Index data loader. Runs on the server during page generation, reading the
// file the pipeline wrote to public/data. Because it is a local file read,
// it never ends up in the browser bundle.

import fs from "node:fs";
import path from "node:path";

import type { IndiceData, Municipio } from "./tipos";

function carrega(): IndiceData {
  const caminho = path.join(process.cwd(), "public", "data", "indice.json");
  return JSON.parse(fs.readFileSync(caminho, "utf-8")) as IndiceData;
}

export function getIndice(): IndiceData {
  return carrega();
}

export function getMeta() {
  return carrega().meta;
}

export function getMunicipios(): Municipio[] {
  return carrega().municipios;
}

export function getMunicipio(cod: string): Municipio | null {
  return carrega().municipios.find((m) => m.cod_ibge === cod) ?? null;
}
