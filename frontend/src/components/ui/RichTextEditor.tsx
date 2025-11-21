'use client'

import React from 'react'
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { motion } from 'framer-motion'
import {
  BoldIcon,
  ItalicIcon,
  ListBulletIcon,
  NumberedListIcon,
  CodeBracketIcon,
} from '@heroicons/react/24/outline'

interface RichTextEditorProps {
  content: string
  onChange: (content: string) => void
  placeholder?: string
  className?: string
  disabled?: boolean
}

export default function RichTextEditor({
  content,
  onChange,
  placeholder = 'Start typing...',
  className = '',
  disabled = false
}: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder,
      }),
    ],
    content,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
    editable: !disabled,
  })

  if (!editor) {
    return null
  }

  const ToolbarButton = ({ 
    onClick, 
    isActive, 
    children, 
    title 
  }: { 
    onClick: () => void
    isActive: boolean
    children: React.ReactNode
    title: string
  }) => (
    <motion.button
      type="button"
      onClick={onClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={`p-2 rounded-md transition-colors ${
        isActive
          ? 'bg-primary-100 text-primary-700'
          : 'text-gray-600 hover:bg-gray-100'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      disabled={disabled}
      title={title}
    >
      {children}
    </motion.button>
  )

  return (
    <div className={`border border-gray-300 rounded-lg overflow-hidden ${className}`}>
      {/* Toolbar */}
      <div className="flex items-center gap-1 p-2 border-b border-gray-200 bg-gray-50">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBold().run()}
          isActive={editor.isActive('bold')}
          title="Bold"
        >
          <BoldIcon className="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleItalic().run()}
          isActive={editor.isActive('italic')}
          title="Italic"
        >
          <ItalicIcon className="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleCode().run()}
          isActive={editor.isActive('code')}
          title="Inline Code"
        >
          <CodeBracketIcon className="h-4 w-4" />
        </ToolbarButton>
        
        <div className="w-px h-6 bg-gray-300 mx-1" />
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          isActive={editor.isActive('bulletList')}
          title="Bullet List"
        >
          <ListBulletIcon className="h-4 w-4" />
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          isActive={editor.isActive('orderedList')}
          title="Numbered List"
        >
          <NumberedListIcon className="h-4 w-4" />
        </ToolbarButton>
        
        <div className="w-px h-6 bg-gray-300 mx-1" />
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          isActive={editor.isActive('heading', { level: 2 })}
          title="Heading 2"
        >
          <span className="text-sm font-semibold">H2</span>
        </ToolbarButton>
        
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          isActive={editor.isActive('heading', { level: 3 })}
          title="Heading 3"
        >
          <span className="text-sm font-semibold">H3</span>
        </ToolbarButton>
      </div>
      
      {/* Editor Content */}
      <div className="min-h-[200px] p-4">
        <EditorContent 
          editor={editor} 
          className={`prose prose-sm max-w-none focus:outline-none ${
            disabled ? 'opacity-50' : ''
          }`}
        />
      </div>
    </div>
  )
}