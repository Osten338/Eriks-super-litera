import React from 'react';

type TagVariant = 'default' | 'success' | 'warning' | 'danger' | 'info';

export interface TagProps extends React.HTMLAttributes<HTMLSpanElement> {
	variant?: TagVariant;
	startIcon?: React.ReactNode;
	endIcon?: React.ReactNode;
}

const styles: Record<TagVariant, string> = {
	default: 'bg-white/10 text-white/80 border-white/10',
	success: 'bg-emerald-400/15 text-emerald-300 border-emerald-400/20',
	warning: 'bg-amber-400/15 text-amber-300 border-amber-400/20',
	danger: 'bg-red-400/15 text-red-300 border-red-400/20',
	info: 'bg-sky-400/15 text-sky-300 border-sky-400/20',
};

export function Tag({ variant = 'default', startIcon, endIcon, className = '', children, ...props }: TagProps) {
	return (
		<span
			className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs ${styles[variant]} ${className}`}
			{...props}
		>
			{startIcon && <span className="opacity-80" aria-hidden>{startIcon}</span>}
			{children}
			{endIcon && <span className="opacity-80" aria-hidden>{endIcon}</span>}
		</span>
	);
}

export default Tag;


