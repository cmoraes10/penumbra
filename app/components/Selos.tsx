// Small badge components that flag special conditions for a municipality.

import { EyeOff, Info, Sprout } from "lucide-react";

export function SeloCacau() {
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-amber-700/50 bg-amber-900/30 px-2 py-0.5 text-xs text-amber-300">
      <Sprout size={12} />
      Zona cacaueira
    </span>
  );
}

export function SeloOpacidade() {
  return (
    <span
      className="inline-flex items-center gap-1 rounded-full border border-red-800/50 bg-red-950/40 px-2 py-0.5 text-xs text-red-300"
      title="O município não prestou contas ao Tesouro Nacional no ano de referência"
    >
      <EyeOff size={12} />
      Não prestou contas
    </span>
  );
}

export function SeloImputado({ campos }: { campos: string[] }) {
  if (!campos.length) return null;
  return (
    <span
      className="inline-flex items-center gap-1 rounded-full border border-penumbra-borda bg-penumbra-card px-2 py-0.5 text-xs text-penumbra-suave"
      title={`Dado ausente, preenchido com valor mediano: ${campos.join(", ")}`}
    >
      <Info size={12} />
      {campos.length} dado{campos.length > 1 ? "s" : ""} imputado{campos.length > 1 ? "s" : ""}
    </span>
  );
}
