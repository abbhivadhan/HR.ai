'use client';

import { useState, useRef, useEffect } from 'react';
import { portfolioService } from '@/services/portfolioService';
import { 
  VideoCameraIcon, 
  StopIcon, 
  PlayIcon, 
  ArrowUpTrayIcon 
} from '@heroicons/react/24/outline';

interface VideoRecorderProps {
  onVideoUploaded: (videoUrl: string) => void;
  maxDuration?: number; // seconds
}

export function VideoRecorder({ onVideoUploaded, maxDuration = 60 }: VideoRecorderProps) {
  const [recording, setRecording] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 },
        audio: true,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp8,opus',
      });

      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' });
        setRecordedBlob(blob);
        const url = URL.createObjectURL(blob);
        setPreviewUrl(url);

        // Stop all tracks
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setRecording(true);
      setDuration(0);
      setError(null);

      // Start timer
      timerRef.current = setInterval(() => {
        setDuration((prev) => {
          const newDuration = prev + 1;
          if (newDuration >= maxDuration) {
            stopRecording();
          }
          return newDuration;
        });
      }, 1000);
    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Failed to access camera/microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const handleUpload = async () => {
    if (!recordedBlob) return;

    setUploading(true);
    setError(null);

    try {
      const file = new File([recordedBlob], 'video-intro.webm', { type: 'video/webm' });
      const videoUrl = await portfolioService.uploadVideo(file);
      onVideoUploaded(videoUrl);
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload video. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const reset = () => {
    setRecordedBlob(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    setDuration(0);
    setError(null);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-4">
      {/* Video Preview */}
      <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
        <video
          ref={videoRef}
          autoPlay
          muted={recording}
          playsInline
          src={previewUrl || undefined}
          className="w-full h-full object-cover"
        />

        {/* Timer Overlay */}
        {recording && (
          <div className="absolute top-4 right-4 bg-red-600 text-white px-3 py-1 rounded-full flex items-center gap-2">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
            <span className="font-mono">{formatTime(duration)}</span>
            <span className="text-sm">/ {formatTime(maxDuration)}</span>
          </div>
        )}

        {/* No Video State */}
        {!recording && !previewUrl && (
          <div className="absolute inset-0 flex items-center justify-center">
            <VideoCameraIcon className="w-16 h-16 text-gray-400" />
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Controls */}
      <div className="flex gap-3">
        {!recording && !recordedBlob && (
          <button
            onClick={startRecording}
            className="flex-1 flex items-center justify-center gap-2 bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 transition-colors font-medium"
          >
            <PlayIcon className="w-5 h-5" />
            Start Recording
          </button>
        )}

        {recording && (
          <button
            onClick={stopRecording}
            className="flex-1 flex items-center justify-center gap-2 bg-gray-800 text-white py-3 rounded-lg hover:bg-gray-900 transition-colors font-medium"
          >
            <StopIcon className="w-5 h-5" />
            Stop Recording
          </button>
        )}

        {recordedBlob && !uploading && (
          <>
            <button
              onClick={reset}
              className="flex-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 py-3 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              Re-record
            </button>
            <button
              onClick={handleUpload}
              className="flex-1 flex items-center justify-center gap-2 bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 transition-colors font-medium"
            >
              <ArrowUpTrayIcon className="w-5 h-5" />
              Upload Video
            </button>
          </>
        )}

        {uploading && (
          <button
            disabled
            className="flex-1 flex items-center justify-center gap-2 bg-purple-600 text-white py-3 rounded-lg opacity-50 cursor-not-allowed font-medium"
          >
            <Loader2 className="w-5 h-5 animate-spin" />
            Uploading...
          </button>
        )}
      </div>

      {/* Info */}
      <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
        Record a {maxDuration}-second video introduction to showcase your personality and skills
      </p>
    </div>
  );
}
