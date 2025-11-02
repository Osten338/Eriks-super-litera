import React from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
	variant?: ButtonVariant;
	size?: ButtonSize;
	loading?: boolean;
}

const baseClasses =
	'inline-flex items-center justify-center rounded-xl font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-0 focus-visible:ring-[#79FFA8] disabled:opacity-50 disabled:cursor-not-allowed';

const sizeClasses: Record<ButtonSize, string> = {
	sm: 'h-9 px-3 text-sm gap-2',
	md: 'h-11 px-4 text-sm gap-2',
	lg: 'h-12 px-5 text-base gap-3',
};

const variantClasses: Record<ButtonVariant, string> = {
	primary:
		'bg-[image:var(--grad-primary)] text-white shadow-glow hover:shadow-[var(--ring-glow)] hover:opacity-[.98] active:opacity-95',
	secondary:
		'bg-surface/80 text-white/90 border border-white/10 hover:bg-surface hover:text-white',
	ghost:
		'bg-transparent text-white/80 hover:text-white hover:bg-white/5',
};

export function Button({
	variant = 'primary',
	size = 'md',
	loading = false,
	className = '',
	disabled,
	children,
	...props
}: ButtonProps) {
	return (
		<button
			className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
			disabled={disabled || loading}
			{...props}
		>
			{loading && (
				<span
					className="mr-2 h-4 w-4 rounded-full bg-gradient-to-r from-white/10 via-white/60 to-white/10 animate-shimmer bg-[length:200%_100%]"
					aria-hidden
				/>
			)}
			{children}
		</button>
	);
}

export default Button;


