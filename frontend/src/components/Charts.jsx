import React from 'react';
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from 'recharts';

// Sample data - replace with real API data later
const safetyTrendData = [
    { name: 'Mon', score: 0.85, requests: 120 },
    { name: 'Tue', score: 0.78, requests: 145 },
    { name: 'Wed', score: 0.92, requests: 180 },
    { name: 'Thu', score: 0.75, requests: 165 },
    { name: 'Fri', score: 0.88, requests: 190 },
    { name: 'Sat', score: 0.95, requests: 210 },
    { name: 'Sun', score: 0.82, requests: 175 }
];

const violationData = [
    { category: 'Prompt Injection', count: 45, color: '#EF4444' },
    { category: 'Toxic Content', count: 32, color: '#F59E0B' },
    { category: 'Sensitive Data', count: 18, color: '#06B6D4' },
    { category: 'Jailbreak Attempts', count: 28, color: '#8B5CF6' },
    { category: 'Social Engineering', count: 15, color: '#10B981' }
];

const riskDistributionData = [
    { name: 'Low Risk', value: 65, color: '#22C55E' },
    { name: 'Medium Risk', value: 25, color: '#F59E0B' },
    { name: 'High Risk', value: 10, color: '#EF4444' }
];

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-card-bg border border-border-color rounded-lg p-3 shadow-lg">
                <p className="text-text-primary font-medium">{label}</p>
                {payload.map((entry, index) => (
                    <p key={index} className="text-primary-accent text-sm">
                        {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
                    </p>
                ))}
            </div>
        );
    }
    return null;
};

export const SafetyTrendChart = () => (
    <div className="bg-card-bg rounded-xl p-6 border border-border-color">
        <h3 className="text-lg font-semibold text-text-primary mb-4">Safety Score Trend</h3>
        <ResponsiveContainer width="100%" height={300}>
            <LineChart data={safetyTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" domain={[0, 1]} />
                <Tooltip content={<CustomTooltip />} />
                <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#06B6D4"
                    strokeWidth={3}
                    dot={{ fill: '#06B6D4', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, fill: '#06B6D4' }}
                />
            </LineChart>
        </ResponsiveContainer>
    </div>
);

export const ViolationsChart = () => (
    <div className="bg-card-bg rounded-xl p-6 border border-border-color">
        <h3 className="text-lg font-semibold text-text-primary mb-4">Top Violations by Category</h3>
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={violationData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis type="number" stroke="#9CA3AF" />
                <YAxis dataKey="category" type="category" stroke="#9CA3AF" width={120} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" fill="#06B6D4" radius={[0, 4, 4, 0]} />
            </BarChart>
        </ResponsiveContainer>
    </div>
);

export const RiskDistributionChart = () => (
    <div className="bg-card-bg rounded-xl p-6 border border-border-color">
        <h3 className="text-lg font-semibold text-text-primary mb-4">Risk Level Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
            <PieChart>
                <Pie
                    data={riskDistributionData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                    {riskDistributionData.map((entry) => (
                        <Cell key={`cell-${entry.name}`} fill={entry.color} />
                    ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
            </PieChart>
        </ResponsiveContainer>
    </div>
);