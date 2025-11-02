import React from 'react';
import Button from '../atoms/Button';

export interface ExportPanelProps {
	onExportPdf: () => void;
	onExportDocx: () => void;
	disabled?: boolean;
}

export function ExportPanel({ onExportPdf, onExportDocx, disabled }: ExportPanelProps) {
	return (
		<div className="glass p-4 sticky top-4">
			<div className="text-sm text-white/70 mb-3">Export</div>
			<div className="flex flex-col gap-2">
				<Button variant="secondary" onClick={onExportPdf} disabled={disabled}>Export PDF</Button>
				<Button variant="secondary" onClick={onExportDocx} disabled={disabled}>Export Word</Button>
			</div>
		</div>
	);
}

export default ExportPanel;


