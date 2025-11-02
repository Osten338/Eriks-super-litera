import React from 'react';

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
	value?: number; // 0-100; if undefined -> indeterminate
	label?: string;
}

export function Progress({ value, label, className = '', ...props }: ProgressProps) {
	const isIndeterminate = typeof value !== 'number';
	const clamped = isIndeterminate ? 0 : Math.max(0, Math.min(100, value));
	return (
		<div className={`w-full ${className}`} {...props}>
			{label && (
				<div className="mb-1 flex items-center justify-between text-xs text-white/70">
					<span>{label}</span>
					{!isIndeterminate && <span>{clamped}%</span>}
				</div>
			)}
			<div className="h-2 w-full overflow-hidden rounded-full bg-white/10">
				{isIndeterminate ? (
					<div className="h-full w-1/3 animate-shimmer bg-[image:var(--grad-accent)] bg-[length:200%_100%]" />
				) : (
					<div
						className="h-full bg-[image:var(--grad-accent)] shadow-glow"
						style={{ width: `${clamped}%` }}
					/>
				)}
			</div>
		</div>
	);
}

export default Progress;


