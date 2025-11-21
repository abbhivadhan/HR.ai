'use client';

import { useState } from 'react';
import { Resume, ResumeContent } from '@/types/resume';
import { 
  DocumentArrowDownIcon, 
  SparklesIcon 
} from '@heroicons/react/24/outline';

interface ResumeEditorProps {
  resume: Resume;
  onSave: (content: ResumeContent) => void;
  onGetSuggestions: (section: string) => void;
  onExport: (format: 'pdf' | 'docx') => void;
}

export function ResumeEditor({ resume, onSave, onGetSuggestions, onExport }: ResumeEditorProps) {
  const [content, setContent] = useState<ResumeContent>(resume.content);
  const [activeSection, setActiveSection] = useState('summary');

  const sections = [
    { id: 'summary', label: 'Summary' },
    { id: 'experience', label: 'Experience' },
    { id: 'education', label: 'Education' },
    { id: 'skills', label: 'Skills' },
  ];

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      {/* Editor */}
      <div className="lg:col-span-2 space-y-4">
        <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`px-4 py-2 font-medium transition-colors ${
                activeSection === section.id
                  ? 'text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              {section.label}
            </button>
          ))}
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg">
          <textarea
            value={JSON.stringify(content[activeSection as keyof ResumeContent], null, 2)}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value);
                setContent({ ...content, [activeSection]: parsed });
              } catch {}
            }}
            className="w-full h-96 p-4 border rounded-lg font-mono text-sm"
          />
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => onSave(content)}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg"
          >
            <DocumentArrowDownIcon className="w-4 h-4" />
            Save
          </button>
          <button
            onClick={() => onGetSuggestions(activeSection)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg"
          >
            <SparklesIcon className="w-4 h-4" />
            Get AI Suggestions
          </button>
        </div>
      </div>

      {/* Preview */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg">
        <h3 className="font-bold mb-4">Preview</h3>
        <div className="space-y-4 text-sm">
          <div>
            <h4 className="font-semibold">Summary</h4>
            <p className="text-gray-600">{content.summary}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
