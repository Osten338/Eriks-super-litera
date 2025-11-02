import React from 'react';
import Button from '../../components/atoms/Button';

export interface CompareHeaderProps {
	onCompare: () => void;
	onExportPdf: () => void;
	onExportDocx: () => void;
	disabled?: boolean;
}

export function CompareHeader({ onCompare, onExportPdf, onExportDocx, disabled }: CompareHeaderProps) {
	return (
		<header className="sticky top-0 z-20 glass p-3 flex items-center justify-between">
			<div className="text-sm text-white/70">Redline Preview</div>
			<div className="flex gap-2">
				<Button onClick={onCompare} disabled={disabled}>Compare</Button>
				<Button variant="secondary" onClick={onExportPdf} disabled={disabled}>Export PDF</Button>
				<Button variant="secondary" onClick={onExportDocx} disabled={disabled}>Export Word</Button>
			</div>
		</header>
	);
}

export default CompareHeader;


