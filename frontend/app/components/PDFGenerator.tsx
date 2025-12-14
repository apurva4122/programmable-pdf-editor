'use client'

import { useState } from 'react'
import axios from 'axios'
import { ReplacementRule } from '../page'
import { saveAs } from 'file-saver'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Card } from '@/components/ui/card'

interface PDFGeneratorProps {
    pdfId: string
    rules: ReplacementRule[]
    numCopies: number
    onNumCopiesChange: (num: number) => void
}

export default function PDFGenerator({
    pdfId,
    rules,
    numCopies,
    onNumCopiesChange
}: PDFGeneratorProps) {
    const [generating, setGenerating] = useState(false)
    const [progress, setProgress] = useState(0)

    const handleGenerate = async () => {
        setGenerating(true)
        setProgress(0)

        try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await axios.post(
        `${apiUrl}/api/generate`,
                {
                    pdf_id: pdfId,
                    rules: rules,
                    num_copies: numCopies
                },
                {
                    responseType: 'blob',
                    onDownloadProgress: (progressEvent) => {
                        if (progressEvent.total) {
                            const percentCompleted = Math.round(
                                (progressEvent.loaded * 100) / progressEvent.total
                            )
                            setProgress(percentCompleted)
                        }
                    }
                }
            )

            // Download the zip file
            const blob = new Blob([response.data], { type: 'application/zip' })
            saveAs(blob, `generated_pdfs_${pdfId}.zip`)

            alert(`Successfully generated ${numCopies} PDF copies!`)
        } catch (error: any) {
            console.error('Generation error:', error)
            alert(`Failed to generate PDFs: ${error.response?.data?.detail || error.message}`)
        } finally {
            setGenerating(false)
            setProgress(0)
        }
    }

    return (
        <div className="space-y-6">
            <div className="space-y-2">
                <Label>Number of Copies to Generate</Label>
                <Input
                    type="number"
                    value={numCopies}
                    onChange={(e) => onNumCopiesChange(parseInt(e.target.value) || 1)}
                    min="1"
                    max="1000"
                />
            </div>

            <Card className="bg-primary/5 border-primary/20">
                <div className="p-4">
                    <p className="text-sm">
                        <strong>Summary:</strong> Will generate {numCopies} PDF copies with {rules.length} text replacement(s)
                    </p>
                </div>
            </Card>

            <Button
                onClick={handleGenerate}
                disabled={generating || rules.length === 0}
                className="w-full"
                size="lg"
            >
                {generating ? `Generating... ${progress}%` : `Generate ${numCopies} PDF Copies`}
            </Button>

            {generating && (
                <div className="space-y-2">
                    <Progress value={progress} />
                    <p className="text-sm text-muted-foreground text-center">
                        Processing PDFs...
                    </p>
                </div>
            )}
        </div>
    )
}

