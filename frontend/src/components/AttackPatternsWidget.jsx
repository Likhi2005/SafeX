import React from 'react';
import { 
    ExclamationTriangleIcon,
    ClockIcon,
    UsersIcon,
    ShieldCheckIcon
} from '@heroicons/react/24/outline';

const AttackPatternsWidget = ({ data, loading }) => {
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

    const patterns = data?.patterns || {};
    const campaigns = patterns.attack_campaigns || [];
    const clusters = patterns.threat_clusters || [];
    const timePatterns = patterns.time_patterns || {};
    const sourceAnalysis = patterns.source_analysis || {};

    return (
        <div className="bg-card-bg rounded-xl p-6 border border-border-color">
            <div className="flex items-center gap-3 mb-6">
                <ShieldCheckIcon className="h-6 w-6 text-orange-500" />
                <h3 className="text-lg font-semibold text-text-primary">Attack Patterns</h3>
            </div>

            <div className="space-y-6">
                {/* Campaign Detection */}
                {campaigns.length > 0 && (
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-text-primary flex items-center gap-2">
                            <ExclamationTriangleIcon className="h-4 w-4 text-orange-500" />
                            Active Campaigns
                        </h4>
                        <div className="space-y-2">
                            {campaigns.slice(0, 2).map((campaign, index) => (
                                <div key={index} className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="text-sm font-medium text-text-primary">
                                            {campaign.attack_type}
                                        </div>
                                        <span className={`px-2 py-1 rounded text-xs ${
                                            campaign.severity === 'high' 
                                                ? 'bg-red-500/20 text-red-400'
                                                : 'bg-orange-500/20 text-orange-400'
                                        }`}>
                                            {campaign.severity}
                                        </span>
                                    </div>
                                    <div className="grid grid-cols-2 gap-2 text-xs text-text-muted">
                                        <div>Threats: {campaign.threat_count}</div>
                                        <div>Avg Risk: {(campaign.avg_risk * 100).toFixed(0)}%</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Threat Clusters */}
                {clusters.length > 0 && (
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-text-primary">Threat Clusters</h4>
                        <div className="space-y-2">
                            {clusters.slice(0, 3).map((cluster, index) => (
                                <div key={index} className="flex justify-between items-center p-2 bg-border-color/10 rounded">
                                    <div className="text-sm">
                                        <div className="text-text-primary font-medium">Cluster {cluster.cluster_id}</div>
                                        <div className="text-text-muted text-xs">{cluster.pattern}</div>
                                    </div>
                                    <div className="text-right text-xs">
                                        <div className="text-text-primary font-medium">{cluster.size}</div>
                                        <div className="text-text-muted">threats</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Time Patterns */}
                {timePatterns.peak_hour !== undefined && (
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-text-primary flex items-center gap-2">
                            <ClockIcon className="h-4 w-4 text-primary-accent" />
                            Temporal Patterns
                        </h4>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div className="p-3 bg-primary-accent/10 rounded-lg">
                                <div className="text-primary-accent font-medium">{timePatterns.peak_hour}:00</div>
                                <div className="text-text-muted text-xs">Peak Hour</div>
                            </div>
                            <div className="p-3 bg-border-color/20 rounded-lg">
                                <div className="text-text-primary font-medium capitalize">{timePatterns.pattern_type}</div>
                                <div className="text-text-muted text-xs">Distribution</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Source Analysis */}
                {sourceAnalysis.unique_ips && (
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-text-primary flex items-center gap-2">
                            <UsersIcon className="h-4 w-4 text-secondary-accent" />
                            Source Analysis
                        </h4>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div className="p-3 bg-secondary-accent/10 rounded-lg">
                                <div className="text-secondary-accent font-medium">{sourceAnalysis.unique_ips}</div>
                                <div className="text-text-muted text-xs">Unique IPs</div>
                            </div>
                            <div className="p-3 bg-border-color/20 rounded-lg">
                                <div className="text-text-primary font-medium">{sourceAnalysis.repeat_attackers?.length || 0}</div>
                                <div className="text-text-muted text-xs">Repeat Attackers</div>
                            </div>
                        </div>
                        
                        {/* Top Countries */}
                        {sourceAnalysis.top_countries?.length > 0 && (
                            <div className="space-y-2">
                                <div className="text-xs font-medium text-text-muted">Top Source Countries</div>
                                {sourceAnalysis.top_countries.slice(0, 3).map((country, index) => (
                                    <div key={index} className="flex justify-between items-center text-xs">
                                        <span className="text-text-muted">{country.country}</span>
                                        <span className="text-text-primary font-medium">{country.count}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* No Data Message */}
                {campaigns.length === 0 && clusters.length === 0 && !timePatterns.peak_hour && (
                    <div className="text-center py-8 text-text-muted">
                        <ShieldCheckIcon className="h-12 w-12 mx-auto mb-3 opacity-50" />
                        <p className="text-sm">No attack patterns detected</p>
                        <p className="text-xs mt-1">Analysis requires more data</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AttackPatternsWidget;