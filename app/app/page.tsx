import Link from "next/link";
import { ArrowRight, MousePointerClick, TrendingDown } from "lucide-react";

import Mapa from "@/components/Mapa";
import Legenda from "@/components/Legenda";
import { SeloCacau } from "@/components/Selos";
import { getMeta, getMunicipios } from "@/lib/dados";

export default function Home() {
  const meta = getMeta();
  const municipios = getMunicipios();
  const top = municipios.slice(0, 10);

  return (
    <div className="flex flex-col gap-8">
      <section>
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          Os municípios que a Bahia deixou na meia-luz
        </h1>
        <p className="mt-3 max-w-3xl text-penumbra-suave">
          A Penumbra cruza dados abertos de renda, serviço público, orçamento e geografia para medir
          quais dos {meta.n_municipios} municípios baianos juntam, ao mesmo tempo, mais necessidade e
          menos atenção. O foco é o interior, e em especial a zona cacaueira, região que já teve o auge
          do cacau e afundou na sombra depois da praga da vassoura-de-bruxa.
        </p>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1fr_240px]">
        <Mapa />
        <div className="flex flex-col gap-4">
          <Legenda />
          <div className="flex items-start gap-2 rounded-lg border border-penumbra-borda bg-penumbra-card p-3 text-xs text-penumbra-suave">
            <MousePointerClick size={16} className="mt-0.5 shrink-0" />
            <span>Clique num município no mapa para abrir a ficha com os indicadores e o porquê da nota.</span>
          </div>
        </div>
      </section>

      <section>
        <h2 className="mb-3 flex items-center gap-2 text-lg font-medium">
          <TrendingDown size={18} className="text-penumbra-destaque" />
          As dez cidades mais na penumbra
        </h2>
        <ol className="grid gap-2 sm:grid-cols-2">
          {top.map((m) => (
            <li key={m.cod_ibge}>
              <Link
                href={`/municipio/${m.cod_ibge}`}
                className="flex items-center justify-between rounded-md border border-penumbra-borda bg-penumbra-card px-3 py-2 hover:border-penumbra-suave"
              >
                <span className="flex items-center gap-2">
                  <span className="text-penumbra-suave">{m.rank_penumbra}.</span>
                  <span className="font-medium">{m.nome}</span>
                  {m.zona_cacaueira && <SeloCacau />}
                </span>
                <span className="text-penumbra-destaque">{m.indice_penumbra.toFixed(1)}</span>
              </Link>
            </li>
          ))}
        </ol>
        <Link
          href="/ranking"
          className="mt-3 inline-flex items-center gap-1.5 text-sm text-penumbra-suave hover:text-penumbra-texto"
        >
          Ver o ranking completo dos {meta.n_municipios} municípios
          <ArrowRight size={15} />
        </Link>
      </section>
    </div>
  );
}
