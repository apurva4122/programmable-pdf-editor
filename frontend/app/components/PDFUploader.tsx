'use client'

import { useState } from 'react'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Upload } from 'lucide-react'
import { Card } from '@/components/ui/card'

interface PDFUploaderProps {
    onUploaded: (pdfId: string) => void
    onSectionsDetected: (sections: any[]) => void
}

export default function PDFUploader({ onUploaded, onSectionsDetected }: PDFUploaderProps) {
    const [uploading, setUploading] = useState(false)
    const [processing, setProcessing] = useState(false)
    const [uploadedFile, setUploadedFile] = useState<string | null>(null)
    const [pdfId, setPdfId] = useState<string | null>(null)

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        setUploading(true)
        const formData = new FormData()
        formData.append('file', file)

        try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

            const id = response.data.pdf_id
            setPdfId(id)
            setUploadedFile(file.name)
            onUploaded(id)

      // Automatically process OCR
      setProcessing(true)
      const ocrResponse = await axios.post(`${apiUrl}/api/ocr/${id}`)
      onSectionsDetected(ocrResponse.data.sections)
      setProcessing(false)
    } catch (error: any) {
      console.error('Upload error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error'
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      alert(`Failed to upload PDF.\n\nError: ${errorMessage}\n\nBackend URL: ${apiUrl}\n\nPlease check:\n1. Backend is running on Railway\n2. CORS_ORIGINS includes your Vercel URL\n3. NEXT_PUBLIC_API_URL is set correctly`)
    } finally {
      setUploading(false)
    }
    }

    return (
        <div className="space-y-4">
            <Card className="border-2 border-dashed">
                <div className="p-8 text-center">
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileChange}
                        className="hidden"
                        id="pdf-upload"
                        disabled={uploading || processing}
                    />
                    <label htmlFor="pdf-upload" className="cursor-pointer">
                        <div className="flex flex-col items-center gap-4">
                            <Upload className="w-12 h-12 text-muted-foreground" />
                            <div>
                                <Button
                                    variant="outline"
                                    disabled={uploading || processing}
                                    asChild
                                >
                                    <span>
                                        {uploading ? 'Uploading...' : processing ? 'Processing with OCR...' : 'Select PDF File'}
                                    </span>
                                </Button>
                            </div>
                            <p className="text-sm text-muted-foreground">
                                {uploading ? 'Uploading your file...' : processing ? 'Scanning PDF with OCR...' : 'Choose a PDF file to upload'}
                            </p>
                        </div>
                    </label>
                </div>
            </Card>

            {uploadedFile && (
                <Card className="bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800">
                    <div className="p-4">
                        <p className="text-green-800 dark:text-green-200">
                            ✓ Uploaded: <strong>{uploadedFile}</strong>
                        </p>
                    </div>
                </Card>
            )}
        </div>
    )
}

