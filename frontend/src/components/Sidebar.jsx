import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
    ChartBarIcon,
    ShieldCheckIcon,
    DocumentTextIcon,
    CogIcon,
    HomeIcon
} from '@heroicons/react/24/outline';

const Sidebar = () => {
    const location = useLocation();

    const menuItems = [
        { name: 'Dashboard', path: '/', icon: HomeIcon },
        { name: 'Safety Check', path: '/safety-check', icon: ShieldCheckIcon },
        { name: 'Logs', path: '/logs', icon: DocumentTextIcon },
        { name: 'Settings', path: '/settings', icon: CogIcon },
    ];

    return (
        <div className="fixed left-0 top-0 h-full w-64 bg-card border-r border-border z-50">
            {/* Logo Section */}
            <div className="flex items-center justify-center h-16 border-b border-border">
                <div className="flex items-center space-x-2">
                    <ShieldCheckIcon className="h-8 w-8 text-primary" />
                    <h1 className="text-xl font-bold text-textPrimary">
                        Shield<span className="text-primary">GPT</span>
                    </h1>
                </div>
            </div>

            {/* Navigation Menu */}
            <nav className="mt-8">
                <div className="px-4 space-y-2">
                    {menuItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;

                        return (
                            <Link
                                key={item.name}
                                to={item.path}
                                className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200 ${isActive
                                        ? 'bg-primary bg-opacity-20 text-primary border border-primary border-opacity-30'
                                        : 'text-textMuted hover:text-textPrimary hover:bg-border'
                                    }`}
                            >
                                <Icon className="mr-3 h-5 w-5" />
                                {item.name}
                            </Link>
                        );
                    })}
                </div>
            </nav>

            {/* Status Indicator */}
            <div className="absolute bottom-4 left-4 right-4">
                <div className="bg-border rounded-lg p-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-secondary rounded-full animate-pulse"></div>
                            <span className="text-xs text-textMuted">System Active</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;

