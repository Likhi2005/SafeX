import React, { useState, useEffect, useRef } from 'react';
import { 
    ShieldCheckIcon, 
    ExclamationTriangleIcon,
    ChartBarIcon,
    GlobeAltIcon,
    ClockIcon,
    EyeIcon,
    BoltIcon
} from '@heroicons/react/24/outline';
import ThreatMap from '../components/ThreatMap';
import ThreatIntelligenceWidget from '../components/ThreatIntelligenceWidget';
import AttackPatternsWidget from '../components/AttackPatternsWidget';
import PredictionsWidget from '../components/PredictionsWidget';
import RealTimeAlerts from '../components/RealTimeAlerts';

const Intelligence = () => {
    const [intelligenceData, setIntelligenceData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(null);
    const wsRef = useRef(null);

    // WebSocket connection for real-time updates
    useEffect(() => {
        if (isRealTimeEnabled) {
            connectWebSocket();
        } else {
            disconnectWebSocket();
        }

        return () => disconnectWebSocket();
    }, [isRealTimeEnabled]);

    const connectWebSocket = () => {
        try {
            // Import socket.io client dynamically
            const io = window.io || require('socket.io-client');
            
            wsRef.current = io('http://localhost:5000', {
                transports: ['websocket', 'polling']
            });

            wsRef.current.on('connect', () => {
                console.log('🔗 Connected to threat intelligence feed');
                wsRef.current.emit('subscribe_threats', { room: 'threats' });
            });

            wsRef.current.on('threat_update', (data) => {
                console.log('📊 Received threat update:', data.type);
                if (data.data) {
                    setIntelligenceData(prev => ({
                        ...prev,
                        real_time: data.data
                    }));
                    setLastUpdated(new Date().toLocaleTimeString());
                }
            });

            wsRef.current.on('new_threat', (data) => {
                console.log('🚨 New threat alert:', data.threat);
                // Handle new threat alerts
            });

            wsRef.current.on('connect_error', (error) => {
                console.warn('WebSocket connection error:', error);
                setError('Real-time connection failed - using polling mode');
            });

        } catch (err) {
            console.warn('WebSocket not available, falling back to polling');
            setError('Real-time updates unavailable');
            startPolling();
        }
    };

    const disconnectWebSocket = () => {
        if (wsRef.current) {
            wsRef.current.emit('unsubscribe_threats', { room: 'threats' });
            wsRef.current.disconnect();
            wsRef.current = null;
        }
    };

    const startPolling = () => {
        const pollInterval = setInterval(fetchIntelligenceData, 30000); // Poll every 30 seconds
        return () => clearInterval(pollInterval);
    };

    const fetchIntelligenceData = async () => {
        try {
            setError(null);
            
            const response = await fetch('http://localhost:5000/api/intelligence/dashboard?minutes=60');
            const data = await response.json();

            if (data.success !== false && data.dashboard) {
                setIntelligenceData(data.dashboard);
                setLastUpdated(new Date().toLocaleTimeString());
            } else {
                throw new Error(data.message || 'Failed to fetch intelligence data');
            }

        } catch (err) {
            console.error('Failed to fetch intelligence data:', err);
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    // Initial data load
    useEffect(() => {
        fetchIntelligenceData();
    }, []);

    const getOverallRiskLevel = () => {
        if (!intelligenceData?.predictions?.predictions?.next_hour_risk) return 'low';
        return intelligenceData.predictions.predictions.next_hour_risk.level;
    };

    const getRiskColor = (level) => {
        switch (level) {
            case 'critical': return 'text-red-500 bg-red-500/10 border-red-500';
            case 'high': return 'text-orange-500 bg-orange-500/10 border-orange-500';
            case 'medium': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500';
            case 'low': return 'text-green-500 bg-green-500/10 border-green-500';
            default: return 'text-gray-500 bg-gray-500/10 border-gray-500';
        }
    };

    if (isLoading && !intelligenceData) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-accent mx-auto"></div>
                    <p className="text-text-muted mt-4">Loading threat intelligence...</p>
                </div>
            </div>
        );
    }

    const riskLevel = getOverallRiskLevel();
    const riskColorClass = getRiskColor(riskLevel);

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-text-primary flex items-center gap-3">
                        <ShieldCheckIcon className="h-8 w-8 text-primary-accent" />
                        Threat Intelligence
                    </h1>
                    <p className="text-text-muted mt-1">Real-time threat analysis, patterns, and predictions</p>
                </div>
                
                {/* Real-time Status */}
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${isRealTimeEnabled ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
                        <span className="text-sm text-text-muted">
                            {isRealTimeEnabled ? 'Live' : 'Polling'}
                        </span>
                    </div>
                    
                    {lastUpdated && (
                        <div className="flex items-center gap-2 text-sm text-text-muted">
                            <ClockIcon className="h-4 w-4" />
                            <span>Updated {lastUpdated}</span>
                        </div>
                    )}
                    
                    <button
                        onClick={() => setIsRealTimeEnabled(!isRealTimeEnabled)}
                        className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                            isRealTimeEnabled 
                                ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                                : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                        }`}
                    >
                        {isRealTimeEnabled ? 'Live Mode' : 'Manual Mode'}
                    </button>
                </div>
            </div>

            {/* Error Banner */}
            {error && (
                <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-4">
                    <p className="text-orange-400">{error}</p>
                </div>
            )}

            {/* Overall Risk Status */}
            <div className={`rounded-xl p-6 border ${riskColorClass}`}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <BoltIcon className="h-8 w-8" />
                        <div>
                            <h3 className="text-lg font-semibold">Current Risk Level</h3>
                            <p className="text-sm opacity-80">
                                Next hour prediction: {intelligenceData?.predictions?.predictions?.next_hour_risk?.risk_score || 'N/A'}
                            </p>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-3xl font-bold uppercase">{riskLevel}</div>
                        <div className="text-sm opacity-80">
                            {intelligenceData?.summary?.active_threats || 0} active threats
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Widgets Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                {/* Real-time Threat Map */}
                <div className="lg:col-span-2">
                    <div className="bg-card-bg rounded-xl p-6 border border-border-color h-96">
                        <div className="flex items-center gap-3 mb-4">
                            <GlobeAltIcon className="h-6 w-6 text-primary-accent" />
                            <h3 className="text-lg font-semibold text-text-primary">Global Threat Activity</h3>
                        </div>
                        <ThreatMap 
                            threats={intelligenceData?.real_time?.threats || []}
                            className="h-80"
                        />
                    </div>
                </div>

                {/* Real-time Alerts */}
                <div className="xl:col-span-1">
                    <RealTimeAlerts 
                        threats={intelligenceData?.real_time?.threats || []}
                    />
                </div>
            </div>

            {/* Intelligence Widgets */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                {/* Threat Intelligence Summary */}
                <ThreatIntelligenceWidget 
                    data={intelligenceData?.real_time}
                    loading={isLoading}
                />

                {/* Attack Patterns */}
                <AttackPatternsWidget 
                    data={intelligenceData?.patterns}
                    loading={isLoading}
                />

                {/* Predictions */}
                <PredictionsWidget 
                    data={intelligenceData?.predictions}
                    loading={isLoading}
                />
            </div>

            {/* Detailed Analytics */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                {/* Campaign Detection */}
                {intelligenceData?.patterns?.patterns?.attack_campaigns?.length > 0 && (
                    <div className="bg-card-bg rounded-xl p-6 border border-border-color">
                        <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                            <ExclamationTriangleIcon className="h-5 w-5 text-orange-500" />
                            Active Attack Campaigns
                        </h3>
                        <div className="space-y-4">
                            {intelligenceData.patterns.patterns.attack_campaigns.slice(0, 3).map((campaign, index) => (
                                <div key={campaign.campaign_id} className="p-4 bg-border-color/30 rounded-lg">
                                    <div className="flex items-center justify-between mb-2">
                                        <h4 className="font-medium text-text-primary">{campaign.attack_type}</h4>
                                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                                            campaign.severity === 'high' ? 'bg-red-500/20 text-red-400' : 'bg-orange-500/20 text-orange-400'
                                        }`}>
                                            {campaign.severity}
                                        </span>
                                    </div>
                                    <div className="text-sm text-text-muted grid grid-cols-2 gap-4">
                                        <div>Threats: {campaign.threat_count}</div>
                                        <div>Avg Risk: {(campaign.avg_risk * 100).toFixed(1)}%</div>
                                        <div className="col-span-2">Duration: {campaign.time_span}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Time Pattern Analysis */}
                {intelligenceData?.patterns?.patterns?.time_patterns && (
                    <div className="bg-card-bg rounded-xl p-6 border border-border-color">
                        <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                            <ChartBarIcon className="h-5 w-5 text-primary-accent" />
                            Temporal Attack Patterns
                        </h3>
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span className="text-text-muted">Peak Hour:</span>
                                    <span className="font-medium text-text-primary ml-2">
                                        {intelligenceData.patterns.patterns.time_patterns.peak_hour}:00
                                    </span>
                                </div>
                                <div>
                                    <span className="text-text-muted">Pattern Type:</span>
                                    <span className="font-medium text-text-primary ml-2">
                                        {intelligenceData.patterns.patterns.time_patterns.pattern_type}
                                    </span>
                                </div>
                            </div>
                            
                            {/* Hourly distribution visualization */}
                            <div className="mt-4">
                                <div className="text-xs text-text-muted mb-2">Hourly Activity Distribution</div>
                                <div className="flex items-end gap-1 h-16">
                                    {Array.from({length: 24}, (_, hour) => {
                                        const count = intelligenceData.patterns.patterns.time_patterns.hourly_distribution[hour] || 0;
                                        const maxCount = Math.max(...Object.values(intelligenceData.patterns.patterns.time_patterns.hourly_distribution));
                                        const height = maxCount > 0 ? (count / maxCount) * 100 : 0;
                                        
                                        return (
                                            <div 
                                                key={hour}
                                                className="bg-primary-accent/60 rounded-sm flex-1"
                                                style={{height: `${height}%`, minHeight: '2px'}}
                                                title={`${hour}:00 - ${count} threats`}
                                            />
                                        );
                                    })}
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Refresh Button */}
            <div className="flex justify-center">
                <button
                    onClick={fetchIntelligenceData}
                    disabled={isLoading}
                    className="px-6 py-2 bg-primary-accent text-white rounded-lg hover:bg-primary-accent/80 disabled:opacity-50 flex items-center gap-2"
                >
                    <EyeIcon className="h-4 w-4" />
                    {isLoading ? 'Refreshing...' : 'Refresh Intelligence'}
                </button>
            </div>
        </div>
    );
};

export default Intelligence;