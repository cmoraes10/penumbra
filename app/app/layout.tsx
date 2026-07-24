import type { Metadata } from "next";
import Link from "next/link";
import { BookOpen, ExternalLink, ListOrdered, Map, Moon } from "lucide-react";

import "./globals.css";

export const metadata: Metadata = {
  title: "Penumbra, os municípios esquecidos da Bahia",
  description:
    "Um índice de dados abertos que revela os municípios do interior da Bahia mais esquecidos pela renda, pelo serviço público e pela atenção, com foco na zona cacaueira.",
};

const LINKS = [
  { href: "/", rotulo: "Mapa", Icone: Map },
  { href: "/ranking", rotulo: "Ranking", Icone: ListOrdered },
  { href: "/metodologia", rotulo: "Metodologia", Icone: BookOpen },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-penumbra-bg text-penumbra-texto antialiased">
        <header className="border-b border-penumbra-borda">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
            <Link href="/" className="flex items-center gap-2">
              <Moon size={20} className="text-penumbra-destaque" />
              <span className="text-xl font-semibold tracking-tight">Penumbra</span>
              <span className="hidden text-sm text-penumbra-suave sm:inline">
                o que a Bahia deixou na meia-luz
              </span>
            </Link>
            <nav className="flex gap-5 text-sm">
              {LINKS.map((l) => (
                <Link
                  key={l.href}
                  href={l.href}
                  className="flex items-center gap-1.5 text-penumbra-suave hover:text-penumbra-texto"
                >
                  <l.Icone size={16} />
                  <span className="hidden sm:inline">{l.rotulo}</span>
                </Link>
              ))}
            </nav>
          </div>
        </header>

        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>

        <footer className="border-t border-penumbra-borda">
          <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-6 text-sm text-penumbra-suave sm:flex-row sm:items-center sm:justify-between">
            <p className="max-w-2xl">
              Projeto de dados abertos, sem vínculo partidário. Fontes públicas do IBGE, IPEA, INEP e
              Tesouro Nacional. Feito para lançar luz sobre o interior baiano às vésperas das eleições de 2026.
            </p>
            <p className="flex items-center gap-1.5 whitespace-nowrap">
              <span>por Cauã Moraes ·</span>
              <a
                href="https://mowaveone.com"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-penumbra-texto hover:text-penumbra-destaque"
              >
                mowaveone
                <ExternalLink size={13} />
              </a>
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
