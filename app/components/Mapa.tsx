"use client";

// Envolve o mapa num carregamento dinamico sem renderizacao no servidor, porque
// o Leaflet depende do objeto window do navegador e quebraria se rodasse no
// servidor durante a geracao das paginas.

import dynamic from "next/dynamic";

const MapaPenumbra = dynamic(() => import("./MapaPenumbra"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[70vh] w-full items-center justify-center rounded-lg border border-penumbra-borda bg-penumbra-card text-penumbra-suave">
      Carregando o mapa...
    </div>
  ),
});

export default function Mapa() {
  return <MapaPenumbra />;
}
