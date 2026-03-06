import React from 'react';
import {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    XCircleIcon,
    ClockIcon,
    ShieldCheckIcon,
    ChartBarIcon
} from '@heroicons/react/24/outline';

const ResultPanel = ({ result, isLoading }) => {
    if (isLoading) {
        return (
            <div className="bg-card-bg rounded-xl p-6 border border-border-color">
                <div className="flex items-center justify-center h-64">
                    <div className="text-center space-y-4">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-accent mx-auto"></div>
                        <div className="space-y-2">
                            <p className="text-text-primary font-medium">Analyzing prompt safety...</p>
                            <p className="text-text-muted text-sm">Running security filters and ML models</p>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!result) {
        return (
            <div className="bg-card-bg rounded-xl p-6 border border-border-color border-dashed">
                <div className="text-center py-12">
                    <ShieldCheckIcon className="h-16 w-16 text-text-muted mx-auto mb-4" />
                    <p className="text-text-muted text-lg">Enter a prompt above to start safety analysis</p>
                    <p className="text-text-muted text-sm mt-2">Our AI safety gateway will check for potential risks</p>
                </div>
            </div>
        );
    }

    const getDecisionBadge = (decision) => {
        const badges = {
            'ALLOW': {
                color: 'bg-secondary-accent text-white',
                icon: CheckCircleIcon,
                glow: 'shadow-glow-green'
            },
            'SANITIZE': {
                color: 'bg-warning-color text-white',
                icon: ExclamationTriangleIcon,
                glow: 'shadow-lg'
            },
            'BLOCK': {
                color: 'bg-danger-color text-white',
                icon: XCircleIcon,
                glow: 'shadow-glow-red'
            }
        };

        const badge = badges[decision] || badges['BLOCK'];
        const Icon = badge.icon;

        return (
            <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full ${badge.color} ${badge.glow}`}>
                <Icon className="h-5 w-5" />
                <span className="font-semibold">{decision}</span>
            </div>
        );
    };

    const getRiskScoreColor = (score) => {
        if (score >= 0.7) return 'bg-danger-color';
        if (score >= 0.4) return 'bg-warning-color';
        return 'bg-secondary-accent';
    };

    const getRiskLevel = (score) => {
        if (score >= 0.8) return 'CRITICAL';
        if (score >= 0.6) return 'HIGH';
        if (score >= 0.4) return 'MEDIUM';
        if (score >= 0.2) return 'LOW';
        return 'MINIMAL';
    };

    return (
        <div className="space-y-6">
            {/* Main Result Card */}
            <div className="bg-card-bg rounded-xl p-6 border border-border-color">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-text-primary">Analysis Result</h2>
                    <div className="flex items-center space-x-4">
                        {result.latency_ms && (
                            <div className="flex items-center space-x-1 text-text-muted">
                                <ClockIcon className="h-4 w-4" />
                                <span className="text-sm">{result.latency_ms}ms</span>
                            </div>
                        )}
                        {getDecisionBadge(result.decision)}
                    </div>
                </div>

                {/* Risk Score Section */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <span className="text-text-primary font-medium">Risk Score</span>
                        <div className="flex items-center space-x-2">
                            <span className="text-2xl font-bold text-text-primary">
                                {(result.risk_score * 100).toFixed(1)}%
                            </span>
                            <span className={`px-2 py-1 rounded text-xs font-semibold ${result.risk_score >= 0.7 ? 'bg-danger-color text-white' :
                                    result.risk_score >= 0.4 ? 'bg-warning-color text-white' :
                                        'bg-secondary-accent text-white'
                                }`}>
                                {getRiskLevel(result.risk_score)}
                            </span>
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-border-color rounded-full h-3">
                        <div
                            className={`h-3 rounded-full transition-all duration-500 ${getRiskScoreColor(result.risk_score)}`}
                            style={{ width: `${Math.max(result.risk_score * 100, 2)}%` }}
                        ></div>
                    </div>

                    {/* Risk Level Indicators */}
                    <div className="flex justify-between text-xs text-text-muted">
                        <span>Safe</span>
                        <span>Low</span>
                        <span>Medium</span>
                        <span>High</span>
                        <span>Critical</span>
                    </div>
                </div>

                {/* Detection Reasons */}
                {result.reasons && result.reasons.length > 0 && (
                    <div className="mt-6 pt-6 border-t border-border-color">
                        <h3 className="text-lg font-medium text-text-primary mb-3">Detection Details</h3>
                        <div className="space-y-2">
                            {result.reasons.map((reason, index) => (
                                <div key={index} className="flex items-start space-x-2 p-3 bg-border-color bg-opacity-50 rounded-lg">
                                    <ExclamationTriangleIcon className="h-5 w-5 text-warning-color mt-0.5 flex-shrink-0" />
                                    <span className="text-text-primary">{reason}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Filter Results */}
                {result.filter_results && (
                    <div className="mt-6 pt-6 border-t border-border-color">
                        <h3 className="text-lg font-medium text-text-primary mb-3">Filter Analysis</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {Object.entries(result.filter_results).map(([filterName, filterResult]) => (
                                <div key={filterName} className="bg-border-color bg-opacity-30 rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-text-primary font-medium capitalize">
                                            {filterName.replace('_', ' ')}
                                        </span>
                                        <ChartBarIcon className="h-4 w-4 text-primary-accent" />
                                    </div>
                                    <div className="space-y-1">
                                        <div className="flex justify-between text-sm">
                                            <span className="text-text-muted">Risk Score:</span>
                                            <span className="text-text-primary font-medium">
                                                {(filterResult.risk_score * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                        {filterResult.reason && (
                                            <p className="text-xs text-text-muted mt-1">{filterResult.reason}</p>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Response Panel */}
            {result.response && (
                <div className="bg-card-bg rounded-xl p-6 border border-border-color">
                    <h3 className="text-lg font-semibold text-text-primary mb-4">LLM Response</h3>
                    <div className="bg-dark-bg rounded-lg p-4 border border-border-color">
                        <p className="text-text-primary whitespace-pre-wrap">{result.response}</p>
                    </div>
                </div>
            )}

            {/* Blocked Content Warning */}
            {result.decision === 'BLOCK' && (
                <div className="bg-danger-color bg-opacity-10 border border-danger-color border-opacity-30 rounded-xl p-6">
                    <div className="flex items-start space-x-3">
                        <XCircleIcon className="h-6 w-6 text-danger-color flex-shrink-0 mt-0.5" />
                        <div>
                            <h3 className="text-lg font-semibold text-danger-color mb-2">Content Blocked</h3>
                            <p className="text-text-primary">
                                This prompt has been blocked due to security policy violations.
                                The request was not forwarded to the LLM for safety reasons.
                            </p>
                            {result.reasons && result.reasons.length > 0 && (
                                <div className="mt-3">
                                    <p className="text-text-muted text-sm mb-2">Blocked for:</p>
                                    <ul className="list-disc list-inside space-y-1">
                                        {result.reasons.map((reason, index) => (
                                            <li key={index} className="text-text-muted text-sm">{reason}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Sanitization Notice */}
            {result.decision === 'SANITIZE' && result.prompt_modified && (
                <div className="bg-warning-color bg-opacity-10 border border-warning-color border-opacity-30 rounded-xl p-6">
                    <div className="flex items-start space-x-3">
                        <ExclamationTriangleIcon className="h-6 w-6 text-warning-color flex-shrink-0 mt-0.5" />
                        <div>
                            <h3 className="text-lg font-semibold text-warning-color mb-2">Content Sanitized</h3>
                            <p className="text-text-primary mb-3">
                                The prompt was modified to remove potentially harmful content before processing.
                            </p>

                            {result.original_prompt && result.processed_prompt && (
                                <div className="space-y-3">
                                    <div>
                                        <p className="text-text-muted text-sm mb-1">Original:</p>
                                        <div className="bg-dark-bg rounded p-3 border border-border-color">
                                            <p className="text-text-primary text-sm">{result.original_prompt}</p>
                                        </div>
                                    </div>

                                    <div>
                                        <p className="text-text-muted text-sm mb-1">Sanitized:</p>
                                        <div className="bg-dark-bg rounded p-3 border border-border-color">
                                            <p className="text-text-primary text-sm">{result.processed_prompt}</p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ResultPanel;