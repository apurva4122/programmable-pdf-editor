'use client'

import { TextSection } from '../page'
import { Card } from '@/components/ui/card'
import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TextSectionSelectorProps {
    sections: TextSection[]
    selectedSections: TextSection[]
    onSelect: (section: TextSection) => void
    onDeselect: (sectionId: string) => void
}

export default function TextSectionSelector({
    sections,
    selectedSections,
    onSelect,
    onDeselect
}: TextSectionSelectorProps) {
    const isSelected = (sectionId: string) => {
        return selectedSections.some(s => s.id === sectionId)
    }

    return (
        <div className="space-y-4">
            <p className="text-muted-foreground mb-4">
                Found {sections.length} text sections. Select the ones you want to edit:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
                {sections.map((section) => {
                    const selected = isSelected(section.id)
                    return (
                        <Card
                            key={section.id}
                            onClick={() => selected ? onDeselect(section.id) : onSelect(section)}
                            className={cn(
                                "p-4 cursor-pointer transition-all hover:shadow-md",
                                selected && "border-primary bg-primary/5"
                            )}
                        >
                            <div className="flex items-start justify-between mb-2">
                                <span className="text-xs text-muted-foreground">Page {section.page + 1}</span>
                                {selected && (
                                    <span className="text-primary font-semibold flex items-center gap-1">
                                        <Check className="w-4 h-4" /> Selected
                                    </span>
                                )}
                            </div>
                            <p className="text-sm font-medium break-words">
                                {section.text}
                            </p>
                            <p className="text-xs text-muted-foreground mt-2">
                                Position: ({Math.round(section.x)}, {Math.round(section.y)})
                            </p>
                        </Card>
                    )
                })}
            </div>

            {selectedSections.length > 0 && (
                <Card className="bg-primary/5 border-primary/20">
                    <div className="p-4">
                        <p className="text-primary font-medium">
                            {selectedSections.length} section(s) selected for editing
                        </p>
                    </div>
                </Card>
            )}
        </div>
    )
}

