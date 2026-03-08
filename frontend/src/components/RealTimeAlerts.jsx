import React, { useState, useEffect } from 'react';
import { 
    ExclamationTriangleIcon,
    CheckCircleIcon,
    XCircleIcon,
    ClockIcon,
    EyeIcon,
    EyeSlashIcon
} from '@heroicons/react/24/outline';

const RealTimeAlerts = ({ threats = [] }) => {
    const [alerts, setAlerts] = useState([]);
    const [isMinimized, setIsMinimized] = useState(false);
    const [filter, setFilter] = useState('all'); // all, critical, high, blocked

    useEffect(() => {
        // Convert threats to alerts format and sort by severity
        const newAlerts = threats
            .filter(threat => {
                if (filter === 'all') return true;
                if (filter === 'critical') return threat.severity === 'critical';
                if (filter === 'high') return threat.severity === 'high' || threat.severity === 'critical';
                if (filter === 'blocked') return threat.blocked;
                return true;
            })
            .sort((a, b) => {
                // Sort by severity and time
                const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
                const aSeverity = severityOrder[a.severity] || 0;
                const bSeverity = severityOrder[b.severity] || 0;
                
                if (aSeverity !== bSeverity) return bSeverity - aSeverity;
                return new Date(b.timestamp) - new Date(a.timestamp);
            })
            .slice(0, 10); // Keep only recent 10 alerts

        setAlerts(newAlerts);
    }, [threats, filter]);

    const getAlertIcon = (threat) => {
        if (threat.blocked) {
            return <XCircleIcon className="h-5 w-5 text-red-500" />;
        }
        
        switch (threat.severity) {
            case 'critical':
                return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
            case 'high':
                return <ExclamationTriangleIcon className="h-5 w-5 text-orange-500" />;
            case 'medium':
                return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
            case 'low':
                return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
            default:
                return <CheckCircleIcon className="h-5 w-5 text-gray-500" />;
        }
    };

    const getAlertColor = (threat) => {
        if (threat.blocked) {
            return 'border-l-red-500 bg-red-500/5';
        }
        
        switch (threat.severity) {
            case 'critical':
                return 'border-l-red-500 bg-red-500/5';
            case 'high':
                return 'border-l-orange-500 bg-orange-500/5';
            case 'medium':
                return 'border-l-yellow-500 bg-yellow-500/5';
            case 'low':
                return 'border-l-green-500 bg-green-500/5';
            default:
                return 'border-l-gray-500 bg-gray-500/5';
        }
    };

    const formatTimeAgo = (timestamp) => {
        const now = new Date();
        const time = new Date(timestamp);
        const diffMs = now - time;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return time.toLocaleDateString();
    };

    const getFilterCounts = () => {
        const counts = {
            all: threats.length,
            critical: threats.filter(t => t.severity === 'critical').length,
            high: threats.filter(t => t.severity === 'high' || t.severity === 'critical').length,
            blocked: threats.filter(t => t.blocked).length
        };
        return counts;
    };

    const counts = getFilterCounts();

    if (isMinimized) {
        return (
            <div className="bg-card-bg rounded-xl border border-border-color">
                <div className="p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <ExclamationTriangleIcon className="h-5 w-5 text-primary-accent" />
                        <span className="font-medium text-text-primary">Real-time Alerts</span>
                        {counts.all > 0 && (
                            <span className="bg-primary-accent text-white text-xs px-2 py-1 rounded-full">
                                {counts.all}
                            </span>
                        )}
                    </div>
                    <button
                        onClick={() => setIsMinimized(false)}
                        className="text-text-muted hover:text-text-primary transition-colors"
                    >
                        <EyeIcon className="h-4 w-4" />
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-card-bg rounded-xl border border-border-color">
            {/* Header */}
            <div className="p-4 border-b border-border-color">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <ExclamationTriangleIcon className="h-5 w-5 text-primary-accent" />
                        <h3 className="font-semibold text-text-primary">Real-time Alerts</h3>
                    </div>
                    <button
                        onClick={() => setIsMinimized(true)}
                        className="text-text-muted hover:text-text-primary transition-colors"
                    >
                        <EyeSlashIcon className="h-4 w-4" />
                    </button>
                </div>
                
                {/* Filter Buttons */}
                <div className="flex gap-2 text-sm">
                    {[
                        { key: 'all', label: 'All', count: counts.all },
                        { key: 'critical', label: 'Critical', count: counts.critical },
                        { key: 'high', label: 'High+', count: counts.high },
                        { key: 'blocked', label: 'Blocked', count: counts.blocked }
                    ].map(filterOption => (
                        <button
                            key={filterOption.key}
                            onClick={() => setFilter(filterOption.key)}
                            className={`px-3 py-1 rounded-lg font-medium transition-colors ${
                                filter === filterOption.key
                                    ? 'bg-primary-accent text-white'
                                    : 'bg-border-color/50 text-text-muted hover:text-text-primary'
                            }`}
                        >
                            {filterOption.label}
                            {filterOption.count > 0 && (
                                <span className="ml-1 text-xs">
                                    ({filterOption.count})
                                </span>
                            )}
                        </button>
                    ))}
                </div>
            </div>

            {/* Alerts List */}
            <div className="p-4">
                <div className="space-y-3 max-h-80 overflow-y-auto">
                    {alerts.length > 0 ? (
                        alerts.map((alert, index) => (
                            <div 
                                key={`${alert.id}-${index}`} 
                                className={`p-3 rounded-lg border-l-4 ${getAlertColor(alert)} animate-slideIn`}
                                style={{ animationDelay: `${index * 50}ms` }}
                            >
                                <div className="flex items-start gap-3">
                                    {getAlertIcon(alert)}
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center justify-between mb-1">
                                            <h4 className="text-sm font-medium text-text-primary truncate">
                                                {alert.attack_type || 'Unknown Threat'}
                                            </h4>
                                            <span className="text-xs text-text-muted ml-2 flex-shrink-0">
                                                {formatTimeAgo(alert.timestamp)}
                                            </span>
                                        </div>
                                        
                                        <div className="flex items-center justify-between text-xs">
                                            <span className="text-text-muted">
                                                Risk: {(alert.risk_score * 100).toFixed(0)}% • {alert.country}
                                            </span>
                                            <div className="flex items-center gap-2">
                                                {alert.blocked && (
                                                    <span className="bg-red-500/20 text-red-400 px-2 py-1 rounded text-xs font-medium">
                                                        BLOCKED
                                                    </span>
                                                )}
                                                <span className={`px-2 py-1 rounded text-xs font-medium capitalize ${
                                                    alert.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                                                    alert.severity === 'high' ? 'bg-orange-500/20 text-orange-400' :
                                                    alert.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                                                    'bg-green-500/20 text-green-400'
                                                }`}>
                                                    {alert.severity}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="text-center py-6 text-text-muted">
                            <CheckCircleIcon className="h-12 w-12 mx-auto mb-3 opacity-50" />
                            <p className="text-sm">No active alerts</p>
                            <p className="text-xs mt-1">
                                {filter === 'all' ? 'All systems secure' : `No ${filter} threats detected`}
                            </p>
                        </div>
                    )}
                </div>
            </div>

            {alerts.length > 0 && (
                <div className="px-4 pb-4 flex justify-between items-center text-xs text-text-muted">
                    <span>Showing {alerts.length} of {threats.length} alerts</span>
                    <div className="flex items-center gap-1">
                        <ClockIcon className="h-3 w-3" />
                        <span>Auto-refresh every 30s</span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RealTimeAlerts;