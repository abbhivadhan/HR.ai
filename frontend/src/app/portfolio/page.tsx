'use client';

import { useState, useEffect } from 'react';
import { portfolioService } from '@/services/portfolioService';
import { Portfolio, PortfolioProject } from '@/types/portfolio';
import { VideoRecorder } from '@/components/portfolio/VideoRecorder';
import AnimatedCard from '@/components/ui/AnimatedCard';
import { 
  VideoCameraIcon, 
  PlusIcon, 
  ArrowTopRightOnSquareIcon 
} from '@heroicons/react/24/outline';

export default function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [projects, setProjects] = useState<PortfolioProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [showVideoRecorder, setShowVideoRecorder] = useState(false);

  useEffect(() => {
    loadPortfolio();
  }, []);

  const loadPortfolio = async () => {
    try {
      const data = await portfolioService.getMyPortfolio();
      setPortfolio(data);
      const projectsData = await portfolioService.getProjects();
      setProjects(projectsData);
    } catch (error) {
      console.error('Failed to load portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVideoUploaded = async (videoUrl: string) => {
    try {
      await portfolioService.updatePortfolio({ video_intro_url: videoUrl });
      setShowVideoRecorder(false);
      loadPortfolio();
    } catch (error) {
      console.error('Failed to update portfolio:', error);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">
          My Portfolio
        </h1>

        {/* Video Introduction */}
        <AnimatedCard className="p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">Video Introduction</h2>
          {portfolio?.video_intro_url ? (
            <div>
              <video src={portfolio.video_intro_url} controls className="w-full rounded-lg" />
              <button
                onClick={() => setShowVideoRecorder(true)}
                className="mt-4 text-purple-600 hover:text-purple-700"
              >
                Re-record
              </button>
            </div>
          ) : showVideoRecorder ? (
            <VideoRecorder onVideoUploaded={handleVideoUploaded} />
          ) : (
            <button
              onClick={() => setShowVideoRecorder(true)}
              className="flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg"
            >
              <VideoCameraIcon className="w-5 h-5" />
              Record Video Introduction
            </button>
          )}
        </AnimatedCard>

        {/* Projects */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Projects</h2>
            <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg">
              <PlusIcon className="w-5 h-5" />
              Add Project
            </button>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {projects.map((project) => (
              <AnimatedCard key={project.id} className="p-6">
                <h3 className="text-xl font-bold mb-2">{project.title}</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">{project.description}</p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {project.technologies.map((tech) => (
                    <span key={tech} className="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded text-sm">
                      {tech}
                    </span>
                  ))}
                </div>
                <div className="flex gap-3">
                  {project.live_url && (
                    <a href={project.live_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-purple-600">
                      <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                      Live
                    </a>
                  )}
                  {project.github_url && (
                    <a href={project.github_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-purple-600">
                      <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                      Code
                    </a>
                  )}
                </div>
              </AnimatedCard>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
