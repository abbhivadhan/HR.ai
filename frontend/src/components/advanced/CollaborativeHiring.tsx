'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  StarIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

interface TeamMember {
  id: string;
  name: string;
  role: string;
  avatar: string;
  status: 'online' | 'offline' | 'busy';
}

interface CandidateScore {
  memberId: string;
  memberName: string;
  score: number;
  feedback: string;
  timestamp: Date;
}

interface CollaborativeNote {
  id: string;
  author: TeamMember;
  content: string;
  timestamp: Date;
  mentions: string[];
}

export default function CollaborativeHiring() {
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([
    {
      id: '1',
      name: 'Sarah Johnson',
      role: 'Hiring Manager',
      avatar: '/avatars/sarah.jpg',
      status: 'online'
    },
    {
      id: '2',
      name: 'Mike Chen',
      role: 'Technical Lead',
      avatar: '/avatars/mike.jpg',
      status: 'online'
    },
    {
      id: '3',
      name: 'Emily Davis',
      role: 'HR Specialist',
      avatar: '/avatars/emily.jpg',
      status: 'busy'
    }
  ]);

  const [scores, setScores] = useState<CandidateScore[]>([
    {
      memberId: '1',
      memberName: 'Sarah Johnson',
      score: 4.5,
      feedback: 'Strong technical skills and great communication',
      timestamp: new Date()
    },
    {
      memberId: '2',
      memberName: 'Mike Chen',
      score: 4.0,
      feedback: 'Good problem-solving abilities',
      timestamp: new Date()
    }
  ]);

  const [notes, setNotes] = useState<CollaborativeNote[]>([]);
  const [newNote, setNewNote] = useState('');
  const [activeTab, setActiveTab] = useState<'scores' | 'notes' | 'team'>('scores');

  const averageScore = scores.reduce((sum, s) => sum + s.score, 0) / scores.length;

  const addNote = () => {
    if (!newNote.trim()) return;

    const note: CollaborativeNote = {
      id: Date.now().toString(),
      author: teamMembers[0],
      content: newNote,
      timestamp: new Date(),
      mentions: []
    };

    setNotes([note, ...notes]);
    setNewNote('');
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <UserGroupIcon className="w-8 h-8 text-blue-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Collaborative Hiring
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Team evaluation for John Doe
            </p>
          </div>
        </div>

        {/* Average Score */}
        <div className="text-center">
          <div className="text-3xl font-bold text-blue-600">
            {averageScore.toFixed(1)}
          </div>
          <div className="flex items-center justify-center mt-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <StarIcon
                key={star}
                className={`w-5 h-5 ${
                  star <= averageScore
                    ? 'text-yellow-400 fill-current'
                    : 'text-gray-300'
                }`}
              />
            ))}
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Team Average
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 mb-6 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
        {(['scores', 'notes', 'team'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'bg-white dark:bg-gray-800 text-blue-600 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'scores' && (
          <motion.div
            key="scores"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            {scores.map((score, index) => (
              <motion.div
                key={score.memberId}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">
                      {score.memberName}
                    </h4>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {score.timestamp.toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center space-x-1">
                    <span className="text-lg font-bold text-blue-600">
                      {score.score}
                    </span>
                    <StarIcon className="w-5 h-5 text-yellow-400 fill-current" />
                  </div>
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  {score.feedback}
                </p>
              </motion.div>
            ))}

            {/* Add Score Button */}
            <button className="w-full py-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-gray-600 dark:text-gray-400 hover:border-blue-500 hover:text-blue-600 transition-colors">
              + Add Your Score
            </button>
          </motion.div>
        )}

        {activeTab === 'notes' && (
          <motion.div
            key="notes"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            {/* Add Note */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <textarea
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Add a note... (use @ to mention team members)"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none"
                rows={3}
              />
              <div className="flex justify-end mt-2">
                <button
                  onClick={addNote}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add Note
                </button>
              </div>
            </div>

            {/* Notes List */}
            <div className="space-y-3">
              {notes.length === 0 ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <ChatBubbleLeftRightIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No notes yet. Be the first to add one!</p>
                </div>
              ) : (
                notes.map((note, index) => (
                  <motion.div
                    key={note.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                        {note.author.name.charAt(0)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="font-semibold text-gray-900 dark:text-white">
                            {note.author.name}
                          </h4>
                          <span className="text-xs text-gray-600 dark:text-gray-400">
                            {note.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          {note.content}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        )}

        {activeTab === 'team' && (
          <motion.div
            key="team"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-3"
          >
            {teamMembers.map((member, index) => (
              <motion.div
                key={member.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 flex items-center justify-between"
              >
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-lg">
                      {member.name.charAt(0)}
                    </div>
                    <div
                      className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white dark:border-gray-700 ${
                        member.status === 'online'
                          ? 'bg-green-500'
                          : member.status === 'busy'
                          ? 'bg-yellow-500'
                          : 'bg-gray-400'
                      }`}
                    />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">
                      {member.name}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {member.role}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {scores.find((s) => s.memberId === member.id) ? (
                    <CheckCircleIcon className="w-6 h-6 text-green-500" />
                  ) : (
                    <ClockIcon className="w-6 h-6 text-gray-400" />
                  )}
                </div>
              </motion.div>
            ))}

            {/* Add Team Member */}
            <button className="w-full py-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-gray-600 dark:text-gray-400 hover:border-blue-500 hover:text-blue-600 transition-colors">
              + Add Team Member
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Actions */}
      <div className="flex space-x-3 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <button className="flex-1 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center space-x-2">
          <CheckCircleIcon className="w-5 h-5" />
          <span>Move to Next Stage</span>
        </button>
        <button className="flex-1 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center space-x-2">
          <XCircleIcon className="w-5 h-5" />
          <span>Reject Candidate</span>
        </button>
      </div>
    </div>
  );
}
