"use client";

// Wraps the map in a dynamic import with no SSR because Leaflet depends on the
// browser's window object and would break during server-side page generation.

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
