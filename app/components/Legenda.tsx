// Legenda das faixas de cor do mapa.

import { CLASSES } from "@/lib/cores";

export default function Legenda() {
  return (
    <div className="rounded-lg border border-penumbra-borda bg-penumbra-card p-3 text-xs">
      <p className="mb-2 font-medium text-penumbra-texto">Índice de Penumbra</p>
      <div className="flex flex-col gap-1">
        {CLASSES.map((c) => (
          <div key={c.rotulo} className="flex items-center gap-2">
            <span className="inline-block h-3 w-5 rounded-sm" style={{ backgroundColor: c.cor }} />
            <span className="text-penumbra-suave">{c.rotulo}</span>
          </div>
        ))}
      </div>
      <p className="mt-2 text-penumbra-suave">Mais claro, menos esquecido. Mais escuro, mais na penumbra.</p>
    </div>
  );
}
