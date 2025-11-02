import React from 'react';
import Button from '../../components/atoms/Button';

export function Hero({ onPrimary }: { onPrimary?: () => void }) {
	return (
		<section className="relative overflow-hidden rounded-2xl border border-white/10 bg-ink p-8 sm:p-12">
			<div className="absolute inset-0 u-aurora animate-aurora" aria-hidden />
			<div className="relative z-10 max-w-3xl">
				<h1 className="text-4xl sm:text-6xl font-semibold tracking-tight">
					Understand every change at a glance.
				</h1>
				<p className="mt-4 text-white/80 text-lg">
					Upload two documents. Get precise, readable redlines in seconds.
				</p>
				<div className="mt-6 flex gap-3">
					<Button size="lg" onClick={onPrimary}>Try the Workspace</Button>
					<Button variant="secondary" size="lg" onClick={onPrimary}>Compare your docs</Button>
				</div>
			</div>
		</section>
	);
}

export default Hero;


