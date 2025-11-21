'use client'

import React from 'react'
import { motion } from 'framer-motion'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line, Bar, Doughnut, Pie } from 'react-chartjs-2'
import { ChartData } from '@/types/dashboard'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface ChartCardProps {
  title: string
  data: ChartData
  type: 'line' | 'bar' | 'doughnut' | 'pie'
  height?: number
  description?: string
  loading?: boolean
  actions?: React.ReactNode
}

const ChartCard: React.FC<ChartCardProps> = ({
  title,
  data,
  type,
  height = 300,
  description,
  loading = false,
  actions
}) => {
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: 'rgb(156, 163, 175)',
          padding: 15,
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1
      }
    },
    scales: type !== 'doughnut' && type !== 'pie' ? {
      x: {
        grid: {
          color: 'rgba(156, 163, 175, 0.1)',
          display: false
        },
        ticks: {
          color: 'rgb(156, 163, 175)'
        }
      },
      y: {
        grid: {
          color: 'rgba(156, 163, 175, 0.1)'
        },
        ticks: {
          color: 'rgb(156, 163, 175)'
        }
      }
    } : undefined
  }

  const renderChart = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center" style={{ height }}>
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )
    }

    switch (type) {
      case 'line':
        return <Line data={data} options={chartOptions} height={height} />
      case 'bar':
        return <Bar data={data} options={chartOptions} height={height} />
      case 'doughnut':
        return <Doughnut data={data} options={chartOptions} height={height} />
      case 'pie':
        return <Pie data={data} options={chartOptions} height={height} />
      default:
        return null
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
          {description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{description}</p>
          )}
        </div>
        {actions && <div>{actions}</div>}
      </div>
      
      <div style={{ height }}>
        {renderChart()}
      </div>
    </motion.div>
  )
}

export default ChartCard
