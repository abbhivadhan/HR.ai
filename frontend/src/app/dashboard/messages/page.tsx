'use client'

import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import {
  MagnifyingGlassIcon,
  PaperAirplaneIcon,
  PaperClipIcon,
  EllipsisVerticalIcon,
  PhoneIcon,
  VideoCameraIcon
} from '@heroicons/react/24/outline'

interface Message {
  id: string
  senderId: string
  text: string
  timestamp: Date
  read: boolean
}

interface Conversation {
  id: string
  name: string
  avatar?: string
  lastMessage: string
  lastMessageTime: Date
  unreadCount: number
  online: boolean
}

export default function MessagesPage() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadConversations()
  }, [])

  useEffect(() => {
    if (selectedConversation) {
      loadMessages(selectedConversation)
    }
  }, [selectedConversation])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadConversations = () => {
    setConversations([
      {
        id: '1',
        name: 'Sarah Johnson',
        lastMessage: 'Thanks for considering my application!',
        lastMessageTime: new Date(Date.now() - 300000),
        unreadCount: 2,
        online: true
      },
      {
        id: '2',
        name: 'TechCorp Recruiting',
        lastMessage: 'We would like to schedule an interview',
        lastMessageTime: new Date(Date.now() - 3600000),
        unreadCount: 0,
        online: false
      },
      {
        id: '3',
        name: 'Michael Chen',
        lastMessage: 'Looking forward to hearing from you',
        lastMessageTime: new Date(Date.now() - 86400000),
        unreadCount: 0,
        online: true
      }
    ])
  }

  const loadMessages = (conversationId: string) => {
    setMessages([
      {
        id: '1',
        senderId: conversationId,
        text: 'Hi! I saw your profile and I think you would be a great fit for our team.',
        timestamp: new Date(Date.now() - 7200000),
        read: true
      },
      {
        id: '2',
        senderId: 'me',
        text: 'Thank you! I\'m very interested in learning more about the position.',
        timestamp: new Date(Date.now() - 7000000),
        read: true
      },
      {
        id: '3',
        senderId: conversationId,
        text: 'Great! Would you be available for a call this week?',
        timestamp: new Date(Date.now() - 6800000),
        read: true
      },
      {
        id: '4',
        senderId: 'me',
        text: 'Yes, I\'m available Thursday or Friday afternoon.',
        timestamp: new Date(Date.now() - 6600000),
        read: true
      }
    ])
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = () => {
    if (!newMessage.trim() || !selectedConversation) return

    const message: Message = {
      id: Date.now().toString(),
      senderId: 'me',
      text: newMessage,
      timestamp: new Date(),
      read: false
    }

    setMessages([...messages, message])
    setNewMessage('')
  }

  const selectedConv = conversations.find(c => c.id === selectedConversation)

  return (
    <div className="h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Conversations List */}
      <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Messages</h1>
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => setSelectedConversation(conv.id)}
              className={`w-full p-4 flex items-center space-x-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                selectedConversation === conv.id ? 'bg-blue-50 dark:bg-blue-900/20' : ''
              }`}
            >
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                  {conv.name.split(' ').map(n => n[0]).join('')}
                </div>
                {conv.online && (
                  <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white dark:border-gray-800 rounded-full"></div>
                )}
              </div>
              <div className="flex-1 text-left">
                <div className="flex justify-between items-start">
                  <h3 className="font-semibold text-gray-900 dark:text-white">{conv.name}</h3>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {conv.lastMessageTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 truncate">{conv.lastMessage}</p>
                  {conv.unreadCount > 0 && (
                    <span className="ml-2 px-2 py-0.5 bg-blue-600 text-white text-xs rounded-full">
                      {conv.unreadCount}
                    </span>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      {selectedConversation ? (
        <div className="flex-1 flex flex-col">
          {/* Chat Header */}
          <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                  {selectedConv?.name.split(' ').map(n => n[0]).join('')}
                </div>
                {selectedConv?.online && (
                  <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white dark:border-gray-800 rounded-full"></div>
                )}
              </div>
              <div>
                <h2 className="font-semibold text-gray-900 dark:text-white">{selectedConv?.name}</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {selectedConv?.online ? 'Online' : 'Offline'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                <PhoneIcon className="w-5 h-5" />
              </button>
              <button className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                <VideoCameraIcon className="w-5 h-5" />
              </button>
              <button className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                <EllipsisVerticalIcon className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${message.senderId === 'me' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-md px-4 py-2 rounded-2xl ${
                    message.senderId === 'me'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
                  }`}
                >
                  <p>{message.text}</p>
                  <p className={`text-xs mt-1 ${
                    message.senderId === 'me' ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </motion.div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center space-x-2">
              <button className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                <PaperClipIcon className="w-5 h-5" />
              </button>
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type a message..."
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              <button
                onClick={handleSendMessage}
                className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <PaperAirplaneIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
          <div className="text-center">
            <div className="w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No conversation selected</h3>
            <p className="text-gray-600 dark:text-gray-400">Choose a conversation to start messaging</p>
          </div>
        </div>
      )}
    </div>
  )
}
