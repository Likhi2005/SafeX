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
        const interval = setInterval(checkHealth, 30000);

        return () => clearInterval(interval);
    }, []);

    const getStatusColor = () => {
        switch (systemStatus) {
            case 'online': return 'text-secondary';
            case 'offline': return 'text-danger';
            default: return 'text-warning';
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
        <div className="fixed top-0 right-0 left-64 h-16 bg-card border-b border-border z-40">
            <div className="flex items-center justify-between h-full px-6">
                {/* Left side - Page context */}
                <div className="flex items-center space-x-4">
                    <h2 className="text-lg font-semibold text-textPrimary">
                        AI Safety Dashboard
                    </h2>
                </div>

                {/* Right side - Status and user */}
                <div className="flex items-center space-x-6">
                    {/* System Status */}
                    <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${systemStatus === 'online' ? 'bg-secondary animate-pulse' :
                                systemStatus === 'offline' ? 'bg-danger' : 'bg-warning animate-pulse'
                            }`}></div>
                        <span className={`text-sm font-medium ${getStatusColor()}`}>
                            {getStatusText()}
                        </span>
                        <span className="text-xs text-textMuted">
                            {lastUpdate.toLocaleTimeString()}
                        </span>
                    </div>

                    {/* Notifications */}
                    <button className="relative p-2 text-textMuted hover:text-textPrimary transition-colors">
                        <BellIcon className="h-5 w-5" />
                        <span className="absolute top-0 right-0 h-2 w-2 bg-danger rounded-full"></span>
                    </button>

                    {/* User Profile */}
                    <button className="flex items-center space-x-2 p-2 text-textMuted hover:text-textPrimary transition-colors">
                        <UserIcon className="h-5 w-5" />
                        <span className="text-sm font-medium">Admin</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Navbar;
