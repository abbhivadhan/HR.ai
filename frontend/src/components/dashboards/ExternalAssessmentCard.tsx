'use client'

import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { 
  AcademicCapIcon,
  ArrowRightIcon,
  SparklesIcon,
  CodeBracketIcon,
  CommandLineIcon,
  BeakerIcon,
  BookOpenIcon
} from '@heroicons/react/24/outline'

export default function ExternalAssessmentCard() {
  const router = useRouter()

  const providers = [
    { name: 'HackerRank', icon: CodeBracketIcon },
    { name: 'CodeSignal', icon: CommandLineIcon },
    { name: 'TestGorilla', icon: BeakerIcon },
    { name: 'Pluralsight', icon: BookOpenIcon }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 rounded-xl shadow-lg p-6 text-white relative overflow-hidden"
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-40 h-40 bg-white rounded-full -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute bottom-0 right-0 w-60 h-60 bg-white rounded-full translate-x-1/3 translate-y-1/3"></div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        <div className="flex items-center space-x-2 mb-3">
          <SparklesIcon className="w-6 h-6" />
          <h3 className="text-xl font-bold">Professional Assessments</h3>
        </div>

        <p className="text-white/90 mb-4 text-sm">
          Take industry-standard skill tests from leading platforms
        </p>

        {/* Provider Icons */}
        <div className="flex items-center space-x-2 mb-4">
          {providers.map((provider) => {
            const Icon = provider.icon
            return (
              <div
                key={provider.name}
                className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center"
                title={provider.name}
              >
                <Icon className="w-5 h-5 text-white" />
              </div>
            )
          })}
          <div className="text-xs text-white/80 ml-2">+more</div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-2 text-center">
            <div className="text-2xl font-bold">12+</div>
            <div className="text-xs text-white/80">Tests</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-2 text-center">
            <div className="text-2xl font-bold">4</div>
            <div className="text-xs text-white/80">Providers</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-2 text-center">
            <div className="text-2xl font-bold">100%</div>
            <div className="text-xs text-white/80">Free</div>
          </div>
        </div>

        {/* CTA Button */}
        <button
          onClick={() => router.push('/assessments/external')}
          className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-white text-purple-600 rounded-lg hover:bg-white/90 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          <AcademicCapIcon className="w-5 h-5" />
          <span>Browse Tests</span>
          <ArrowRightIcon className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  )
}
