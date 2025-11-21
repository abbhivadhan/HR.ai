'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { schedulingService } from '@/services/schedulingService';
import { ScheduledEvent } from '@/types/scheduling';
import { SmartCalendar } from '@/components/scheduling/SmartCalendar';
import AnimatedCard from '@/components/ui/AnimatedCard';
import { 
  CalendarIcon, 
  ClockIcon, 
  VideoCameraIcon,
  BellIcon,
  UserGroupIcon,
  MapPinIcon,
  PlusIcon,
  SparklesIcon,
  CheckCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

export default function SchedulingPage() {
  const [events, setEvents] = useState<ScheduledEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<ScheduledEvent | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar');

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const data = await schedulingService.getEvents();
      setEvents(data);
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  };

  const upcomingEvents = events.filter(e => new Date(e.start_time) > new Date()).slice(0, 5);
  const todayEvents = events.filter(e => {
    const eventDate = new Date(e.start_time);
    const today = new Date();
    return eventDate.toDateString() === today.toDateString();
  });

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center">
                  <CalendarIcon className="w-7 h-7 text-green-600" />
                </div>
                <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
                  Smart Scheduling
                </h1>
              </div>
              <p className="text-gray-600 dark:text-gray-300 ml-15">
                AI-powered calendar management for interviews and meetings
              </p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-xl hover:from-green-700 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl font-semibold"
            >
              <PlusIcon className="w-5 h-5" />
              Schedule Event
            </button>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <AnimatedCard className="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Today</p>
                  <p className="text-2xl font-bold text-green-600">{todayEvents.length}</p>
                </div>
                <CalendarIcon className="w-8 h-8 text-green-600 opacity-50" />
              </div>
            </AnimatedCard>

            <AnimatedCard className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Upcoming</p>
                  <p className="text-2xl font-bold text-blue-600">{upcomingEvents.length}</p>
                </div>
                <ClockIcon className="w-8 h-8 text-blue-600 opacity-50" />
              </div>
            </AnimatedCard>

            <AnimatedCard className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">This Week</p>
                  <p className="text-2xl font-bold text-purple-600">{events.length}</p>
                </div>
                <BellIcon className="w-8 h-8 text-purple-600 opacity-50" />
              </div>
            </AnimatedCard>

            <AnimatedCard className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border-orange-200 dark:border-orange-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">AI Optimized</p>
                  <p className="text-2xl font-bold text-orange-600">95%</p>
                </div>
                <SparklesIcon className="w-8 h-8 text-orange-600 opacity-50" />
              </div>
            </AnimatedCard>
          </div>
        </motion.div>

        {/* View Toggle */}
        <div className="flex justify-end mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-1 shadow-md inline-flex">
            <button
              onClick={() => setViewMode('calendar')}
              className={`px-4 py-2 rounded-md transition-all ${
                viewMode === 'calendar'
                  ? 'bg-green-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Calendar View
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-4 py-2 rounded-md transition-all ${
                viewMode === 'list'
                  ? 'bg-green-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              List View
            </button>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Calendar/List View */}
          <div className="lg:col-span-2">
            {viewMode === 'calendar' ? (
              <SmartCalendar events={events} onEventClick={setSelectedEvent} />
            ) : (
              <AnimatedCard className="p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">All Events</h2>
                <div className="space-y-3">
                  {events.map((event, index) => (
                    <motion.div
                      key={event.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      onClick={() => setSelectedEvent(event)}
                      className="p-4 bg-gray-50 dark:bg-gray-700 rounded-xl cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-all border border-gray-200 dark:border-gray-600"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{event.title}</h3>
                          <div className="space-y-1">
                            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                              <ClockIcon className="w-4 h-4" />
                              {new Date(event.start_time).toLocaleString()}
                            </div>
                            {event.meeting_url && (
                              <div className="flex items-center gap-2 text-sm text-blue-600">
                                <VideoCameraIcon className="w-4 h-4" />
                                Video Meeting
                              </div>
                            )}
                          </div>
                        </div>
                        <span className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-600 text-xs rounded-full">
                          {event.status}
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </AnimatedCard>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Upcoming Events */}
            <AnimatedCard className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Upcoming</h2>
                <BellIcon className="w-5 h-5 text-green-600" />
              </div>
              <div className="space-y-3">
                {upcomingEvents.length > 0 ? (
                  upcomingEvents.map((event) => (
                    <div
                      key={event.id}
                      onClick={() => setSelectedEvent(event)}
                      className="p-3 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg cursor-pointer hover:shadow-md transition-all border border-green-200 dark:border-green-800"
                    >
                      <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-1">{event.title}</h3>
                      <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                        <ClockIcon className="w-3 h-3" />
                        {new Date(event.start_time).toLocaleString()}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 dark:text-gray-400 text-sm text-center py-4">
                    No upcoming events
                  </p>
                )}
              </div>
            </AnimatedCard>

            {/* AI Suggestions */}
            <AnimatedCard className="p-6 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20">
              <div className="flex items-center gap-2 mb-4">
                <SparklesIcon className="w-6 h-6 text-purple-600" />
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">AI Suggestions</h2>
              </div>
              <div className="space-y-3">
                <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                    Best time for interviews: 10 AM - 12 PM
                  </p>
                  <span className="text-xs text-purple-600">Based on your schedule</span>
                </div>
                <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                    Add 15-min buffer between meetings
                  </p>
                  <span className="text-xs text-purple-600">Reduce stress</span>
                </div>
              </div>
            </AnimatedCard>

            {/* Quick Actions */}
            <AnimatedCard className="p-6">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
              <div className="space-y-2">
                <button className="w-full flex items-center gap-3 p-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors">
                  <VideoCameraIcon className="w-5 h-5 text-blue-600" />
                  <span className="text-gray-900 dark:text-white text-sm">Schedule Interview</span>
                </button>
                <button className="w-full flex items-center gap-3 p-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors">
                  <UserGroupIcon className="w-5 h-5 text-green-600" />
                  <span className="text-gray-900 dark:text-white text-sm">Team Meeting</span>
                </button>
                <button className="w-full flex items-center gap-3 p-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors">
                  <BellIcon className="w-5 h-5 text-orange-600" />
                  <span className="text-gray-900 dark:text-white text-sm">Set Reminder</span>
                </button>
              </div>
            </AnimatedCard>
          </div>
        </div>

        {/* Event Details Modal */}
        {selectedEvent && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={() => setSelectedEvent(null)}>
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              onClick={(e) => e.stopPropagation()}
            >
              <AnimatedCard className="max-w-2xl w-full p-8 relative">
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="absolute top-4 right-4 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <XMarkIcon className="w-5 h-5 text-gray-500" />
                </button>

                <div className="flex items-start gap-4 mb-6">
                  <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                    <CalendarIcon className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{selectedEvent.title}</h2>
                    <span className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-600 text-sm rounded-full">
                      {selectedEvent.status}
                    </span>
                  </div>
                </div>

                <div className="space-y-4 mb-6">
                  <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <CalendarIcon className="w-5 h-5 text-green-600" />
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Date</p>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {new Date(selectedEvent.start_time).toLocaleDateString('en-US', { 
                          weekday: 'long', 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <ClockIcon className="w-5 h-5 text-blue-600" />
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Time</p>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {new Date(selectedEvent.start_time).toLocaleTimeString('en-US', { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </p>
                    </div>
                  </div>

                  {selectedEvent.meeting_url && (
                    <div className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                      <VideoCameraIcon className="w-5 h-5 text-blue-600" />
                      <div className="flex-1">
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Video Meeting</p>
                        <a 
                          href={selectedEvent.meeting_url} 
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline font-medium"
                        >
                          Join Meeting →
                        </a>
                      </div>
                    </div>
                  )}

                  {selectedEvent.description && (
                    <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <MapPinIcon className="w-5 h-5 text-purple-600" />
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Description</p>
                        <p className="font-medium text-gray-900 dark:text-white">{selectedEvent.description}</p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex gap-3">
                  {selectedEvent.meeting_url && (
                    <a
                      href={selectedEvent.meeting_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg hover:from-green-700 hover:to-blue-700 transition-all font-semibold"
                    >
                      <VideoCameraIcon className="w-5 h-5" />
                      Join Now
                    </a>
                  )}
                  <button
                    onClick={() => setSelectedEvent(null)}
                    className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-semibold"
                  >
                    Close
                  </button>
                </div>
              </AnimatedCard>
            </motion.div>
          </div>
        )}

        {/* Create Event Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={() => setShowCreateModal(false)}>
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              onClick={(e) => e.stopPropagation()}
            >
              <AnimatedCard className="max-w-2xl w-full p-8">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Schedule New Event</h2>
                <form className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Event Title
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
                      placeholder="e.g., Technical Interview with John"
                    />
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Date
                      </label>
                      <input
                        type="date"
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Time
                      </label>
                      <input
                        type="time"
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Meeting URL (Optional)
                    </label>
                    <input
                      type="url"
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
                      placeholder="https://meet.google.com/..."
                    />
                  </div>

                  <div className="flex gap-3 pt-4">
                    <button
                      type="submit"
                      className="flex-1 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg hover:from-green-700 hover:to-blue-700 transition-all font-semibold"
                    >
                      Create Event
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCreateModal(false)}
                      className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-semibold"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </AnimatedCard>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
}
