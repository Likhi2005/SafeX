import React from 'react';

const MetricCard = ({ title, value, icon: Icon, trend, color = 'primary' }) => {
    const getColorClasses = () => {
        switch (color) {
            case 'success':
                return {
                    border: 'border-secondary-accent border-opacity-30',
                    glow: 'shadow-glow-green',
                    icon: 'text-secondary-accent',
                    value: 'text-secondary-accent'
                };
            case 'warning':
                return {
                    border: 'border-warning-color border-opacity-30',
                    glow: 'shadow-lg',
                    icon: 'text-warning-color',
                    value: 'text-warning-color'
                };
            case 'danger':
                return {
                    border: 'border-danger-color border-opacity-30',
                    glow: 'shadow-glow-red',
                    icon: 'text-danger-color',
                    value: 'text-danger-color'
                };
            default:
                return {
                    border: 'border-primary-accent border-opacity-30',
                    glow: 'shadow-glow-cyan',
                    icon: 'text-primary-accent',
                    value: 'text-primary-accent'
                };
        }
    };

    const colors = getColorClasses();

    return (
        <div className={`bg-card-bg rounded-xl p-6 border ${colors.border} ${colors.glow} hover:scale-105 transition-all duration-300`}>
            <div className="flex items-center justify-between">
                <div className="flex-1">
                    <p className="text-text-muted text-sm font-medium uppercase tracking-wider mb-2">
                        {title}
                    </p>
                    <p className={`text-3xl font-bold ${colors.value} mb-1`}>
                        {value}
                    </p>
                    {trend && (
                        <div className="flex items-center space-x-1">
                            <span className={`text-sm ${trend.direction === 'up' ? 'text-secondary-accent' :
                                    trend.direction === 'down' ? 'text-danger-color' : 'text-text-muted'
                                }`}>
                                {trend.direction === 'up' ? '↗' : trend.direction === 'down' ? '↘' : '→'} {trend.value}
                            </span>
                            <span className="text-xs text-text-muted">vs last week</span>
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











// import React from 'react';

// const MetricCard = ( { title, value, icon: Icon, color = 'primary'}) => {
//     const colorClasses = {
//         primary: 'border-primary/30 shadow-glow',
//         secondary: 'border-secondary/30 shadow-glow-green',
//         warning: 'border-warning/30 shadow-glow-yellow',
//         danger: 'border-danger/30 shadow-glow-red'
//     };

//     const iconColorClasses = {
//         primary: 'text-primary bg-primary/20',
//         secondary: 'text-secondary bg-secondary/20',
//         warning: 'text-warning bg-warning/20',
//         danger: 'text-danger bg-danger/20'
//     };

//     return (
//         <div className={`bg-card rounded-xl border-2 p-6 ${colorClasses[color]}`}>
//             <div className='flex items-center justify-between'>
//                 <div>
//                     <p className='text-textMuted text-sm font-medium'>{title}</p>
//                     <p className='text-3xl font-bold text-textPrimary mt-2'>{value}</p>
//                 </div>
//                 <div className={`p-3 rounded-lg ${iconColorClasses[color]}`}>
//                     <Icon className='h-6 w-6'/>
//                 </div>
//             </div>
//         </div>
//     );
// };

// export default MetricCard;