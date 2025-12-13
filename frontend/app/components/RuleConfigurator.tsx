'use client'

import { useState, useEffect } from 'react'
import { TextSection, ReplacementRule } from '../page'
import { Card } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'

interface RuleConfiguratorProps {
    selectedSections: TextSection[]
    rules: ReplacementRule[]
    onRuleUpdate: (sectionId: string, rule: ReplacementRule) => void
}

export default function RuleConfigurator({
    selectedSections,
    rules,
    onRuleUpdate
}: RuleConfiguratorProps) {
    const getRuleForSection = (sectionId: string): ReplacementRule => {
        return rules.find(r => r.section_id === sectionId) || {
            section_id: sectionId,
            original_text: selectedSections.find(s => s.id === sectionId)?.text || '',
            type: 'serial',
            start_value: 1,
            prefix: '',
            suffix: ''
        }
    }

    return (
        <div className="space-y-6">
            {selectedSections.map((section) => {
                const rule = getRuleForSection(section.id)
                return (
                    <Card key={section.id} className="p-6">
                        <h3 className="text-lg font-semibold mb-4">
                            Section: <span className="font-normal text-muted-foreground">"{section.text}"</span>
                        </h3>

                        <div className="space-y-4">
                            {/* Replacement Type */}
                            <div className="space-y-2">
                                <Label>Replacement Type</Label>
                                <Select
                                    value={rule.type}
                                    onValueChange={(value) => {
                                        onRuleUpdate(section.id, {
                                            ...rule,
                                            type: value as 'serial' | 'random' | 'custom'
                                        })
                                    }}
                                >
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="serial">Serial Number</SelectItem>
                                        <SelectItem value="random">Random Number</SelectItem>
                                        <SelectItem value="custom">Custom</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            {/* Serial Number Options */}
                            {rule.type === 'serial' && (
                                <div className="space-y-2">
                                    <Label>Start Value</Label>
                                    <Input
                                        type="number"
                                        value={rule.start_value || 1}
                                        onChange={(e) => {
                                            onRuleUpdate(section.id, {
                                                ...rule,
                                                start_value: parseInt(e.target.value) || 1
                                            })
                                        }}
                                    />
                                </div>
                            )}

                            {/* Random Number Options */}
                            {rule.type === 'random' && (
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label>Min Value</Label>
                                        <Input
                                            type="number"
                                            value={rule.random_min || 1}
                                            onChange={(e) => {
                                                onRuleUpdate(section.id, {
                                                    ...rule,
                                                    random_min: parseInt(e.target.value) || 1
                                                })
                                            }}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Max Value</Label>
                                        <Input
                                            type="number"
                                            value={rule.random_max || 100}
                                            onChange={(e) => {
                                                onRuleUpdate(section.id, {
                                                    ...rule,
                                                    random_max: parseInt(e.target.value) || 100
                                                })
                                            }}
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Format Options */}
                            <div className="space-y-2">
                                <Label>Number Format (e.g., %04d for 0001, %d for 1)</Label>
                                <Input
                                    type="text"
                                    value={rule.format || ''}
                                    onChange={(e) => {
                                        onRuleUpdate(section.id, {
                                            ...rule,
                                            format: e.target.value || undefined
                                        })
                                    }}
                                    placeholder="%04d"
                                />
                                <p className="text-xs text-muted-foreground">
                                    Leave empty for default formatting
                                </p>
                            </div>

                            {/* Prefix and Suffix */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Prefix</Label>
                                    <Input
                                        type="text"
                                        value={rule.prefix || ''}
                                        onChange={(e) => {
                                            onRuleUpdate(section.id, {
                                                ...rule,
                                                prefix: e.target.value
                                            })
                                        }}
                                        placeholder="INV-"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label>Suffix</Label>
                                    <Input
                                        type="text"
                                        value={rule.suffix || ''}
                                        onChange={(e) => {
                                            onRuleUpdate(section.id, {
                                                ...rule,
                                                suffix: e.target.value
                                            })
                                        }}
                                        placeholder="-2024"
                                    />
                                </div>
                            </div>

                            {/* Preview */}
                            <Card className="bg-muted p-4">
                                <p className="text-sm font-medium mb-2">Preview:</p>
                                <p className="text-lg font-mono">
                                    {rule.prefix || ''}
                                    {rule.type === 'serial'
                                        ? (rule.format ? rule.format.replace('%d', String(rule.start_value || 1)) : String(rule.start_value || 1))
                                        : rule.type === 'random'
                                            ? (rule.format ? rule.format.replace('%d', String(rule.random_min || 1)) : String(rule.random_min || 1))
                                            : '1'}
                                    {rule.suffix || ''}
                                </p>
                            </Card>
                        </div>
                    </Card>
                )
            })}
        </div>
    )
}

