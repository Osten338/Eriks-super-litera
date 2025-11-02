import React from 'react';
import Button from '../atoms/Button';
import Tag from '../atoms/Tag';

export type UploadStatus = 'idle' | 'ready' | 'error';

export interface UploadCardProps {
	label: string;
	accept?: string;
	file?: File | null;
	status?: UploadStatus;
	error?: string;
	onFileSelect: (file: File | null) => void;
}

export function UploadCard({ label, accept = '.docx,.pdf', file, status = 'idle', error, onFileSelect }: UploadCardProps) {
	const inputRef = React.useRef<HTMLInputElement>(null);
	const onPick = () => inputRef.current?.click();

	const onDrop: React.DragEventHandler<HTMLDivElement> = (e) => {
		e.preventDefault();
		const f = e.dataTransfer.files?.[0];
		if (f) onFileSelect(f);
	};

	const onChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
		onFileSelect(e.target.files?.[0] || null);
	};

	return (
		<div
			onDragOver={(e) => e.preventDefault()}
			onDrop={onDrop}
			className="glass p-4 sm:p-5 flex items-center justify-between gap-4"
		>
			<div className="flex min-w-0 items-center gap-3">
				<div className="h-10 w-10 rounded-lg bg-[image:var(--grad-primary)] shadow-glow" aria-hidden />
				<div className="min-w-0">
					<div className="text-sm text-white/80">{label}</div>
					<div className="text-sm truncate">
						{file ? file.name : <span className="text-white/50">Drop file here or browse</span>}
					</div>
				</div>
			</div>
			<div className="flex items-center gap-3">
				{status === 'ready' && <Tag variant="success">Ready</Tag>}
				{status === 'error' && <Tag variant="danger">Error</Tag>}
				<Button variant="secondary" size="sm" onClick={onPick}>Browse</Button>
				<input ref={inputRef} type="file" accept={accept} className="sr-only" onChange={onChange} />
			</div>
			{error && <div className="mt-2 text-xs text-red-400">{error}</div>}
		</div>
	);
}

export default UploadCard;


