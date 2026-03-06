import React, { useState, useEffect } from 'react';
import LogsTable from '../components/LogsTable';
import MetricCard from '../components/MetricCard';
import { getThreatStats, getThreatLogs } from '../services/api';
import {
    DocumentTextIcon,
    ClockIcon,
    ExclamationTriangleIcon,
    CheckCircleIcon
} from '@heroicons/react/24/outline';

const Logs = () => {
    const [stats, setStats] = useState({
        totalRequests: 0,
        avgLatency: 0,
        blockedRequests: 0,
        allowedRequests: 0
    });

    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchLogsData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch both stats and logs
            const [statsResponse, logsResponse] = await Promise.all([
                getThreatStats(),
                getThreatLogs(1000) // Get more logs for the table
            ]);

            if (statsResponse.success && statsResponse.data.statistics) {
                const statistics = statsResponse.data.statistics;
                setStats({
                    totalRequests: statistics.total_threats || 0,
                    avgLatency: 45, // This would come from performance metrics
                    blockedRequests: statistics.blocked_threats || 0,
                    allowedRequests: statistics.allowed_threats || 0
                });
            }

            if (logsResponse.success && logsResponse.data.threats) {
                setLogs(logsResponse.data.threats);
            }

        } catch (err) {
            console.error('Failed to fetch logs data:', err);
            setError('Failed to load logs data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogsData();
    }, []);

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-text-primary">Threat Logs</h1>
                    <p className="text-text-muted mt-1">Monitor all security analysis requests and their outcomes</p>
                </div>
                <button
                    onClick={fetchLogsData}
                    disabled={loading}
                    className="px-4 py-2 bg-primary-accent text-white rounded-lg hover:bg-primary-accent/80 disabled:opacity-50"
                >
                    {loading ? 'Refreshing...' : 'Refresh'}
                </button>
            </div>

            {/* Error Banner */}
            {error && (
                <div className="bg-danger-color bg-opacity-10 border border-danger-color rounded-lg p-4">
                    <p className="text-danger-color">{error}</p>
                </div>
            )}

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <MetricCard
                    title="Total Requests"
                    value={stats.totalRequests.toLocaleString()}
                    icon={DocumentTextIcon}
                    color="primary"
                />

                <MetricCard
                    title="Avg Latency"
                    value={`${stats.avgLatency}ms`}
                    icon={ClockIcon}
                    color="success"
                />

                <MetricCard
                    title="Blocked"
                    value={stats.blockedRequests.toLocaleString()}
                    icon={ExclamationTriangleIcon}
                    color="danger"
                />

                <MetricCard
                    title="Allowed"
                    value={stats.allowedRequests.toLocaleString()}
                    icon={CheckCircleIcon}
                    color="success"
                />
            </div>

            {/* Logs Table */}
            <LogsTable
                logs={logs}
                loading={loading}
                onRefresh={fetchLogsData}
            />
        </div>
    );
};

export default Logs;





// import React from 'react';
// import LogsTable from '../components/LogsTable';
// import MetricCard from '../components/MetricCard';
// import {
//     DocumentTextIcon,
//     ClockIcon,
//     ExclamationTriangleIcon,
//     CheckCircleIcon
// } from '@heroicons/react/24/outline';

// const Logs = () => {
//     // Mock statistics - replace with real API data
//     const stats = {
//         totalRequests: 1247,
//         avgLatency: 42,
//         blockedRequests: 138,
//         allowedRequests: 1109
//     };

//     return (
//         <div className="space-y-6">
//             {/* Page Header */}
//             <div>
//                 <h1 className="text-3xl font-bold text-text-primary">Request Logs</h1>
//                 <p className="text-text-muted mt-1">Monitor all safety check requests and their outcomes</p>
//             </div>

//             {/* Quick Stats */}
//             <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
//                 <MetricCard
//                     title="Total Requests"
//                     value={stats.totalRequests.toLocaleString()}
//                     icon={DocumentTextIcon}
//                     color="primary"
//                 />

//                 <MetricCard
//                     title="Avg Latency"
//                     value={`${stats.avgLatency}ms`}
//                     icon={ClockIcon}
//                     color="success"
//                 />

//                 <MetricCard
//                     title="Blocked"
//                     value={stats.blockedRequests}
//                     icon={ExclamationTriangleIcon}
//                     color="danger"
//                 />

//                 <MetricCard
//                     title="Allowed"
//                     value={stats.allowedRequests}
//                     icon={CheckCircleIcon}
//                     color="success"
//                 />
//             </div>

//             {/* Logs Table */}
//             <LogsTable />
//         </div>
//     );
// };

// export default Logs;