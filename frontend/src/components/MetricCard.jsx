import React from 'react';

const MetricCard = ({ title, value, icon: Icon, trend, color = 'primary' }) => {
    const getColorClasses = () => {
        switch (color) {
            case 'success':
                return {
                    border: 'border-secondary border-opacity-30',
                    glow: 'shadow-glow-green',
                    icon: 'text-secondary',
                    value: 'text-secondary'
                };
            case 'warning':
                return {
                    border: 'border-warning border-opacity-30',
                    glow: 'shadow-glow-yellow',
                    icon: 'text-warning',
                    value: 'text-warning'
                };
            case 'danger':
                return {
                    border: 'border-danger border-opacity-30',
                    glow: 'shadow-glow-red',
                    icon: 'text-danger',
                    value: 'text-danger'
                };
            default:
                return {
                    border: 'border-primary border-opacity-30',
                    glow: 'shadow-glow',
                    icon: 'text-primary',
                    value: 'text-primary'
                };
        }
    };

    const colors = getColorClasses();

    return (
        <div className={`bg-card rounded-xl p-6 border ${colors.border} ${colors.glow} hover:scale-105 transition-all duration-300`}>
            <div className="flex items-center justify-between">
                <div className="flex-1">
                    <p className="text-textMuted text-sm font-medium uppercase tracking-wider mb-2">
                        {title}
                    </p>
                    <p className={`text-3xl font-bold ${colors.value} mb-1`}>
                        {value}
                    </p>
                    {trend && (
                        <div className="flex items-center space-x-1">
                            <span className={`text-sm ${trend.direction === 'up' ? 'text-secondary' :
                                    trend.direction === 'down' ? 'text-danger' : 'text-textMuted'
                                }`}>
                                {trend.direction === 'up' ? '↗' : trend.direction === 'down' ? '↘' : '→'} {trend.value}
                            </span>
                            <span className="text-xs text-textMuted">vs last week</span>
                        </div>
                    )}
                </div>

                {Icon && (
                    <div className={`p-3 rounded-full bg-opacity-20 ${colors.icon.replace('text-', 'bg-')}`}>
                        <Icon className={`h-8 w-8 ${colors.icon}`} />
                    </div>
                )}
            </div>
        </div>
    );
};

export default MetricCard;