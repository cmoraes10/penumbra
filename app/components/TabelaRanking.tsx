"use client";

// Municipality ranking table. Supports name search, intermediate-region filter,
// and a cocoa-zone highlight toggle. Default sort follows the index, most to
// least forgotten.

import Link from "next/link";
import { useMemo, useState } from "react";

import type { Municipio } from "@/lib/tipos";
import { corDoIndice } from "@/lib/cores";
import { SeloCacau, SeloOpacidade } from "./Selos";

function formataInteiro(valor: number | null): string {
  return valor === null ? "sem dado" : valor.toLocaleString("pt-BR");
}

export default function TabelaRanking({ municipios }: { municipios: Municipio[] }) {
  const [busca, setBusca] = useState("");
  const [regiao, setRegiao] = useState("todas");
  const [soCacau, setSoCacau] = useState(false);

  const regioes = useMemo(
    () => Array.from(new Set(municipios.map((m) => m.regiao_intermediaria).filter(Boolean))).sort() as string[],
    [municipios],
  );

  const filtrados = useMemo(() => {
    const termo = busca.trim().toLowerCase();
    return municipios.filter((m) => {
      if (soCacau && !m.zona_cacaueira) return false;
      if (regiao !== "todas" && m.regiao_intermediaria !== regiao) return false;
      if (termo && !m.nome.toLowerCase().includes(termo)) return false;
      return true;
    });
  }, [municipios, busca, regiao, soCacau]);

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <input
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          placeholder="Buscar município"
          className="rounded-md border border-penumbra-borda bg-penumbra-card px-3 py-1.5 text-sm outline-none focus:border-penumbra-suave"
        />
        <select
          value={regiao}
          onChange={(e) => setRegiao(e.target.value)}
          className="rounded-md border border-penumbra-borda bg-penumbra-card px-3 py-1.5 text-sm"
        >
          <option value="todas">Todas as regiões</option>
          {regioes.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm text-penumbra-suave">
          <input type="checkbox" checked={soCacau} onChange={(e) => setSoCacau(e.target.checked)} />
          Só a zona cacaueira
        </label>
        <span className="ml-auto text-sm text-penumbra-suave">{filtrados.length} municípios</span>
      </div>

      <div className="overflow-x-auto rounded-lg border border-penumbra-borda">
        <table className="w-full text-sm">
          <thead className="bg-penumbra-card text-left text-penumbra-suave">
            <tr>
              <th className="px-3 py-2">nº</th>
              <th className="px-3 py-2">Município</th>
              <th className="px-3 py-2">Região</th>
              <th className="px-3 py-2 text-right">População</th>
              <th className="px-3 py-2 text-right">Índice</th>
            </tr>
          </thead>
          <tbody>
            {filtrados.map((m) => (
              <tr key={m.cod_ibge} className="border-t border-penumbra-borda hover:bg-penumbra-card/60">
                <td className="px-3 py-2 text-penumbra-suave">{m.rank_penumbra}</td>
                <td className="px-3 py-2">
                  <Link href={`/municipio/${m.cod_ibge}`} className="font-medium hover:underline">
                    {m.nome}
                  </Link>
                  <span className="ml-2 inline-flex gap-1 align-middle">
                    {m.zona_cacaueira && <SeloCacau />}
                    {!m.enviou_dca && <SeloOpacidade />}
                  </span>
                </td>
                <td className="px-3 py-2 text-penumbra-suave">{m.regiao_intermediaria ?? "—"}</td>
                <td className="px-3 py-2 text-right">{formataInteiro(m.populacao_2022)}</td>
                <td className="px-3 py-2 text-right">
                  <span className="inline-flex items-center gap-2">
                    <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: corDoIndice(m.indice_penumbra) }} />
                    {m.indice_penumbra.toFixed(1)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
