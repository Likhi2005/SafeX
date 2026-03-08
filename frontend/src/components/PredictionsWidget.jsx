import React from 'react';
import { 
    BoltIcon,
    ArrowTrendingUpIcon,
    ExclamationTriangleIcon,
    ClockIcon
} from '@heroicons/react/24/outline';

const PredictionsWidget = ({ data, loading }) => {
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

    const predictions = data?.predictions || {};
    const nextHourRisk = predictions.next_hour_risk || {};
    const trendingAttacks = predictions.trending_attacks || [];
    const riskHotspots = predictions.risk_hotspots || [];
    const threatForecast = predictions.threat_forecast || {};

    const getRiskColor = (level) => {
        switch (level) {
            case 'high': return 'text-red-500 bg-red-500/10 border-red-500/20';
            case 'medium': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
            case 'low': return 'text-green-500 bg-green-500/10 border-green-500/20';
            default: return 'text-gray-500 bg-gray-500/10 border-gray-500/20';
        }
    };

    const getTrendIcon = (trend) => {
        if (trend === 'increasing') {
            return <ArrowTrendingUpIcon className="h-4 w-4 text-red-500" />;
        }
        return <ClockIcon className="h-4 w-4 text-gray-500" />;
    };

    return (
        <div className="bg-card-bg rounded-xl p-6 border border-border-color">
            <div className="flex items-center gap-3 mb-6">
                <BoltIcon className="h-6 w-6 text-purple-500" />
                <h3 className="text-lg font-semibold text-text-primary">Threat Predictions</h3>
            </div>

            <div className="space-y-6">
                {/* Next Hour Risk Prediction */}
                {nextHourRisk.level && (
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-text-primary">Next Hour Risk Level</h4>
                        <div className={`p-4 rounded-lg border ${getRiskColor(nextHourRisk.level)}`}>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-lg font-bold uppercase">{nextHourRisk.level}</span>
                                {getTrendIcon(nextHourRisk.trend)}
                            </div>
                            <div className="text-sm opacity-80">
                                Risk Score: {(nextHourRisk.risk_score * 100).toFixed(1)}%
                            </div>
                            <div className="text-xs opacity-60 mt-1">
                                Confidence: {(nextHourRisk.confidence * 100).toFixed(0)}%
                            </div>
                        </div>
                    </div>
                )}

                {/* 24-Hour Forecast */}
                {threatForecast.expected_threats_24h && (
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-text-primary">24-Hour Forecast</h4>
                        <div className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-lg">
                            <div className="text-2xl font-bold text-purple-400 mb-1">
                                {threatForecast.expected_threats_24h}
                            </div>
                            <div className="text-sm text-text-muted mb-2">Expected Threats</div>
                            {threatForecast.confidence_interval && (
                                <div className="text-xs text-text-muted">
                                    Range: {threatForecast.confidence_interval[0]} - {threatForecast.confidence_interval[1]}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Trending Attack Types */}
                {trendingAttacks.length > 0 && (
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-text-primary">Trending Attacks</h4>
                        <div className="space-y-2">
                            {trendingAttacks.slice(0, 3).map((attack, index) => (
                                <div key={index} className="flex items-center justify-between p-2 bg-orange-500/10 rounded">
                                    <span className="text-sm text-text-primary capitalize">
                                        {attack.replace('_', ' ')}
                                    </span>
                                    <ArrowTrendingUpIcon className="h-4 w-4 text-orange-500" />
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Risk Hotspots */}
                {riskHotspots.length > 0 && (
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-text-primary">Risk Hotspots</h4>
                        <div className="space-y-2">
                            {riskHotspots.slice(0, 3).map((hotspot, index) => (
                                <div key={index} className="flex justify-between items-center p-2 bg-border-color/10 rounded">
                                    <div className="text-sm">
                                        <div className="text-text-primary font-medium">{hotspot.location}</div>
                                        <div className="text-text-muted text-xs">{hotspot.threat_count} threats</div>
                                    </div>
                                    <div className="text-right">
                                        <div className={`text-sm font-medium ${
                                            hotspot.risk_level >= 0.7 ? 'text-red-500' :
                                            hotspot.risk_level >= 0.4 ? 'text-yellow-500' : 'text-green-500'
                                        }`}>
                                            {(hotspot.risk_level * 100).toFixed(0)}%
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Key Risks */}
                {threatForecast.key_risks?.length > 0 && (
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-text-primary">Key Risk Factors</h4>
                        <div className="space-y-1">
                            {threatForecast.key_risks.map((risk, index) => (
                                <div key={index} className="flex items-center gap-2 text-sm text-text-muted">
                                    <ExclamationTriangleIcon className="h-3 w-3 text-yellow-500" />
                                    <span>{risk}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* No Predictions Message */}
                {!nextHourRisk.level && !threatForecast.expected_threats_24h && trendingAttacks.length === 0 && (
                    <div className="text-center py-8 text-text-muted">
                        <BoltIcon className="h-12 w-12 mx-auto mb-3 opacity-50" />
                        <p className="text-sm">No predictions available</p>
                        <p className="text-xs mt-1">Gathering data for analysis</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PredictionsWidget;