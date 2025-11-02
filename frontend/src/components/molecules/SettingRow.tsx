import React from 'react';
import Toggle from '../atoms/Toggle';

export interface SettingRowProps {
	label: string;
	description?: string;
	checked: boolean;
	onChange: (checked: boolean) => void;
}

export function SettingRow({ label, description, checked, onChange }: SettingRowProps) {
	return (
		<div className="flex items-start justify-between gap-4 rounded-xl border border-white/10 bg-white/5 p-3">
			<div>
				<div className="text-sm">{label}</div>
				{description && <div className="text-xs text-white/60">{description}</div>}
			</div>
			<Toggle checked={checked} onChange={onChange} />
		</div>
	);
}

export default SettingRow;


