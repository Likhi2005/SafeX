import React, { useState, useEffect } from 'react';
import { BellIcon, UserIcon } from '@heroicons/react/24/outline';
import { getHealthCheck } from '../services/api';

const Navbar = () => {
    const [systemStatus, setSystemStatus] = useState('checking');
    const [lastUpdate, setLastUpdate] = useState(new Date());

    useEffect(() => {
        const checkHealth = async () => {
            const result = await getHealthCheck();
            setSystemStatus(result.success ? 'online' : 'offline');
            setLastUpdate(new Date());
        };

        checkHealth();
        const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

        return () => clearInterval(interval);
    }, []);

    const getStatusColor = () => {
        switch (systemStatus) {
            case 'online': return 'text-secondary-accent';
            case 'offline': return 'text-danger-color';
            default: return 'text-warning-color';
        }
    };

    const getStatusText = () => {
        switch (systemStatus) {
            case 'online': return 'Backend Online';
            case 'offline': return 'Backend Offline';
            default: return 'Checking...';
        }
    };

    return (
        <div className="fixed top-0 right-0 left-64 h-16 bg-card-bg border-b border-border-color z-40">
            <div className="flex items-center justify-between h-full px-6">
                {/* Left side - Page context */}
                <div className="flex items-center space-x-4">
                    <h2 className="text-lg font-semibold text-text-primary">
                        AI Safety Dashboard
                    </h2>
                </div>

                {/* Right side - Status and user */}
                <div className="flex items-center space-x-6">
                    {/* System Status */}
                    <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${systemStatus === 'online' ? 'bg-secondary-accent animate-pulse' :
                                systemStatus === 'offline' ? 'bg-danger-color' : 'bg-warning-color animate-pulse'
                            }`}></div>
                        <span className={`text-sm font-medium ${getStatusColor()}`}>
                            {getStatusText()}
                        </span>
                        <span className="text-xs text-text-muted">
                            {lastUpdate.toLocaleTimeString()}
                        </span>
                    </div>

                    {/* Notifications */}
                    <button className="relative p-2 text-text-muted hover:text-text-primary transition-colors">
                        <BellIcon className="h-5 w-5" />
                        <span className="absolute top-0 right-0 h-2 w-2 bg-danger-color rounded-full"></span>
                    </button>

                    {/* User Profile */}
                    <button className="flex items-center space-x-2 p-2 text-text-muted hover:text-text-primary transition-colors">
                        <UserIcon className="h-5 w-5" />
                        <span className="text-sm font-medium">Admin</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Navbar;















// import React from 'react';
// import { Bell, User, Activity } from 'lucide-react';

// const Navbar = () => {
//     return (
//         <header className='bg-card border-b border-border px-6 py-4'>
//             <div className='flex items-center justify-between'>
//                 {/* Page Title */}
//                 <div className='flex items-center space-x-4'>
//                     <h2 className='text-2xl font-semibold text-textPrimary'>
//                         Security Dashboard
//                     </h2>
//                     <div className='flex items-center space-x-2 px-3 py-1 bg-secondary/20 rounded-full'>
//                         <div className='w-2 h-2 bg-secondary rounded-full animate-pulse'></div>
//                         <span className='text-sm text-secondary font-medium'>System Active</span>
//                     </div>
//                 </div>

//                 {/* Right Side */}
//                 <div className='flex items-center space-x-4'>
//                     {/* Status Indicator */}
//                     <div className='flex items-center space-x-2 text-textMuted'>
//                         <Activity className='h-4 w-4'/>
//                         <span className='text-sm'>API: Online</span>
//                     </div>

//                     {/* Notifications */}
//                     <button className='p-2 text-textMuted hover:text-textPrimary transition-colors rounded-lg hover:bg-border/50'>
//                         <Bell className='h-5 w-5'/>
//                     </button>

//                     {/* User Profile */}
//                     <button className='p-2 text-textMuted hover:text-textPrimary transition-colors rounded-lg hover:bg-border/50'>
//                         <User className='h-5 w-5'/>
//                     </button>
//                 </div>
//             </div>
//         </header>
//     );
// };

// export default Navbar;