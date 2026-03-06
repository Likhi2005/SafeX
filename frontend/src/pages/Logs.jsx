import React from 'react';
import LogsTable from '../components/LogsTable';
import MetricCard from '../components/MetricCard';
import {
    DocumentTextIcon,
    ClockIcon,
    ExclamationTriangleIcon,
    CheckCircleIcon
} from '@heroicons/react/24/outline';

const Logs = () => {
    // Mock statistics - replace with real API data
    const stats = {
        totalRequests: 1247,
        avgLatency: 42,
        blockedRequests: 138,
        allowedRequests: 1109
    };

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div>
                <h1 className="text-3xl font-bold text-text-primary">Request Logs</h1>
                <p className="text-text-muted mt-1">Monitor all safety check requests and their outcomes</p>
            </div>

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
                    value={stats.blockedRequests}
                    icon={ExclamationTriangleIcon}
                    color="danger"
                />

                <MetricCard
                    title="Allowed"
                    value={stats.allowedRequests}
                    icon={CheckCircleIcon}
                    color="success"
                />
            </div>

            {/* Logs Table */}
            <LogsTable />
        </div>
    );
};

export default Logs;