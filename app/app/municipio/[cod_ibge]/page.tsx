import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft } from "lucide-react";

import RadarSubescores from "@/components/RadarSubescores";
import { SeloCacau, SeloImputado, SeloOpacidade } from "@/components/Selos";
import { corDoIndice } from "@/lib/cores";
import { getMunicipio, getMunicipios } from "@/lib/dados";

export function generateStaticParams() {
  return getMunicipios().map((m) => ({ cod_ibge: m.cod_ibge }));
}

export function generateMetadata({ params }: { params: { cod_ibge: string } }) {
  const m = getMunicipio(params.cod_ibge);
  return { title: m ? `${m.nome}, Penumbra` : "Município, Penumbra" };
}

function reais(valor: number | null): string {
  return valor === null ? "sem dado" : valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

function numero(valor: number | null, casas = 0): string {
  return valor === null ? "sem dado" : valor.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
}

export default function MunicipioPage({ params }: { params: { cod_ibge: string } }) {
  const m = getMunicipio(params.cod_ibge);
  if (!m) notFound();

  const indicadores: { rotulo: string; valor: string; fonte: string }[] = [
    { rotulo: "População (Censo 2022)", valor: numero(m.populacao_2022), fonte: "IBGE" },
    { rotulo: "Densidade (hab/km²)", valor: numero(m.densidade_hab_km2, 1), fonte: "IBGE" },
    { rotulo: "PIB per capita", valor: reais(m.pib_per_capita), fonte: "IBGE, 2021" },
    { rotulo: "IDHM", valor: numero(m.idhm_2010, 3), fonte: "IPEA, 2010" },
    { rotulo: "IDEB anos iniciais", valor: numero(m.ideb_ai_2023, 1), fonte: "INEP, 2023" },
    { rotulo: "Mortalidade infantil (por mil)", valor: numero(m.mortalidade_infantil_2010, 1), fonte: "IPEA, 2010" },
    { rotulo: "Autonomia fiscal", valor: m.autonomia_fiscal === null ? "sem dado" : `${(m.autonomia_fiscal * 100).toFixed(1)}%`, fonte: "Tesouro, 2022" },
    { rotulo: "Investimento por habitante", valor: reais(m.investimento_pc), fonte: "Tesouro, 2022" },
    { rotulo: "Distância até Salvador", valor: m.distancia_capital_km === null ? "sem dado" : `${numero(m.distancia_capital_km, 0)} km`, fonte: "IBGE" },
  ];

  return (
    <div className="flex flex-col gap-6">
      <Link
        href="/ranking"
        className="inline-flex items-center gap-1.5 text-sm text-penumbra-suave hover:text-penumbra-texto"
      >
        <ArrowLeft size={15} />
        voltar ao ranking
      </Link>

      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{m.nome}</h1>
          <p className="mt-1 text-penumbra-suave">
            {m.microrregiao}, {m.regiao_intermediaria ?? m.mesorregiao}
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {m.zona_cacaueira && <SeloCacau />}
            {!m.enviou_dca && <SeloOpacidade />}
            <SeloImputado campos={m.imputados} />
          </div>
        </div>
        <div className="rounded-lg border border-penumbra-borda bg-penumbra-card px-5 py-3 text-right">
          <div className="text-xs text-penumbra-suave">Índice de Penumbra</div>
          <div className="text-3xl font-semibold" style={{ color: corDoIndice(m.indice_penumbra) }}>
            {m.indice_penumbra.toFixed(1)}
          </div>
          <div className="text-xs text-penumbra-suave">nº {m.rank_penumbra} de mais esquecido</div>
        </div>
      </header>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-penumbra-borda bg-penumbra-card p-4">
          <h2 className="mb-2 text-sm font-medium text-penumbra-suave">Por que está na penumbra</h2>
          <RadarSubescores subescores={m.subescores} />
        </div>

        <div className="rounded-lg border border-penumbra-borda bg-penumbra-card p-4">
          <h2 className="mb-3 text-sm font-medium text-penumbra-suave">Indicadores</h2>
          <table className="w-full text-sm">
            <tbody>
              {indicadores.map((ind) => (
                <tr key={ind.rotulo} className="border-t border-penumbra-borda first:border-t-0">
                  <td className="py-2 text-penumbra-suave">{ind.rotulo}</td>
                  <td className="py-2 text-right font-medium">{ind.valor}</td>
                  <td className="py-2 pl-3 text-right text-xs text-penumbra-suave">{ind.fonte}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <Link href="/metodologia" className="text-sm text-penumbra-suave hover:text-penumbra-texto">
        Como o índice é calculado
      </Link>
    </div>
  );
}
