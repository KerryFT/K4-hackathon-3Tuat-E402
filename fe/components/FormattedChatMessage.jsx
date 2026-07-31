'use client';

export default function FormattedChatMessage({ content, isUser = false }) {
  if (!content) return null;

  if (isUser) {
    return <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>;
  }

  // Pre-process inline bullet points or continuous text from LLM outputs
  let formattedContent = content
    .replace(/(?<!\n)\s+(\d+\.\s+\*\*)/g, '\n\n$1')
    .replace(/(?<!\n)\s+-\s+/g, '\n- ');

  const lines = formattedContent.split('\n');

  return (
    <div className="space-y-2 text-sm leading-relaxed">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return null;

        // Heading (### Heading or ## Heading)
        if (trimmed.startsWith('#')) {
          const text = trimmed.replace(/^#+\s*/, '');
          return (
            <h4 key={idx} className="font-bold text-[#0B3B60] dark:text-[#38BDF8] text-sm mt-2 mb-1 border-b border-slate-200/60 dark:border-slate-700/60 pb-1">
              {text}
            </h4>
          );
        }

        // Bullet point (- or • or * or 1., 2.)
        const bulletMatch = trimmed.match(/^(?:[•\-\*]|\d+\.)\s+(.*)/);
        if (bulletMatch) {
          const rawBulletText = bulletMatch[1];
          return (
            <div key={idx} className="flex items-start gap-2.5 pl-1 my-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#1565A8] dark:bg-sky-400 mt-2 flex-shrink-0" />
              <div className="flex-1 text-slate-700 dark:text-slate-200">
                {parseBoldText(rawBulletText)}
              </div>
            </div>
          );
        }

        return (
          <p key={idx} className="text-slate-700 dark:text-slate-200">
            {parseBoldText(trimmed)}
          </p>
        );
      })}
    </div>
  );
}

function parseBoldText(str) {
  if (!str) return '';
  const parts = str.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="font-bold text-slate-900 dark:text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}
