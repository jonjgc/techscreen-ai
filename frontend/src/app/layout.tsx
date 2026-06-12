import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "TechScreen AI — Avaliação Automática de Testes Técnicos",
  description:
    "Plataforma que utiliza IA para avaliar testes técnicos de desenvolvedores com feedback detalhado de um Tech Lead Sênior virtual.",
  keywords: ["tech screen", "avaliação técnica", "code review", "inteligência artificial"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className={`${inter.variable} h-full`}>
      <body className="min-h-full flex flex-col gradient-bg">{children}</body>
    </html>
  );
}
