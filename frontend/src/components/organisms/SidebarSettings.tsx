import React from 'react';
import SettingRow from '../molecules/SettingRow';

export interface SidebarSettingsProps {
	includeFormatting: boolean;
	setIncludeFormatting: (v: boolean) => void;
	ocr: boolean;
	setOcr: (v: boolean) => void;
}

export function SidebarSettings({ includeFormatting, setIncludeFormatting, ocr, setOcr }: SidebarSettingsProps) {
	return (
		<aside className="space-y-3">
			<SettingRow
				label="Include formatting differences"
				description="Track style changes like bold, italics, and headings."
				checked={includeFormatting}
				onChange={setIncludeFormatting}
			/>
			<SettingRow
				label="OCR for scanned PDFs"
				description="Extract text from scanned documents before comparison."
				checked={ocr}
				onChange={setOcr}
			/>
		</aside>
	);
}

export default SidebarSettings;


