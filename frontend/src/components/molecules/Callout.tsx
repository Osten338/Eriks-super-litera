import React from 'react';

type CalloutVariant = 'info' | 'success' | 'warning' | 'danger';

export interface CalloutProps extends React.HTMLAttributes<HTMLDivElement> {
	variant?: CalloutVariant;
	title?: string;
}

const variantStyle: Record<CalloutVariant, string> = {
	info: 'border-sky-400/25 bg-sky-400/10 text-sky-200',
	success: 'border-emerald-400/25 bg-emerald-400/10 text-emerald-200',
	warning: 'border-amber-400/25 bg-amber-400/10 text-amber-200',
	danger: 'border-red-400/25 bg-red-400/10 text-red-200',
};

export function Callout({ variant = 'info', title, className = '', children, ...props }: CalloutProps) {
	return (
		<div className={`rounded-xl border p-3 ${variantStyle[variant]} ${className}`} {...props}>
			{title && <div className="mb-1 text-sm font-medium">{title}</div>}
			<div className="text-sm text-white/85">{children}</div>
		</div>
	);
}

export default Callout;


