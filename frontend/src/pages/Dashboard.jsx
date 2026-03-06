import React, { useState, useEffect } from 'react';
import MetricCard from '../components/MetricCard';
import { SafetyTrendChart, ViolationsChart, RiskDistributionChart } from '../components/Charts';
import {
    ShieldCheckIcon,
    ChartBarIcon,
    ExclamationTriangleIcon,
    ClockIcon,
    ServerIcon
} from '@heroicons/react/24/outline';

const Dashboard = () => {
    const [metrics, setMetrics] = useState({
        totalRequests: 1247,
        averageSafetyScore: 0.847,
        activePolicies: 12,
        violations: 138,
        avgLatency: 42
    });

    const [systemHealth, setSystemHealth] = useState({
        status: 'healthy',
        uptime: '99.9%',
        lastUpdate: new Date().toLocaleTimeString()
    });

    // Simulate real-time updates
    useEffect(() => {
        const interval = setInterval(() => {
            setMetrics(prev => ({
                ...prev,
                totalRequests: prev.totalRequests + Math.floor(Math.random() * 3),
                averageSafetyScore: Math.max(0.1, Math.min(1.0, prev.averageSafetyScore + (Math.random() - 0.5) * 0.02))
            }));
            setSystemHealth(prev => ({
                ...prev,
                lastUpdate: new Date().toLocaleTimeString()
            }));
        }, 10000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-text-primary">Dashboard</h1>
                    <p className="text-text-muted mt-1">AI Safety Gateway Overview</p>
                </div>
                <div className="flex items-center space-x-2">
                    <ServerIcon className="h-5 w-5 text-secondary-accent" />
                    <span className="text-sm text-text-primary">Last updated: {systemHealth.lastUpdate}</span>
                </div>
            </div>

            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                <MetricCard
                    title="Total Requests"
                    value={metrics.totalRequests.toLocaleString()}
                    icon={ChartBarIcon}
                    trend={{ direction: 'up', value: '+12%' }}
                    color="primary"
                />

                <MetricCard
                    title="Avg Safety Score"
                    value={metrics.averageSafetyScore.toFixed(3)}
                    icon={ShieldCheckIcon}
                    trend={{ direction: 'up', value: '+0.05' }}
                    color="success"
                />

                <MetricCard
                    title="Active Policies"
                    value={metrics.activePolicies}
                    icon={ShieldCheckIcon}
                    trend={{ direction: 'neutral', value: '0' }}
                    color="primary"
                />

                <MetricCard
                    title="Violations"
                    value={metrics.violations}
                    icon={ExclamationTriangleIcon}
                    trend={{ direction: 'down', value: '-5%' }}
                    color="warning"
                />

                <MetricCard
                    title="Avg Latency"
                    value={`${metrics.avgLatency}ms`}
                    icon={ClockIcon}
                    trend={{ direction: 'down', value: '-3ms' }}
                    color="success"
                />
            </div>

            {/* System Status Banner */}
            <div className="bg-card-bg rounded-xl p-4 border border-secondary-accent border-opacity-30 shadow-glow-green">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-secondary-accent rounded-full animate-pulse"></div>
                        <span className="text-text-primary font-medium">System Status: Healthy</span>
                        <span className="text-text-muted">•</span>
                        <span className="text-text-muted">Uptime: {systemHealth.uptime}</span>
                    </div>
                    <div className="text-sm text-text-muted">
                        All security filters operational
                    </div>
                </div>
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <SafetyTrendChart />
                <ViolationsChart />
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                <div className="xl:col-span-1">
                    <RiskDistributionChart />
                </div>

                {/* Recent Activity */}
                <div className="xl:col-span-2 bg-card-bg rounded-xl p-6 border border-border-color">
                    <h3 className="text-lg font-semibold text-text-primary mb-4">Recent Security Events</h3>
                    <div className="space-y-3">
                        {[
                            { time: '2 min ago', event: 'High-risk prompt blocked', severity: 'high', user: 'user_123' },
                            { time: '5 min ago', event: 'Prompt injection attempt detected', severity: 'medium', user: 'user_456' },
                            { time: '8 min ago', event: 'Content sanitized successfully', severity: 'low', user: 'user_789' },
                            { time: '12 min ago', event: 'Policy violation: toxic language', severity: 'medium', user: 'user_101' },
                            { time: '15 min ago', event: 'Clean prompt processed', severity: 'info', user: 'user_202' }
                        ].map((activity, index) => (
                            <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-border-color bg-opacity-50">
                                <div className="flex items-center space-x-3">
                                    <div className={`w-2 h-2 rounded-full ${activity.severity === 'high' ? 'bg-danger-color' :
                                            activity.severity === 'medium' ? 'bg-warning-color' :
                                                activity.severity === 'low' ? 'bg-primary-accent' : 'bg-secondary-accent'
                                        }`}></div>
                                    <span className="text-text-primary text-sm">{activity.event}</span>
                                </div>
                                <div className="flex items-center space-x-4">
                                    <span className="text-text-muted text-xs">{activity.user}</span>
                                    <span className="text-text-muted text-xs">{activity.time}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;