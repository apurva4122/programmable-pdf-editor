import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Programmable PDF Editor',
  description: 'Edit PDFs programmatically with OCR and batch generation',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

