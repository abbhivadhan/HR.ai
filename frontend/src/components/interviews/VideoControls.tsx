'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  VideoCameraIcon,
  VideoCameraSlashIcon,
  MicrophoneIcon,
  XMarkIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  ExclamationTriangleIcon,
  SignalIcon,
  CogIcon,
  PhoneXMarkIcon
} from '@heroicons/react/24/outline';
import { VideoSettings, ConnectionQuality } from '../../types/interview';

interface VideoControlsProps {
  videoSettings: VideoSettings;
  onToggleCamera: () => void;
  onToggleMicrophone: () => void;
  onToggleSpeaker: () => void;
  onTechnicalIssue: (issue: string) => void;
  connectionQuality: ConnectionQuality;
}

export const VideoControls: React.FC<VideoControlsProps> = ({
  videoSettings,
  onToggleCamera,
  onToggleMicrophone,
  onToggleSpeaker,
  onTechnicalIssue,
  connectionQuality
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const getQualityColor = (quality: number) => {
    if (quality >= 0.8) return 'text-green-500';
    if (quality >= 0.6) return 'text-yellow-500';
    if (quality >= 0.4) return 'text-orange-500';
    return 'text-red-500';
  };

  const getQualityBars = (quality: number) => {
    const bars = Math.ceil(quality * 4);
    return Array.from({ length: 4 }, (_, i) => (
      <div
        key={i}
        className={`w-1 h-3 rounded-full ${
          i < bars ? getQualityColor(quality).replace('text-', 'bg-') : 'bg-gray-600'
        }`}
      />
    ));
  };

  return (
    <div className="bg-gray-800 border-t border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Main controls */}
        <div className="flex items-center space-x-4">
          {/* Camera toggle */}
          <button
            onClick={onToggleCamera}
            className={`p-3 rounded-full transition-colors ${
              videoSettings.camera
                ? 'bg-gray-700 text-white hover:bg-gray-600'
                : 'bg-red-600 text-white hover:bg-red-700'
            }`}
            title={videoSettings.camera ? 'Turn off camera' : 'Turn on camera'}
          >
            {videoSettings.camera ? (
              <VideoCameraIcon className="h-6 w-6" />
            ) : (
              <VideoCameraSlashIcon className="h-6 w-6" />
            )}
          </button>

          {/* Microphone toggle */}
          <button
            onClick={onToggleMicrophone}
            className={`p-3 rounded-full transition-colors ${
              videoSettings.microphone
                ? 'bg-gray-700 text-white hover:bg-gray-600'
                : 'bg-red-600 text-white hover:bg-red-700'
            }`}
            title={videoSettings.microphone ? 'Mute microphone' : 'Unmute microphone'}
          >
            {videoSettings.microphone ? (
              <MicrophoneIcon className="h-6 w-6" />
            ) : (
              <XMarkIcon className="h-6 w-6" />
            )}
          </button>

          {/* Speaker toggle */}
          <button
            onClick={onToggleSpeaker}
            className={`p-3 rounded-full transition-colors ${
              videoSettings.speaker
                ? 'bg-gray-700 text-white hover:bg-gray-600'
                : 'bg-red-600 text-white hover:bg-red-700'
            }`}
            title={videoSettings.speaker ? 'Mute speaker' : 'Unmute speaker'}
          >
            {videoSettings.speaker ? (
              <SpeakerWaveIcon className="h-6 w-6" />
            ) : (
              <SpeakerXMarkIcon className="h-6 w-6" />
            )}
          </button>

          {/* Connection quality indicator */}
          <div className="flex items-center space-x-2 px-3 py-2 bg-gray-700 rounded-lg">
            <SignalIcon className={`h-5 w-5 ${getQualityColor(connectionQuality.video)}`} />
            <div className="flex items-center space-x-1">
              {getQualityBars(connectionQuality.video)}
            </div>
            <span className="text-sm text-gray-300">
              {connectionQuality.overall}
            </span>
          </div>
        </div>

        {/* Secondary controls */}
        <div className="flex items-center space-x-4">
          {/* Advanced settings toggle */}
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="p-2 text-gray-400 hover:text-white rounded-md hover:bg-gray-700"
            title="Advanced settings"
          >
            <CogIcon className="h-5 w-5" />
          </button>

          {/* Technical issues button */}
          <button
            onClick={() => onTechnicalIssue('User reported technical issue')}
            className="flex items-center space-x-2 px-3 py-2 text-yellow-400 hover:text-yellow-300 rounded-md hover:bg-gray-700"
            title="Report technical issue"
          >
            <ExclamationTriangleIcon className="h-5 w-5" />
            <span className="text-sm">Issues?</span>
          </button>

          {/* End call button */}
          <button
            onClick={() => onTechnicalIssue('User ended interview')}
            className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            title="End interview"
          >
            <PhoneXMarkIcon className="h-5 w-5" />
            <span className="text-sm">End</span>
          </button>
        </div>
      </div>

      {/* Advanced settings panel */}
      {showAdvanced && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="mt-4 pt-4 border-t border-gray-700"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Connection details */}
            <div className="bg-gray-700 rounded-lg p-4">
              <h4 className="text-white font-medium mb-3">Connection Quality</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Video:</span>
                  <span className={getQualityColor(connectionQuality.video)}>
                    {Math.round(connectionQuality.video * 100)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Audio:</span>
                  <span className={getQualityColor(connectionQuality.audio)}>
                    {Math.round(connectionQuality.audio * 100)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Latency:</span>
                  <span className="text-white">{connectionQuality.latency}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Bandwidth:</span>
                  <span className="text-white">{connectionQuality.bandwidth} kbps</span>
                </div>
              </div>
            </div>

            {/* Device settings */}
            <div className="bg-gray-700 rounded-lg p-4">
              <h4 className="text-white font-medium mb-3">Device Settings</h4>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Camera</label>
                  <select
                    className="w-full bg-gray-600 text-white rounded px-3 py-1 text-sm"
                    value={videoSettings.cameraDeviceId || ''}
                    onChange={(e) => {
                      // Handle camera device change
                      console.log('Camera device changed:', e.target.value);
                    }}
                  >
                    <option value="">Default Camera</option>
                    {/* Device options would be populated dynamically */}
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Microphone</label>
                  <select
                    className="w-full bg-gray-600 text-white rounded px-3 py-1 text-sm"
                    value={videoSettings.microphoneDeviceId || ''}
                    onChange={(e) => {
                      // Handle microphone device change
                      console.log('Microphone device changed:', e.target.value);
                    }}
                  >
                    <option value="">Default Microphone</option>
                    {/* Device options would be populated dynamically */}
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Speaker</label>
                  <select
                    className="w-full bg-gray-600 text-white rounded px-3 py-1 text-sm"
                    value={videoSettings.speakerDeviceId || ''}
                    onChange={(e) => {
                      // Handle speaker device change
                      console.log('Speaker device changed:', e.target.value);
                    }}
                  >
                    <option value="">Default Speaker</option>
                    {/* Device options would be populated dynamically */}
                  </select>
                </div>
              </div>
            </div>

            {/* Troubleshooting */}
            <div className="bg-gray-700 rounded-lg p-4">
              <h4 className="text-white font-medium mb-3">Troubleshooting</h4>
              <div className="space-y-2">
                <button
                  onClick={() => onTechnicalIssue('Audio issues')}
                  className="w-full text-left text-sm text-gray-300 hover:text-white py-1"
                >
                  • Audio not working
                </button>
                <button
                  onClick={() => onTechnicalIssue('Video issues')}
                  className="w-full text-left text-sm text-gray-300 hover:text-white py-1"
                >
                  • Video not showing
                </button>
                <button
                  onClick={() => onTechnicalIssue('Connection issues')}
                  className="w-full text-left text-sm text-gray-300 hover:text-white py-1"
                >
                  • Poor connection
                </button>
                <button
                  onClick={() => onTechnicalIssue('Other technical issue')}
                  className="w-full text-left text-sm text-gray-300 hover:text-white py-1"
                >
                  • Other issues
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};