import React from 'react';
import type { Stats } from '../../api/types';

export interface StatProps {
	label: string;
	value: number | string;
	subtle?: string;
}

export function StatCard({ label, value, subtle }: StatProps) {
	return (
		<div className="rounded-xl border border-white/10 bg-white/5 p-4">
			<div className="text-xs text-white/60">{label}</div>
			<div className="mt-1 text-2xl font-semibold">{value}</div>
			{subtle && <div className="mt-1 text-xs text-white/50">{subtle}</div>}
		</div>
	);
}

export function DiffStats({ stats }: { stats: Stats }) {
	return (
		<div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
			<StatCard label="Insertions" value={stats.insertions} subtle="added" />
			<StatCard label="Deletions" value={stats.deletions} subtle="removed" />
			<StatCard label="Moves" value={stats.moves} subtle="repositioned" />
			<StatCard label="Total" value={stats.total} subtle="changes" />
		</div>
	);
}

export default StatCard;


