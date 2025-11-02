import React from 'react';

export interface ToggleProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'onChange'> {
	checked: boolean;
	onChange: (checked: boolean) => void;
	label?: string;
}

export function Toggle({ checked, onChange, label, className = '', ...props }: ToggleProps) {
	return (
		<button
			role="switch"
			aria-checked={checked}
			onClick={() => onChange(!checked)}
			className={`inline-flex items-center gap-3 group ${className}`}
			{...props}
		>
			<span
				className={`relative h-6 w-11 rounded-full border transition-colors ${
					checked ? 'bg-[image:var(--grad-accent)] border-white/10 shadow-glow' : 'bg-white/10 border-white/10'
				}`}
			>
				<span
					className={`absolute top-1/2 -translate-y-1/2 transition-transform h-4 w-4 rounded-full bg-white shadow-sm ${
						checked ? 'translate-x-[22px]' : 'translate-x-[6px]'
					}`}
				/>
			</span>
			{label && <span className="text-sm text-white/80 select-none">{label}</span>}
		</button>
	);
}

export default Toggle;


