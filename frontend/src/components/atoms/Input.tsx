import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
	label?: string;
	helpText?: string;
	error?: string;
	leftIcon?: React.ReactNode;
	rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
	({ label, helpText, error, leftIcon, rightIcon, className = '', id, ...props }, ref) => {
		const inputId = id || React.useId();
		const describedByIds: string[] = [];
		if (helpText) describedByIds.push(`${inputId}-help`);
		if (error) describedByIds.push(`${inputId}-error`);

		return (
			<label htmlFor={inputId} className="block text-sm text-white/80">
				{label && <span className="mb-1 block">{label}</span>}
				<div className={`relative flex items-center`}> 
					{leftIcon && <span className="absolute left-3 text-white/50" aria-hidden>{leftIcon}</span>}
					<input
						id={inputId}
						ref={ref}
						className={`w-full h-11 rounded-xl bg-surface/80 border border-white/10 text-white placeholder-white/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#79FFA8] focus:border-white/20 ${leftIcon ? 'pl-10' : 'pl-4'} ${rightIcon ? 'pr-10' : 'pr-4'} ${className}`}
						aria-invalid={!!error}
						aria-describedby={describedByIds.join(' ') || undefined}
						{...props}
					/>
					{rightIcon && <span className="absolute right-3 text-white/50" aria-hidden>{rightIcon}</span>}
				</div>
				{helpText && !error && (
					<p id={`${inputId}-help`} className="mt-1 text-xs text-white/50">{helpText}</p>
				)}
				{error && (
					<p id={`${inputId}-error`} className="mt-1 text-xs text-red-400">{error}</p>
				)}
			</label>
		);
	}
);

Input.displayName = 'Input';

export default Input;


