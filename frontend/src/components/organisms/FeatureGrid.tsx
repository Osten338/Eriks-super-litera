import React from 'react';

export interface FeatureItem {
	icon?: React.ReactNode;
	title: string;
	description: string;
}

export function FeatureGrid({ items }: { items: FeatureItem[] }) {
	return (
		<section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
			{items.map((it, i) => (
				<div key={i} className="group rounded-2xl border border-white/10 bg-surface/60 p-5 transition-transform hover:-translate-y-0.5">
					<div className="h-10 w-10 rounded-lg bg-[image:var(--grad-accent)] shadow-glow mb-3" aria-hidden />
					<h3 className="text-lg font-medium">{it.title}</h3>
					<p className="mt-1 text-sm text-white/70">{it.description}</p>
				</div>
			))}
		</section>
	);
	}

export default FeatureGrid;


