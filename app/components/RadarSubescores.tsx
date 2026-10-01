"use client";

// Radar chart of the six sub-scores for a municipality. Shows at a glance why
// it is in the penumbra: deprivation, distance, fiscal gap, or some combination.

import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";

import type { Subescores } from "@/lib/tipos";
import { ROTULO_SINAL } from "@/lib/tipos";

export default function RadarSubescores({ subescores }: { subescores: Subescores }) {
  const dados = (Object.keys(ROTULO_SINAL) as (keyof Subescores)[]).map((chave) => ({
    sinal: ROTULO_SINAL[chave],
    valor: Number((subescores[chave] * 100).toFixed(0)),
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={dados} outerRadius="70%">
        <PolarGrid stroke="#252a36" />
        <PolarAngleAxis dataKey="sinal" tick={{ fill: "#9aa3b2", fontSize: 11 }} />
        <Radar dataKey="valor" stroke="#e8a838" fill="#e8a838" fillOpacity={0.4} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
