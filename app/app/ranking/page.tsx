import TabelaRanking from "@/components/TabelaRanking";
import { getMunicipios } from "@/lib/dados";

export const metadata = {
  title: "Ranking, Penumbra",
  description: "Ranking dos municípios da Bahia pelo Índice de Penumbra.",
};

export default function RankingPage() {
  const municipios = getMunicipios();

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Ranking da penumbra</h1>
        <p className="mt-2 max-w-3xl text-penumbra-suave">
          Todos os municípios ordenados do mais ao menos esquecido. Busque uma cidade, filtre por região
          ou veja só a zona cacaueira. Clique num nome para abrir a ficha completa.
        </p>
      </div>
      <TabelaRanking municipios={municipios} />
    </div>
  );
}
