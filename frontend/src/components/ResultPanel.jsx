import React, { useState } from 'react';
import {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    XCircleIcon,
    ClockIcon,
    ShieldCheckIcon,
    ChartBarIcon,
    EyeIcon,
    DocumentIcon,
    ChevronDownIcon,
    ChevronRightIcon,
    InformationCircleIcon,
    ArrowTopRightOnSquareIcon
} from '@heroicons/react/24/outline';

const ResultPanel = ({ result, isLoading }) => {
    const [expandedFilters, setExpandedFilters] = useState({});
    const [showRawData, setShowRawData] = useState(false);

    const toggleFilterExpanded = (filterName) => {
        setExpandedFilters(prev => ({
            ...prev,
            [filterName]: !prev[filterName]
        }));
    };

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
                            <p className="text-textMuted text-sm">Running multi-layer security analysis</p>
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
                        Enter a prompt above to start comprehensive AI safety analysis
                    </p>
                    <div className="flex items-center justify-center space-x-6 text-sm text-textMuted">
                        <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-primary rounded-full"></div>
                            <span>Pattern Detection</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-secondary rounded-full"></div>
                            <span>ML Analysis</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-warning rounded-full"></div>
                            <span>Obfuscation Check</span>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    const getDecisionBadge = (decision) => {
        const badges = {
            'ALLOW': {
                color: 'bg-secondary text-background',
                textColor: 'text-secondary',
                bgLight: 'bg-secondary/10',
                icon: CheckCircleIcon,
                label: 'Safe',
                glow: 'shadow-glow-green'
            },
            'SANITIZE': {
                color: 'bg-warning text-background',
                textColor: 'text-warning',
                bgLight: 'bg-warning/10',
                icon: ExclamationTriangleIcon,
                label: 'Needs Sanitization',
                glow: 'shadow-glow-yellow'
            },
            'BLOCK': {
                color: 'bg-danger text-white',
                textColor: 'text-danger',
                bgLight: 'bg-danger/10',
                icon: XCircleIcon,
                label: 'Blocked',
                glow: 'shadow-glow-red'
            }
        };

        const badge = badges[decision] || badges['BLOCK'];
        const Icon = badge.icon;

        return (
            <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full text-sm font-medium ${badge.color} ${badge.glow}`}>
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

    const getFilterStatusBadge = (status) => {
        const statusConfig = {
            'SAFE': { color: 'bg-secondary/20 text-secondary border border-secondary/30', icon: CheckCircleIcon },
            'LOW': { color: 'bg-primary/20 text-primary border border-primary/30', icon: InformationCircleIcon },
            'MEDIUM': { color: 'bg-warning/20 text-warning border border-warning/30', icon: ExclamationTriangleIcon },
            'HIGH': { color: 'bg-danger/20 text-danger border border-danger/30', icon: ExclamationTriangleIcon },
            'CRITICAL': { color: 'bg-danger/30 text-danger border border-danger/50', icon: XCircleIcon }
        };

        const config = statusConfig[status] || statusConfig['SAFE'];
        const Icon = config.icon;

        return (
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${config.color}`}>
                <Icon className="w-3 h-3 mr-1" />
                {status}
            </span>
        );
    };

    const DetailedFilters = ({ detailedFilters }) => {
        if (!detailedFilters) {
            // Fallback to basic filter results
            const filterResults = result.filter_results || {};
            return (
                <div className="space-y-4">
                    {Object.entries(filterResults).map(([filterKey, filterData]) => (
                        <div key={filterKey} className="border border-border rounded-lg overflow-hidden bg-card">
                            <div className="px-4 py-3 bg-background/50 border-b border-border">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        <div>
                                            <h4 className="font-medium text-textPrimary capitalize">
                                                {filterKey.replace('_', ' ')}
                                            </h4>
                                            <p className="text-sm text-textMuted">
                                                {filterData.reason || 'Security filter analysis'}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-3">
                                        <span className={`text-lg font-bold ${getRiskScoreColor(filterData.risk_score || 0)}`}>
                                            {((filterData.risk_score || 0) * 100).toFixed(1)}%
                                        </span>
                                        {getFilterStatusBadge(filterData.risk_score >= 0.7 ? 'HIGH' : filterData.risk_score >= 0.4 ? 'MEDIUM' : 'SAFE')}
                                    </div>
                                </div>
                                {/* Progress Bar */}
                                <div className="mt-3">
                                    <div className="w-full bg-border rounded-full h-2">
                                        <div
                                            className={`h-2 rounded-full transition-all duration-500 ${getProgressBarColor(filterData.risk_score || 0)}`}
                                            style={{ width: `${(filterData.risk_score || 0) * 100}%` }}
                                        ></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            );
        }

        return (
            <div className="space-y-4">
                {Object.entries(detailedFilters).map(([filterKey, filterData]) => (
                    <div key={filterKey} className="border border-border rounded-lg overflow-hidden bg-card">
                        <div
                            className="px-4 py-3 bg-background/50 cursor-pointer hover:bg-background/70 transition-colors border-b border-border"
                            onClick={() => toggleFilterExpanded(filterKey)}
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    {expandedFilters[filterKey] ?
                                        <ChevronDownIcon className="h-4 w-4 text-textMuted" /> :
                                        <ChevronRightIcon className="h-4 w-4 text-textMuted" />
                                    }
                                    <div>
                                        <h4 className="font-medium text-textPrimary">{filterData.name}</h4>
                                        <p className="text-sm text-textMuted">{filterData.description}</p>
                                    </div>
                                </div>
                                <div className="flex items-center space-x-3">
                                    <span className={`text-lg font-bold ${getRiskScoreColor(filterData.risk_score)}`}>
                                        {(filterData.risk_score * 100).toFixed(1)}%
                                    </span>
                                    {getFilterStatusBadge(filterData.status)}
                                </div>
                            </div>
                            {/* Progress Bar */}
                            <div className="mt-3">
                                <div className="w-full bg-border rounded-full h-2">
                                    <div
                                        className={`h-2 rounded-full transition-all duration-500 ${getProgressBarColor(filterData.risk_score)}`}
                                        style={{ width: `${filterData.risk_score * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>

                        {expandedFilters[filterKey] && (
                            <div className="px-4 py-4 bg-card">
                                {/* Detailed Analysis */}
                                <div className="space-y-4">
                                    {/* Reason */}
                                    <div className="bg-background/30 rounded-lg p-3">
                                        <span className="text-sm font-medium text-textPrimary">Analysis Result:</span>
                                        <p className="text-sm text-textMuted mt-1">{filterData.reason}</p>
                                    </div>

                                    {/* Filter-specific details */}
                                    <FilterSpecificDetails
                                        type={filterKey}
                                        data={filterData}
                                    />

                                    {/* Technical Details */}
                                    {filterData.details && (
                                        <div className="bg-background/30 rounded-lg p-3">
                                            <h5 className="text-sm font-medium text-textPrimary mb-2">Technical Details</h5>
                                            <dl className="grid grid-cols-2 gap-2 text-xs">
                                                {Object.entries(filterData.details).map(([key, value]) => (
                                                    <div key={key}>
                                                        <dt className="text-textMuted capitalize">{key.replace('_', ' ')}:</dt>
                                                        <dd className="text-textPrimary font-medium">
                                                            {Array.isArray(value) ? value.join(', ') : String(value)}
                                                        </dd>
                                                    </div>
                                                ))}
                                            </dl>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        );
    };

    const FilterSpecificDetails = ({ type, data }) => {
        switch (type) {
            case 'regex_filter':
                return (
                    <div className="space-y-3">
                        {data.categories_detected?.length > 0 && (
                            <div className="bg-danger/10 rounded-lg p-3">
                                <span className="text-sm font-medium text-textPrimary">Threat Categories Detected:</span>
                                <div className="flex flex-wrap gap-1 mt-2">
                                    {data.categories_detected.map((category, idx) => (
                                        <span key={idx} className="px-2 py-1 bg-danger/20 text-danger text-xs rounded-full capitalize border border-danger/30">
                                            {category.replace('_', ' ')}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {data.matches?.length > 0 && (
                            <div className="bg-background/30 rounded-lg p-3">
                                <span className="text-sm font-medium text-textPrimary">Pattern Matches:</span>
                                <div className="mt-2 text-xs bg-background/50 p-2 rounded max-h-32 overflow-y-auto border border-border">
                                    {data.matches.map((match, idx) => (
                                        <div key={idx} className="mb-1 pb-1 border-b border-border/50 last:border-b-0">
                                            <span className="font-mono text-danger">"{match.match}"</span>
                                            <span className="text-textMuted ml-2">({match.category})</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                );

            case 'obfuscation_detector':
                return (
                    <div className="space-y-3">
                        {data.is_obfuscated && (
                            <div className="bg-warning/10 rounded-lg p-3">
                                <span className="text-sm font-medium text-textPrimary">Obfuscation Techniques:</span>
                                <div className="flex flex-wrap gap-1 mt-2">
                                    {data.techniques_found?.map((technique, idx) => (
                                        <span key={idx} className="px-2 py-1 bg-warning/20 text-warning text-xs rounded-full border border-warning/30">
                                            {technique.type?.replace('_', ' ')} ({technique.score?.toFixed(2)})
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {data.decoded_prompt && data.decoded_prompt.length > 0 && (
                            <div className="bg-background/30 rounded-lg p-3">
                                <span className="text-sm font-medium text-textPrimary">Decoded Content:</span>
                                <div className="mt-2 text-xs bg-background/50 p-2 rounded font-mono max-h-24 overflow-y-auto border border-border">
                                    {data.decoded_prompt}
                                </div>
                            </div>
                        )}
                    </div>
                );

            case 'ml_classifier':
                return (
                    <div className="space-y-3">
                        {data.ml_results?.length > 0 && (
                            <div className="bg-primary/10 rounded-lg p-3">
                                <span className="text-sm font-medium text-textPrimary">ML Model Results:</span>
                                <div className="mt-2 space-y-2">
                                    {data.ml_results.map((mlResult, idx) => (
                                        <div key={idx} className="flex justify-between items-center bg-background/30 p-2 rounded text-xs border border-border">
                                            <span className="font-medium capitalize text-textPrimary">
                                                {mlResult.method?.replace('_', ' ')}
                                            </span>
                                            <div className="flex items-center space-x-2">
                                                <span className={`font-bold ${getRiskScoreColor(mlResult.score || 0)}`}>
                                                    {((mlResult.score || 0) * 100).toFixed(1)}%
                                                </span>
                                                <span className="text-textMuted">{mlResult.reason}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                        {data.model_info && (
                            <div className="bg-background/30 rounded-lg p-3">
                                <span className="text-sm font-medium text-textPrimary">Model Information:</span>
                                <div className="mt-2 text-xs text-textMuted space-y-1">
                                    <div>Type: <span className="text-textPrimary">{data.model_info.model_type || 'Unknown'}</span></div>
                                    <div>Status: <span className={`font-medium ${data.model_info.initialized ? 'text-secondary' : 'text-warning'}`}>
                                        {data.model_info.initialized ? 'Loaded' : 'Fallback Mode'}
                                    </span></div>
                                </div>
                            </div>
                        )}
                    </div>
                );

            default:
                return null;
        }
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
            <div className="bg-card rounded-xl p-6 border border-border shadow-glow">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                            <ShieldCheckIcon className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold text-textPrimary">Security Analysis Complete</h2>
                            <p className="text-sm text-textMuted">Multi-layer threat detection results</p>
                        </div>
                    </div>
                    <div className="flex items-center space-x-4">
                        {result.processing_time_seconds && (
                            <div className="flex items-center space-x-1 text-textMuted text-sm">
                                <ClockIcon className="h-4 w-4" />
                                <span>{(result.processing_time_seconds * 1000).toFixed(0)}ms</span>
                            </div>
                        )}
                        {getDecisionBadge(result.decision)}
                    </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-4 gap-6 mb-6">
                    <div className="text-center bg-background/30 rounded-lg p-4">
                        <div className={`text-3xl font-bold ${getRiskScoreColor(result.risk_score)} mb-1`}>
                            {(result.risk_score * 100).toFixed(1)}%
                        </div>
                        <div className="text-sm text-textMuted">Risk Score</div>
                    </div>
                    <div className="text-center bg-background/30 rounded-lg p-4">
                        <div className="text-3xl font-bold text-primary mb-1">
                            {result.filter_summary?.filters_triggered || Object.keys(result.filter_results || {}).length}
                        </div>
                        <div className="text-sm text-textMuted">Filters Triggered</div>
                    </div>
                    <div className="text-center bg-background/30 rounded-lg p-4">
                        <div className="text-3xl font-bold text-textPrimary mb-1">
                            {result.processing_time_seconds ? (result.processing_time_seconds * 1000).toFixed(0) : '0'}<span className="text-lg text-textMuted">ms</span>
                        </div>
                        <div className="text-sm text-textMuted">Response Time</div>
                    </div>
                    <div className="text-center bg-background/30 rounded-lg p-4">
                        <div className="text-3xl font-bold text-secondary mb-1">
                            {(result.filter_summary?.overall_confidence || result.confidence || 'MEDIUM').toUpperCase()}
                        </div>
                        <div className="text-sm text-textMuted">Confidence</div>
                    </div>
                </div>

                {/* Overall Risk Progress Bar */}
                <div className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-textPrimary">Overall Risk Level</span>
                        <span className={`text-sm font-medium ${getRiskScoreColor(result.risk_score)}`}>
                            {result.risk_level || (result.risk_score >= 0.8 ? 'CRITICAL' :
                                result.risk_score >= 0.6 ? 'HIGH' :
                                    result.risk_score >= 0.4 ? 'MEDIUM' : 'LOW')}
                        </span>
                    </div>
                    <div className="w-full bg-border rounded-full h-3">
                        <div
                            className={`h-3 rounded-full transition-all duration-1000 ${getProgressBarColor(result.risk_score)}`}
                            style={{ width: `${Math.max(result.risk_score * 100, 2)}%` }}
                        ></div>
                    </div>
                </div>

                {/* Explanation */}
                <div className="bg-background/30 rounded-lg p-4 border border-border">
                    <div className="flex items-start space-x-3">
                        <InformationCircleIcon className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                        <div>
                            <p className="text-sm text-textPrimary font-medium">Analysis Summary</p>
                            <p className="text-sm text-textMuted mt-1">
                                {result.explanation || 'No explanation available'}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Data Table - Guardrail Style */}
            <div className="bg-card rounded-xl border border-border overflow-hidden">
                <div className="px-6 py-4 border-b border-border bg-background/30">
                    <h3 className="text-lg font-semibold text-textPrimary">Real-time LLM Input/Output Log</h3>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-background/50">
                            <tr>
                                <th className="text-left p-4 text-textMuted font-medium text-sm border-b border-border">Timestamp ↑</th>
                                <th className="text-left p-4 text-textMuted font-medium text-sm border-b border-border">Source Model</th>
                                <th className="text-left p-4 text-textMuted font-medium text-sm border-b border-border">Prompt (Truncated)</th>
                                <th className="text-left p-4 text-textMuted font-medium text-sm border-b border-border">Output (Truncated)</th>
                                <th className="text-left p-4 text-textMuted font-medium text-sm border-b border-border">Safety Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr className="border-b border-border hover:bg-background/30">
                                <td className="p-4 text-textPrimary text-sm font-mono">
                                    {formatTimestamp()}
                                </td>
                                <td className="p-4 text-textPrimary text-sm">
                                    SafeX Gateway
                                </td>
                                <td className="p-4 text-textPrimary text-sm max-w-xs">
                                    <div className="flex items-center space-x-2">
                                        <span className="text-primary">"</span>
                                        <span>{truncateText(result.original_prompt || "Test prompt", 40)}</span>
                                        <span className="text-primary">"</span>
                                    </div>
                                </td>
                                <td className="p-4 text-textPrimary text-sm max-w-xs">
                                    {result.processed_prompt !== result.original_prompt ? (
                                        <div className="flex items-center space-x-2">
                                            <span className="text-warning">"</span>
                                            <span>{truncateText(result.processed_prompt || "Sanitized", 40)}</span>
                                            <span className="text-warning">"</span>
                                        </div>
                                    ) : (
                                        <span className="text-textMuted italic">No modifications applied</span>
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

            {/* Detailed Filter Results */}
            <div className="bg-card rounded-xl p-6 border border-border">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-textPrimary">Filter Analysis Details</h3>
                    <button
                        onClick={() => setShowRawData(!showRawData)}
                        className="text-sm text-primary hover:text-primary/80 transition-colors flex items-center space-x-1"
                    >
                        <EyeIcon className="h-4 w-4" />
                        <span>{showRawData ? 'Hide' : 'Show'} Raw Data</span>
                    </button>
                </div>

                <DetailedFilters detailedFilters={result.detailed_filters} />

                {/* Raw Data Display */}
                {showRawData && (
                    <div className="mt-6 border-t border-border pt-6">
                        <h4 className="text-sm font-medium text-textPrimary mb-3">Raw Filter Data</h4>
                        <div className="bg-background text-secondary p-4 rounded-lg overflow-x-auto border border-border">
                            <pre className="text-xs font-mono">
                                {JSON.stringify(result.filter_results, null, 2)}
                            </pre>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResultPanel;