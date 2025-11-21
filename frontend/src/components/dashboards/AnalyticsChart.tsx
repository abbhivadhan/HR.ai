'use client';

import React from 'react';
import { ChartData } from '../../types/dashboard';

interface AnalyticsChartProps {
  data: ChartData;
  type: 'line' | 'bar' | 'doughnut' | 'pie';
  height?: number;
  loading?: boolean;
}

// Simple chart implementation using CSS and SVG
// In a real implementation, you'd use a library like Chart.js or Recharts
const AnalyticsChart: React.FC<AnalyticsChartProps> = ({
  data,
  type,
  height = 300,
  loading = false
}) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data.datasets.length || !data.labels.length) {
    return (
      <div className="flex items-center justify-center text-gray-500" style={{ height }}>
        No data available
      </div>
    );
  }

  // Simple bar chart implementation
  if (type === 'bar') {
    const maxValue = Math.max(...data.datasets[0].data);
    
    return (
      <div className="w-full" style={{ height }}>
        <div className="flex items-end justify-between h-full space-x-2 px-4">
          {data.labels.map((label, index) => {
            const value = data.datasets[0].data[index];
            const barHeight = (value / maxValue) * (height - 60);
            
            return (
              <div key={label} className="flex flex-col items-center flex-1">
                <div className="flex flex-col items-center justify-end flex-1">
                  <span className="text-xs text-gray-600 mb-1">{value}</span>
                  <div
                    className="w-full bg-blue-500 rounded-t transition-all duration-300 hover:bg-blue-600"
                    style={{ height: `${barHeight}px`, minHeight: '4px' }}
                  ></div>
                </div>
                <span className="text-xs text-gray-500 mt-2 text-center">{label}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Simple line chart implementation
  if (type === 'line') {
    const maxValue = Math.max(...data.datasets[0].data);
    const minValue = Math.min(...data.datasets[0].data);
    const range = maxValue - minValue || 1;
    
    return (
      <div className="w-full" style={{ height }}>
        <svg width="100%" height="100%" className="overflow-visible">
          <defs>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#3B82F6" stopOpacity="0" />
            </linearGradient>
          </defs>
          
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
            <line
              key={ratio}
              x1="0"
              y1={ratio * (height - 40)}
              x2="100%"
              y2={ratio * (height - 40)}
              stroke="#E5E7EB"
              strokeWidth="1"
            />
          ))}
          
          {/* Data line */}
          <polyline
            fill="none"
            stroke="#3B82F6"
            strokeWidth="2"
            points={data.labels.map((_, index) => {
              const x = (index / (data.labels.length - 1)) * 100;
              const y = ((maxValue - data.datasets[0].data[index]) / range) * (height - 40);
              return `${x}%,${y}`;
            }).join(' ')}
          />
          
          {/* Data points */}
          {data.labels.map((_, index) => {
            const x = (index / (data.labels.length - 1)) * 100;
            const y = ((maxValue - data.datasets[0].data[index]) / range) * (height - 40);
            return (
              <circle
                key={index}
                cx={`${x}%`}
                cy={y}
                r="4"
                fill="#3B82F6"
                className="hover:r-6 transition-all"
              />
            );
          })}
        </svg>
        
        {/* X-axis labels */}
        <div className="flex justify-between mt-2 px-2">
          {data.labels.map((label) => (
            <span key={label} className="text-xs text-gray-500">{label}</span>
          ))}
        </div>
      </div>
    );
  }

  // Simple doughnut chart implementation
  if (type === 'doughnut' || type === 'pie') {
    const total = data.datasets[0].data.reduce((sum, value) => sum + value, 0);
    let currentAngle = 0;
    const chartSize = Math.min(height - 40, 200); // Constrain chart size
    const centerX = chartSize / 2;
    const centerY = chartSize / 2;
    const radius = Math.min(centerX, centerY) - 10;
    const innerRadius = type === 'doughnut' ? radius * 0.6 : 0;
    
    const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];
    
    return (
      <div className="w-full overflow-hidden" style={{ height }}>
        <div className="flex flex-col lg:flex-row items-center justify-center space-y-4 lg:space-y-0 lg:space-x-6 h-full">
          <div className="flex-shrink-0">
            <svg width={chartSize} height={chartSize} className="max-w-full">
              {data.datasets[0].data.map((value, index) => {
                const percentage = value / total;
                const angle = percentage * 360;
                const startAngle = currentAngle;
                const endAngle = currentAngle + angle;
                
                const x1 = centerX + radius * Math.cos((startAngle * Math.PI) / 180);
                const y1 = centerY + radius * Math.sin((startAngle * Math.PI) / 180);
                const x2 = centerX + radius * Math.cos((endAngle * Math.PI) / 180);
                const y2 = centerY + radius * Math.sin((endAngle * Math.PI) / 180);
                
                const largeArcFlag = angle > 180 ? 1 : 0;
                
                const pathData = [
                  `M ${centerX} ${centerY}`,
                  `L ${x1} ${y1}`,
                  `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                  'Z'
                ].join(' ');
                
                currentAngle += angle;
                
                return (
                  <path
                    key={index}
                    d={pathData}
                    fill={colors[index % colors.length]}
                    className="hover:opacity-80 transition-opacity"
                  />
                );
              })}
              
              {type === 'doughnut' && (
                <circle
                  cx={centerX}
                  cy={centerY}
                  r={innerRadius}
                  fill="white"
                />
              )}
            </svg>
          </div>
          
          {/* Legend */}
          <div className="flex-shrink-0 space-y-1 max-w-xs">
            {data.labels.map((label, index) => (
              <div key={label} className="flex items-center space-x-2 text-xs">
                <div
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: colors[index % colors.length] }}
                ></div>
                <span className="text-gray-700 truncate">{label}</span>
                <span className="text-gray-500 flex-shrink-0">
                  {data.datasets[0].data[index]}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center text-gray-500" style={{ height }}>
      Chart type not supported
    </div>
  );
};

export default AnalyticsChart;