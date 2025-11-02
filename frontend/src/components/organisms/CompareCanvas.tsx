import React from 'react';
import DOMPurify from 'dompurify';

export interface CompareCanvasProps {
	paragraphs: { html: string }[];
}

export function CompareCanvas({ paragraphs }: CompareCanvasProps) {
	return (
		<div className="rounded-xl border border-white/10 bg-white/5 p-4 max-h-[70vh] overflow-auto">
			<div className="space-y-2">
				{paragraphs.map((p, i) => (
					<div key={i} className="text-sm" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(p.html) }} />
				))}
			</div>
		</div>
	);
}

export default CompareCanvas;


