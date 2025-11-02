import React from 'react';

export interface TooltipProps {
	content: React.ReactNode;
	children: React.ReactElement;
}

export function Tooltip({ content, children }: TooltipProps) {
	const [open, setOpen] = React.useState(false);
	const id = React.useId();
	return (
		<span
			className="relative inline-flex group"
			onMouseEnter={() => setOpen(true)}
			onMouseLeave={() => setOpen(false)}
			onFocus={() => setOpen(true)}
			onBlur={() => setOpen(false)}
		>
			{React.cloneElement(children, {
				'aria-describedby': open ? id : undefined,
				className: `${children.props.className || ''}`,
			})}
			{open && (
				<span
					id={id}
					role="tooltip"
					className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 whitespace-nowrap rounded-xl bg-surface/90 border border-white/10 px-3 py-1.5 text-xs text-white/90 shadow-glow"
				>
					{content}
				</span>
			)}
		</span>
	);
}

export default Tooltip;


