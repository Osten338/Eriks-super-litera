import React from 'react';
import Tag from '../atoms/Tag';
import Button from '../atoms/Button';

export interface FileRowProps {
	file: File;
	status?: 'idle' | 'uploading' | 'ready' | 'error';
	onRemove?: () => void;
}

function formatBytes(bytes: number) {
	if (!bytes) return '0 B';
	const sizes = ['B', 'KB', 'MB', 'GB'];
	const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), sizes.length - 1);
	const value = bytes / Math.pow(1024, i);
	return `${value.toFixed(value >= 10 || i === 0 ? 0 : 1)} ${sizes[i]}`;
}

export function FileRow({ file, status = 'idle', onRemove }: FileRowProps) {
	return (
		<div className="flex items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/5 px-3 py-2">
			<div className="min-w-0">
				<div className="truncate text-sm">{file.name}</div>
				<div className="text-xs text-white/60">{formatBytes(file.size)}</div>
			</div>
			<div className="flex items-center gap-2">
				{status === 'uploading' && <Tag variant="info">Uploading</Tag>}
				{status === 'ready' && <Tag variant="success">Ready</Tag>}
				{status === 'error' && <Tag variant="danger">Error</Tag>}
				{onRemove && (
					<Button variant="ghost" size="sm" onClick={onRemove} aria-label={`Remove ${file.name}`}>
						Remove
					</Button>
				)}
			</div>
		</div>
	);
}

export default FileRow;


