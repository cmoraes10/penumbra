import { getMeta } from "@/lib/dados";
import { ROTULO_SINAL } from "@/lib/tipos";
import type { Subescores } from "@/lib/tipos";

export const metadata = {
  title: "Metodologia, Penumbra",
  description: "Como o Índice de Penumbra é calculado, com suas fontes e seus pesos.",
};

const DESCRICAO_SINAL: Record<keyof Subescores, string> = {
  carencia_renda: "PIB por habitante. Renda baixa marca a severidade da necessidade material.",
  carencia_servico: "Média do IDHM, do IDEB dos anos iniciais e do inverso da mortalidade infantil.",
  gap_capacidade_orcamentaria: "Quanto o município arrecada por conta própria frente ao que gasta. Quem não presta contas entra como sinal de opacidade.",
  distancia_capital: "Distância até Salvador. Quem está longe da capital some do radar.",
  densidade_baixa: "Habitantes por quilômetro quadrado. Territórios esparsos raramente aparecem nas análises.",
  populacao_pequena: "Tamanho da população. Cidades pequenas têm pouco peso eleitoral e midiático.",
};

export default function MetodologiaPage() {
  const meta = getMeta();
  const chaves = Object.keys(ROTULO_SINAL) as (keyof Subescores)[];

  return (
    <div className="flex max-w-3xl flex-col gap-8">
      <section>
        <h1 className="text-2xl font-semibold tracking-tight">Metodologia</h1>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-medium">O que significa penumbra</h2>
        <p className="text-penumbra-suave">
          Penumbra é a faixa de meia-luz entre a sombra total e a claridade plena. Não é o breu, onde
          nada se vê, nem a luz cheia do holofote, onde tudo aparece. É o entremeio, o lugar onde alguma
          coisa existe mas quase ninguém repara. Foi esse estado que quisemos nomear. Os municípios que
          este índice ilumina não são invisíveis por decreto, estão ali, com nome, código e gente. Mas
          vivem numa zona cinzenta de atenção pública, longe da manchete e da agenda de campanha.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-medium">A zona cacaueira</h2>
        <p className="text-penumbra-suave">
          O coração do projeto é o sul da Bahia. A região do cacau já foi das mais ricas do país e
          despencou para o esquecimento a partir do fim dos anos 1980, quando a praga da vassoura-de-bruxa
          arrasou a lavoura. Existe até hoje uma controvérsia, defendida por parte dos produtores e
          pesquisadores e alvo de investigação, de que o fungo teria sido introduzido de propósito. Este
          projeto não toma partido nessa disputa. O que ele faz é medir, com dados, o tamanho da sombra em
          que a região acabou.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-medium">Os seis sinais</h2>
        <p className="text-penumbra-suave">
          Cada município recebe um escore de 0 a 1 em seis sinais, agrupados em três ideias, a carência da
          necessidade, a falta de orçamento para agir e a invisibilidade. A nota final é a soma ponderada
          desses sinais, reescalada de 0 a 100. Quanto maior, mais fundo na penumbra.
        </p>
        <div className="overflow-hidden rounded-lg border border-penumbra-borda">
          <table className="w-full text-sm">
            <thead className="bg-penumbra-card text-left text-penumbra-suave">
              <tr>
                <th className="px-3 py-2">Sinal</th>
                <th className="px-3 py-2">O que mede</th>
                <th className="px-3 py-2 text-right">Peso</th>
              </tr>
            </thead>
            <tbody>
              {chaves.map((c) => (
                <tr key={c} className="border-t border-penumbra-borda align-top">
                  <td className="px-3 py-2 font-medium">{ROTULO_SINAL[c]}</td>
                  <td className="px-3 py-2 text-penumbra-suave">{DESCRICAO_SINAL[c]}</td>
                  <td className="px-3 py-2 text-right">{(meta.pesos[c] * 100).toFixed(0)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-medium">Como o número é montado</h2>
        <p className="text-penumbra-suave">
          Cada indicador bruto vira um percentil dentro do conjunto dos municípios, o que torna o índice
          resistente a casos extremos como Salvador. Renda e população passam por logaritmo antes, para
          suavizar a cauda. Um dado que falta recebe o valor mediano, nunca o pior, para não punir a cidade
          pela ausência da informação. Já um município que não prestou contas ao Tesouro recebe escore alto
          no sinal de orçamento, porque a falta de transparência é, ela mesma, um sinal de penumbra. Para
          provar que a ordem não depende de um chute de peso, o site também calcula uma versão com todos os
          sinais valendo o mesmo.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-medium">Fontes</h2>
        <ul className="flex flex-col gap-1 text-sm text-penumbra-suave">
          {meta.fontes.map((f) => (
            <li key={f.nome}>
              <a href={f.url} className="hover:text-penumbra-texto hover:underline" target="_blank" rel="noreferrer">
                {f.nome}
              </a>{" "}
              <span className="text-penumbra-suave">({f.ano})</span>
            </li>
          ))}
        </ul>
        <p className="text-xs text-penumbra-suave">
          Dados coletados em {meta.gerado_em.slice(0, 10)}. Índice sobre {meta.n_municipios} municípios da {meta.uf}.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-medium">Aviso</h2>
        <p className="text-penumbra-suave">
          Projeto independente e sem vínculo partidário. Não diz em quem votar. Reúne dados públicos para
          ampliar o campo de visão às vésperas das eleições de 2026, quando o interior costuma ficar fora do
          roteiro. O índice não substitui o conhecimento de quem vive no lugar, apenas devolve contorno a
          quem estava na meia-luz.
        </p>
      </section>
    </div>
  );
}
