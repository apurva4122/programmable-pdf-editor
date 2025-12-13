'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import PDFUploader from './components/PDFUploader'
import TextSectionSelector from './components/TextSectionSelector'
import RuleConfigurator from './components/RuleConfigurator'
import PDFGenerator from './components/PDFGenerator'

export interface TextSection {
    id: string
    text: string
    x: number
    y: number
    width: number
    height: number
    page: number
}

export interface ReplacementRule {
    section_id: string
    original_text: string
    type: 'serial' | 'random' | 'custom'
    start_value?: number
    random_min?: number
    random_max?: number
    prefix?: string
    suffix?: string
    format?: string
}

export default function Home() {
    const [pdfId, setPdfId] = useState<string | null>(null)
    const [sections, setSections] = useState<TextSection[]>([])
    const [selectedSections, setSelectedSections] = useState<TextSection[]>([])
    const [rules, setRules] = useState<ReplacementRule[]>([])
    const [numCopies, setNumCopies] = useState(10)

    const handlePDFUploaded = (id: string) => {
        setPdfId(id)
        setSections([])
        setSelectedSections([])
        setRules([])
    }

    const handleSectionsDetected = (detectedSections: TextSection[]) => {
        setSections(detectedSections)
    }

    const handleSectionSelected = (section: TextSection) => {
        if (!selectedSections.find(s => s.id === section.id)) {
            setSelectedSections([...selectedSections, section])
            // Add default rule for this section
            setRules([...rules, {
                section_id: section.id,
                original_text: section.text,
                type: 'serial',
                start_value: 1,
                prefix: '',
                suffix: ''
            }])
        }
    }

    const handleSectionDeselected = (sectionId: string) => {
        setSelectedSections(selectedSections.filter(s => s.id !== sectionId))
        setRules(rules.filter(r => r.section_id !== sectionId))
    }

    const handleRuleUpdate = (sectionId: string, updatedRule: ReplacementRule) => {
        setRules(rules.map(r => r.section_id === sectionId ? updatedRule : r))
    }

    return (
        <main className="min-h-screen p-8 bg-background">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-4xl font-bold mb-8 text-foreground">
                    Programmable PDF Editor
                </h1>

                <div className="space-y-8">
                    {/* Step 1: Upload PDF */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Step 1: Upload PDF</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <PDFUploader
                                onUploaded={handlePDFUploaded}
                                onSectionsDetected={handleSectionsDetected}
                            />
                        </CardContent>
                    </Card>

                    {/* Step 2: Select Text Sections */}
                    {sections.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Step 2: Select Text Sections to Edit</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <TextSectionSelector
                                    sections={sections}
                                    selectedSections={selectedSections}
                                    onSelect={handleSectionSelected}
                                    onDeselect={handleSectionDeselected}
                                />
                            </CardContent>
                        </Card>
                    )}

                    {/* Step 3: Configure Rules */}
                    {selectedSections.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Step 3: Configure Replacement Rules</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <RuleConfigurator
                                    selectedSections={selectedSections}
                                    rules={rules}
                                    onRuleUpdate={handleRuleUpdate}
                                />
                            </CardContent>
                        </Card>
                    )}

                    {/* Step 4: Generate PDFs */}
                    {rules.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Step 4: Generate PDF Copies</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <PDFGenerator
                                    pdfId={pdfId!}
                                    rules={rules}
                                    numCopies={numCopies}
                                    onNumCopiesChange={setNumCopies}
                                />
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>
        </main>
    )
}

