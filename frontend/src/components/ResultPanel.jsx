import React from 'react';
import {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    XCircleIcon,
    ClockIcon,
    ShieldCheckIcon,
    ChartBarIcon,
    EyeIcon,
    DocumentIcon,
    ArrowTopRightOnSquareIcon
} from '@heroicons/react/24/outline';

const ResultPanel = ({ result, isLoading }) => {
    if (isLoading) {
        return (
            <div className="bg-card rounded-xl p-8 border border-border">
                <div className="flex items-center justify-center h-64">
                    <div className="text-center space-y-6">
                        <div className="relative">
                            <div className="animate-spin rounded-full h-16 w-16 border-4 border-border border-t-primary mx-auto"></div>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <ShieldCheckIcon className="h-6 w-6 text-primary" />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <p className="text-textPrimary font-semibold text-lg">Analyzing prompt safety...</p>
                            <p className="text-textMuted text-sm">Running security filters and ML models</p>
                            <div className="flex items-center justify-center space-x-2 mt-4">
                                <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                                <div className="w-2 h-2 bg-primary rounded-full animate-pulse delay-75"></div>
                                <div className="w-2 h-2 bg-primary rounded-full animate-pulse delay-150"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!result) {
        return (
            <div className="bg-card rounded-xl p-8 border border-border border-dashed">
                <div className="text-center py-16">
                    <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                        <ShieldCheckIcon className="h-10 w-10 text-primary" />
                    </div>
                    <h3 className="text-textPrimary text-xl font-semibold mb-2">Ready for Safety Analysis</h3>
                    <p className="text-textMuted text-base mb-6 max-w-md mx-auto">
                        Enter a prompt above to start comprehensive AI safety analysis using our advanced security filters
                    </p>
                    <div className="flex items-center justify-center space-x-6 text-sm text-textMuted">
                        <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-primary rounded-full"></div>
                            <span>Toxicity Detection</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-secondary rounded-full"></div>
                            <span>Injection Prevention</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-warning rounded-full"></div>
                            <span>Content Analysis</span>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    const getDecisionBadge = (decision) => {
        const badges = {
            'ALLOW': {
                color: 'bg-secondary text-white',
                textColor: 'text-secondary',
                bgLight: 'bg-secondary/10',
                icon: CheckCircleIcon,
                label: 'Safe'
            },
            'SANITIZE': {
                color: 'bg-warning text-black',
                textColor: 'text-warning',
                bgLight: 'bg-warning/10',
                icon: ExclamationTriangleIcon,
                label: 'Violation'
            },
            'BLOCK': {
                color: 'bg-danger text-white',
                textColor: 'text-danger',
                bgLight: 'bg-danger/10',
                icon: XCircleIcon,
                label: 'Violation'
            }
        };

        const badge = badges[decision] || badges['BLOCK'];
        const Icon = badge.icon;

        return (
            <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${badge.color}`}>
                <Icon className="h-4 w-4" />
                <span>{badge.label}</span>
            </div>
        );
    };

    const getRiskScoreColor = (score) => {
        if (score >= 0.7) return 'text-danger';
        if (score >= 0.4) return 'text-warning';
        return 'text-secondary';
    };

    const getProgressBarColor = (score) => {
        if (score >= 0.7) return 'bg-danger';
        if (score >= 0.4) return 'bg-warning';
        return 'bg-secondary';
    };

    const formatTimestamp = () => {
        return new Date().toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
    };

    const truncateText = (text, maxLength = 50) => {
        return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
    };

    return (
        <div className="space-y-6">
            {/* Header Section */}
            <div className="bg-card rounded-xl p-6 border border-border">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                            <ShieldCheckIcon className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold text-textPrimary">LLM Safety Analysis</h2>
                            <p className="text-sm text-textMuted">Real-time security assessment completed</p>
                        </div>
                    </div>
                    <div className="flex items-center space-x-4">
                        {result.latency_ms && (
                            <div className="flex items-center space-x-1 text-textMuted text-sm">
                                <ClockIcon className="h-4 w-4" />
                                <span>{result.latency_ms}ms</span>
                            </div>
                        )}
                        {getDecisionBadge(result.decision)}
                    </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-3 gap-6">
                    <div className="text-center">
                        <div className={`text-3xl font-bold ${getRiskScoreColor(result.risk_score)} mb-1`}>
                            {(result.risk_score * 100).toFixed(1)}%
                        </div>
                        <div className="text-sm text-textMuted">Overall Safety Score</div>
                    </div>
                    <div className="text-center">
                        <div className="text-3xl font-bold text-primary mb-1">
                            {Object.keys(result.filter_results || {}).length}
                        </div>
                        <div className="text-sm text-textMuted">Security Checks</div>
                    </div>
                    <div className="text-center">
                        <div className="text-3xl font-bold text-textPrimary mb-1">
                            {result.latency_ms || 0}<span className="text-lg text-textMuted">ms</span>
                        </div>
                        <div className="text-sm text-textMuted">Response Time</div>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-6">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-textPrimary">Risk Level</span>
                        <span className={`text-sm font-medium ${getRiskScoreColor(result.risk_score)}`}>
                            {result.risk_score >= 0.8 ? 'CRITICAL' :
                                result.risk_score >= 0.6 ? 'HIGH' :
                                    result.risk_score >= 0.4 ? 'MEDIUM' :
                                        result.risk_score >= 0.2 ? 'LOW' : 'MINIMAL'}
                        </span>
                    </div>
                    <div className="w-full bg-border rounded-full h-2">
                        <div
                            className={`h-2 rounded-full transition-all duration-1000 ${getProgressBarColor(result.risk_score)}`}
                            style={{ width: `${Math.max(result.risk_score * 100, 2)}%` }}
                        ></div>
                    </div>
                </div>
            </div>

            {/* Data Table - Guardrail Style */}
            <div className="bg-card rounded-xl border border-border overflow-hidden">
                <div className="px-6 py-4 border-b border-border">
                    <h3 className="text-lg font-semibold text-textPrimary">Real-time LLM Input/Output Log</h3>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-background">
                            <tr>
                                <th className="text-left p-4 text-textMuted font-medium text-sm">Timestamp ↑</th>
                                <th className="text-left p-4 text-textMuted font-medium text-sm">Source Model</th>
                                <th className="text-left p-4 text-textMuted font-medium text-sm">Prompt (Truncated)</th>
                                <th className="text-left p-4 text-textMuted font-medium text-sm">Output (Truncated)</th>
                                <th className="text-left p-4 text-textMuted font-medium text-sm">Safety Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr className="border-b border-border hover:bg-background/50">
                                <td className="p-4 text-textPrimary text-sm font-mono">
                                    {formatTimestamp()}
                                </td>
                                <td className="p-4 text-textPrimary text-sm">
                                    ShieldGPT
                                </td>
                                <td className="p-4 text-textPrimary text-sm max-w-xs">
                                    <div className="flex items-center space-x-2">
                                        <span className="text-primary">"</span>
                                        <span>{truncateText(result.prompt || "Test prompt", 40)}</span>
                                        <span className="text-primary">"</span>
                                    </div>
                                </td>
                                <td className="p-4 text-textPrimary text-sm max-w-xs">
                                    {result.response ? (
                                        <div className="flex items-center space-x-2">
                                            <span className="text-primary">"</span>
                                            <span>{truncateText(result.response, 40)}</span>
                                            <span className="text-primary">"</span>
                                        </div>
                                    ) : (
                                        <span className="text-textMuted italic">No response generated</span>
                                    )}
                                </td>
                                <td className="p-4">
                                    {getDecisionBadge(result.decision)}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Filter Results Grid */}
            {result.filter_results && Object.keys(result.filter_results).length > 0 && (
                <div className="bg-card rounded-xl p-6 border border-border">
                    <h3 className="text-lg font-semibold text-textPrimary mb-4">Security Filter Analysis</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {Object.entries(result.filter_results).map(([filterName, filterResult]) => {
                            const riskColor = filterResult.risk_score >= 0.7 ? 'border-danger bg-danger/5' :
                                filterResult.risk_score >= 0.4 ? 'border-warning bg-warning/5' :
                                    'border-secondary bg-secondary/5';

                            return (
                                <div key={filterName} className={`rounded-lg p-4 border ${riskColor}`}>
                                    <div className="flex items-center justify-between mb-3">
                                        <span className="text-textPrimary font-medium capitalize text-sm">
                                            {filterName.replace('_', ' ')}
                                        </span>
                                        <ChartBarIcon className="h-4 w-4 text-primary" />
                                    </div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center">
                                            <span className="text-textMuted text-xs">Risk Score:</span>
                                            <span className={`font-bold text-sm ${getRiskScoreColor(filterResult.risk_score)}`}>
                                                {(filterResult.risk_score * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                        <div className="w-full bg-border rounded-full h-1.5">
                                            <div
                                                className={`h-1.5 rounded-full transition-all duration-500 ${getProgressBarColor(filterResult.risk_score)}`}
                                                style={{ width: `${Math.max(filterResult.risk_score * 100, 2)}%` }}
                                            ></div>
                                        </div>
                                        {filterResult.reason && (
                                            <p className="text-xs text-textMuted mt-2 line-clamp-2">{filterResult.reason}</p>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Detection Details */}
            {result.reasons && result.reasons.length > 0 && (
                <div className="bg-card rounded-xl p-6 border border-border">
                    <h3 className="text-lg font-semibold text-textPrimary mb-4">Detection Details</h3>
                    <div className="space-y-3">
                        {result.reasons.map((reason, index) => (
                            <div key={index} className="flex items-start space-x-3 p-4 bg-warning/5 border border-warning/20 rounded-lg">
                                <div className="w-6 h-6 bg-warning/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                    <ExclamationTriangleIcon className="h-4 w-4 text-warning" />
                                </div>
                                <div className="flex-1">
                                    <p className="text-textPrimary text-sm">{reason}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* LLM Response */}
            {result.response && (
                <div className="bg-card rounded-xl p-6 border border-border">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-textPrimary">LLM Response</h3>
                        <div className="flex items-center space-x-2">
                            <EyeIcon className="h-4 w-4 text-textMuted" />
                            <span className="text-sm text-textMuted">Generated Content</span>
                        </div>
                    </div>
                    <div className="bg-background rounded-lg p-4 border border-border">
                        <div className="flex items-start space-x-3">
                            <DocumentIcon className="h-5 w-5 text-primary flex-shrink-0 mt-1" />
                            <p className="text-textPrimary whitespace-pre-wrap text-sm leading-relaxed">{result.response}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Status Alerts */}
            {result.decision === 'BLOCK' && (
                <div className="bg-danger/10 border border-danger/30 rounded-xl p-6">
                    <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-danger rounded-full flex items-center justify-center flex-shrink-0">
                            <XCircleIcon className="h-5 w-5 text-white" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold text-danger mb-2">Content Blocked</h3>
                            <p className="text-textPrimary mb-4">
                                This prompt has been blocked due to security policy violations and was not processed by the LLM.
                            </p>
                            {result.reasons && result.reasons.length > 0 && (
                                <div className="bg-background/50 rounded-lg p-3">
                                    <p className="text-textMuted text-sm font-medium mb-2">Violation Details:</p>
                                    <ul className="space-y-1">
                                        {result.reasons.map((reason, index) => (
                                            <li key={index} className="flex items-center space-x-2 text-sm text-textPrimary">
                                                <div className="w-1.5 h-1.5 bg-danger rounded-full"></div>
                                                <span>{reason}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {result.decision === 'SANITIZE' && (
                <div className="bg-warning/10 border border-warning/30 rounded-xl p-6">
                    <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-warning text-black rounded-full flex items-center justify-center flex-shrink-0">
                            <ExclamationTriangleIcon className="h-5 w-5" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold text-warning mb-2">Content Sanitized</h3>
                            <p className="text-textPrimary mb-4">
                                The prompt was automatically modified to remove potentially harmful content before processing.
                            </p>

                            {result.original_prompt && result.processed_prompt && (
                                <div className="space-y-3">
                                    <div className="bg-background/50 rounded-lg p-3">
                                        <p className="text-textMuted text-sm font-medium mb-2">Original Prompt:</p>
                                        <p className="text-textPrimary text-sm font-mono bg-background rounded p-2 border border-border">
                                            {result.original_prompt}
                                        </p>
                                    </div>

                                    <div className="bg-background/50 rounded-lg p-3">
                                        <p className="text-textMuted text-sm font-medium mb-2">Sanitized Prompt:</p>
                                        <p className="text-textPrimary text-sm font-mono bg-background rounded p-2 border border-border">
                                            {result.processed_prompt}
                                        </p>
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












// import React from 'react';
// import {
//     CheckCircleIcon,
//     ExclamationTriangleIcon,
//     XCircleIcon,
//     ClockIcon,
//     ShieldCheckIcon,
//     ChartBarIcon
// } from '@heroicons/react/24/outline';

// const ResultPanel = ({ result, isLoading }) => {
//     if (isLoading) {
//         return (
//             <div className="bg-card-bg rounded-xl p-6 border border-border-color">
//                 <div className="flex items-center justify-center h-64">
//                     <div className="text-center space-y-4">
//                         <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-accent mx-auto"></div>
//                         <div className="space-y-2">
//                             <p className="text-text-primary font-medium">Analyzing prompt safety...</p>
//                             <p className="text-text-muted text-sm">Running security filters and ML models</p>
//                         </div>
//                     </div>
//                 </div>
//             </div>
//         );
//     }

//     if (!result) {
//         return (
//             <div className="bg-card-bg rounded-xl p-6 border border-border-color border-dashed">
//                 <div className="text-center py-12">
//                     <ShieldCheckIcon className="h-16 w-16 text-text-muted mx-auto mb-4" />
//                     <p className="text-text-muted text-lg">Enter a prompt above to start safety analysis</p>
//                     <p className="text-text-muted text-sm mt-2">Our AI safety gateway will check for potential risks</p>
//                 </div>
//             </div>
//         );
//     }

//     const getDecisionBadge = (decision) => {
//         const badges = {
//             'ALLOW': {
//                 color: 'bg-secondary-accent text-white',
//                 icon: CheckCircleIcon,
//                 glow: 'shadow-glow-green'
//             },
//             'SANITIZE': {
//                 color: 'bg-warning-color text-white',
//                 icon: ExclamationTriangleIcon,
//                 glow: 'shadow-lg'
//             },
//             'BLOCK': {
//                 color: 'bg-danger-color text-white',
//                 icon: XCircleIcon,
//                 glow: 'shadow-glow-red'
//             }
//         };

//         const badge = badges[decision] || badges['BLOCK'];
//         const Icon = badge.icon;

//         return (
//             <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full ${badge.color} ${badge.glow}`}>
//                 <Icon className="h-5 w-5" />
//                 <span className="font-semibold">{decision}</span>
//             </div>
//         );
//     };

//     const getRiskScoreColor = (score) => {
//         if (score >= 0.7) return 'bg-danger-color';
//         if (score >= 0.4) return 'bg-warning-color';
//         return 'bg-secondary-accent';
//     };

//     const getRiskLevel = (score) => {
//         if (score >= 0.8) return 'CRITICAL';
//         if (score >= 0.6) return 'HIGH';
//         if (score >= 0.4) return 'MEDIUM';
//         if (score >= 0.2) return 'LOW';
//         return 'MINIMAL';
//     };

//     return (
//         <div className="space-y-6">
//             {/* Main Result Card */}
//             <div className="bg-card-bg rounded-xl p-6 border border-border-color">
//                 <div className="flex items-center justify-between mb-6">
//                     <h2 className="text-xl font-semibold text-text-primary">Analysis Result</h2>
//                     <div className="flex items-center space-x-4">
//                         {result.latency_ms && (
//                             <div className="flex items-center space-x-1 text-text-muted">
//                                 <ClockIcon className="h-4 w-4" />
//                                 <span className="text-sm">{result.latency_ms}ms</span>
//                             </div>
//                         )}
//                         {getDecisionBadge(result.decision)}
//                     </div>
//                 </div>

//                 {/* Risk Score Section */}
//                 <div className="space-y-4">
//                     <div className="flex items-center justify-between">
//                         <span className="text-text-primary font-medium">Risk Score</span>
//                         <div className="flex items-center space-x-2">
//                             <span className="text-2xl font-bold text-text-primary">
//                                 {(result.risk_score * 100).toFixed(1)}%
//                             </span>
//                             <span className={`px-2 py-1 rounded text-xs font-semibold ${result.risk_score >= 0.7 ? 'bg-danger-color text-white' :
//                                     result.risk_score >= 0.4 ? 'bg-warning-color text-white' :
//                                         'bg-secondary-accent text-white'
//                                 }`}>
//                                 {getRiskLevel(result.risk_score)}
//                             </span>
//                         </div>
//                     </div>

//                     {/* Progress Bar */}
//                     <div className="w-full bg-border-color rounded-full h-3">
//                         <div
//                             className={`h-3 rounded-full transition-all duration-500 ${getRiskScoreColor(result.risk_score)}`}
//                             style={{ width: `${Math.max(result.risk_score * 100, 2)}%` }}
//                         ></div>
//                     </div>

//                     {/* Risk Level Indicators */}
//                     <div className="flex justify-between text-xs text-text-muted">
//                         <span>Safe</span>
//                         <span>Low</span>
//                         <span>Medium</span>
//                         <span>High</span>
//                         <span>Critical</span>
//                     </div>
//                 </div>

//                 {/* Detection Reasons */}
//                 {result.reasons && result.reasons.length > 0 && (
//                     <div className="mt-6 pt-6 border-t border-border-color">
//                         <h3 className="text-lg font-medium text-text-primary mb-3">Detection Details</h3>
//                         <div className="space-y-2">
//                             {result.reasons.map((reason, index) => (
//                                 <div key={index} className="flex items-start space-x-2 p-3 bg-border-color bg-opacity-50 rounded-lg">
//                                     <ExclamationTriangleIcon className="h-5 w-5 text-warning-color mt-0.5 flex-shrink-0" />
//                                     <span className="text-text-primary">{reason}</span>
//                                 </div>
//                             ))}
//                         </div>
//                     </div>
//                 )}

//                 {/* Filter Results */}
//                 {result.filter_results && (
//                     <div className="mt-6 pt-6 border-t border-border-color">
//                         <h3 className="text-lg font-medium text-text-primary mb-3">Filter Analysis</h3>
//                         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
//                             {Object.entries(result.filter_results).map(([filterName, filterResult]) => (
//                                 <div key={filterName} className="bg-border-color bg-opacity-30 rounded-lg p-4">
//                                     <div className="flex items-center justify-between mb-2">
//                                         <span className="text-text-primary font-medium capitalize">
//                                             {filterName.replace('_', ' ')}
//                                         </span>
//                                         <ChartBarIcon className="h-4 w-4 text-primary-accent" />
//                                     </div>
//                                     <div className="space-y-1">
//                                         <div className="flex justify-between text-sm">
//                                             <span className="text-text-muted">Risk Score:</span>
//                                             <span className="text-text-primary font-medium">
//                                                 {(filterResult.risk_score * 100).toFixed(1)}%
//                                             </span>
//                                         </div>
//                                         {filterResult.reason && (
//                                             <p className="text-xs text-text-muted mt-1">{filterResult.reason}</p>
//                                         )}
//                                     </div>
//                                 </div>
//                             ))}
//                         </div>
//                     </div>
//                 )}
//             </div>

//             {/* Response Panel */}
//             {result.response && (
//                 <div className="bg-card-bg rounded-xl p-6 border border-border-color">
//                     <h3 className="text-lg font-semibold text-text-primary mb-4">LLM Response</h3>
//                     <div className="bg-dark-bg rounded-lg p-4 border border-border-color">
//                         <p className="text-text-primary whitespace-pre-wrap">{result.response}</p>
//                     </div>
//                 </div>
//             )}

//             {/* Blocked Content Warning */}
//             {result.decision === 'BLOCK' && (
//                 <div className="bg-danger-color bg-opacity-10 border border-danger-color border-opacity-30 rounded-xl p-6">
//                     <div className="flex items-start space-x-3">
//                         <XCircleIcon className="h-6 w-6 text-danger-color flex-shrink-0 mt-0.5" />
//                         <div>
//                             <h3 className="text-lg font-semibold text-danger-color mb-2">Content Blocked</h3>
//                             <p className="text-text-primary">
//                                 This prompt has been blocked due to security policy violations.
//                                 The request was not forwarded to the LLM for safety reasons.
//                             </p>
//                             {result.reasons && result.reasons.length > 0 && (
//                                 <div className="mt-3">
//                                     <p className="text-text-muted text-sm mb-2">Blocked for:</p>
//                                     <ul className="list-disc list-inside space-y-1">
//                                         {result.reasons.map((reason, index) => (
//                                             <li key={index} className="text-text-muted text-sm">{reason}</li>
//                                         ))}
//                                     </ul>
//                                 </div>
//                             )}
//                         </div>
//                     </div>
//                 </div>
//             )}

//             {/* Sanitization Notice */}
//             {result.decision === 'SANITIZE' && result.prompt_modified && (
//                 <div className="bg-warning-color bg-opacity-10 border border-warning-color border-opacity-30 rounded-xl p-6">
//                     <div className="flex items-start space-x-3">
//                         <ExclamationTriangleIcon className="h-6 w-6 text-warning-color flex-shrink-0 mt-0.5" />
//                         <div>
//                             <h3 className="text-lg font-semibold text-warning-color mb-2">Content Sanitized</h3>
//                             <p className="text-text-primary mb-3">
//                                 The prompt was modified to remove potentially harmful content before processing.
//                             </p>

//                             {result.original_prompt && result.processed_prompt && (
//                                 <div className="space-y-3">
//                                     <div>
//                                         <p className="text-text-muted text-sm mb-1">Original:</p>
//                                         <div className="bg-dark-bg rounded p-3 border border-border-color">
//                                             <p className="text-text-primary text-sm">{result.original_prompt}</p>
//                                         </div>
//                                     </div>

//                                     <div>
//                                         <p className="text-text-muted text-sm mb-1">Sanitized:</p>
//                                         <div className="bg-dark-bg rounded p-3 border border-border-color">
//                                             <p className="text-text-primary text-sm">{result.processed_prompt}</p>
//                                         </div>
//                                     </div>
//                                 </div>
//                             )}
//                         </div>
//                     </div>
//                 </div>
//             )}
//         </div>
//     );
// };

// export default ResultPanel;