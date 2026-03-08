import React from 'react';
import { 
    ChartBarIcon, 
    ExclamationTriangleIcon,
    CheckCircleIcon,
    ClockIcon
} from '@heroicons/react/24/outline';

const ThreatIntelligenceWidget = ({ data, loading }) => {
    if (loading) {
        return (
            <div className="bg-card-bg rounded-xl p-6 border border-border-color">
                <div className="animate-pulse">
                    <div className="h-4 bg-border-color rounded w-3/4 mb-4"></div>
                    <div className="space-y-3">
                        <div className="h-8 bg-border-color rounded"></div>
                        <div className="h-6 bg-border-color rounded w-1/2"></div>
                        <div className="h-6 bg-border-color rounded w-2/3"></div>
                    </div>
                </div>
            </div>
        );
    }

    const stats = data?.stats || {};
    const threats = data?.threats || [];
    
    const criticalThreats = stats.critical_threats || 0;
    const totalThreats = stats.total_threats || 0;
    const blockRate = stats.block_rate || 0;
    const avgRisk = stats.avg_risk_score || 0;

    return (
        <div className="bg-card-bg rounded-xl p-6 border border-border-color">
            <div className="flex items-center gap-3 mb-6">
                <ChartBarIcon className="h-6 w-6 text-primary-accent" />
                <h3 className="text-lg font-semibold text-text-primary">Threat Intelligence</h3>
            </div>

            <div className="space-y-6">
                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-border-color/20 rounded-lg">
                        <div className="text-2xl font-bold text-text-primary">{totalThreats}</div>
                        <div className="text-sm text-text-muted">Total Threats</div>
                    </div>
                    
                    <div className="p-4 bg-red-500/10 rounded-lg">
                        <div className="text-2xl font-bold text-red-400">{criticalThreats}</div>
                        <div className="text-sm text-text-muted">Critical</div>
                    </div>
                </div>

                {/* Block Rate */}
                <div className="space-y-2">
                    <div className="flex justify-between items-center">
                        <span className="text-sm font-medium text-text-primary">Block Rate</span>
                        <span className="text-sm text-text-muted">{blockRate.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-border-color rounded-full h-2">
                        <div 
                            className="bg-primary-accent h-2 rounded-full transition-all duration-300"
                            style={{ width: `${blockRate}%` }}
                        />
                    </div>
                </div>

                {/* Average Risk */}
                <div className="space-y-2">
                    <div className="flex justify-between items-center">
                        <span className="text-sm font-medium text-text-primary">Avg Risk Score</span>
                        <span className="text-sm text-text-muted">{(avgRisk * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-border-color rounded-full h-2">
                        <div 
                            className={`h-2 rounded-full transition-all duration-300 ${
                                avgRisk >= 0.7 ? 'bg-red-500' : 
                                avgRisk >= 0.4 ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${avgRisk * 100}%` }}
                        />
                    </div>
                </div>

                {/* Attack Distribution */}
                {stats.attack_distribution && (
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-text-primary">Top Attack Types</h4>
                        <div className="space-y-2">
                            {Object.entries(stats.attack_distribution).slice(0, 3).map(([type, count]) => (
                                <div key={type} className="flex justify-between items-center text-sm">
                                    <span className="text-text-muted capitalize">{type.replace('_', ' ')}</span>
                                    <span className="font-medium text-text-primary">{count}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Recent Activity */}
                <div className="space-y-3">
                    <h4 className="text-sm font-medium text-text-primary">Recent Activity</h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                        {threats.slice(0, 3).map((threat, index) => (
                            <div key={index} className="flex items-center gap-3 p-2 bg-border-color/10 rounded">
                                {threat.blocked ? (
                                    <ExclamationTriangleIcon className="h-4 w-4 text-red-500 flex-shrink-0" />
                                ) : (
                                    <CheckCircleIcon className="h-4 w-4 text-green-500 flex-shrink-0" />
                                )}
                                <div className="text-xs text-text-muted overflow-hidden">
                                    <div className="font-medium text-text-primary">
                                        {threat.attack_type || 'Unknown'}
                                    </div>
                                    <div className="truncate">
                                        Risk: {(threat.risk_score * 100).toFixed(0)}% • {threat.country}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ThreatIntelligenceWidget;