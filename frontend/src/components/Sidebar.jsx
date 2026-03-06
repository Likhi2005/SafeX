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
        <div className="fixed left-0 top-0 h-full w-64 bg-card-bg border-r border-border-color z-50">
            {/* Logo Section */}
            <div className="flex items-center justify-center h-16 border-b border-border-color">
                <div className="flex items-center space-x-2">
                    <ShieldCheckIcon className="h-8 w-8 text-primary-accent" />
                    <h1 className="text-xl font-bold text-text-primary">
                        Shield<span className="text-primary-accent">GPT</span>
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
                                        ? 'bg-primary-accent bg-opacity-20 text-primary-accent border border-primary-accent border-opacity-30'
                                        : 'text-text-muted hover:text-text-primary hover:bg-border-color'
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
                <div className="bg-border-color rounded-lg p-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-secondary-accent rounded-full animate-pulse"></div>
                            <span className="text-xs text-text-muted">System Active</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;



// import React from 'react';
// import { Link, useLocation } from 'react-router-dom';
// import { Shield, BarChart3, ShieldCheck, ScrollText, Settings } from 'lucide-react';

// const Sidebar = () => {
//     const location = useLocation();

//     const menuItems = [
//         {
//             name: 'Dashboard',
//             path: '/dashboard',
//             icon: BarChart3
//         },
//         {
//             name: 'Safety Check',
//             path: '/safety-check',
//             icon: ShieldCheck
//         },
//         {
//             name: 'Logs',
//             path: '/logs',
//             icon: ScrollText
//         },
//         {
//             name: 'Settings',
//             path: '/settings',
//             icon: Settings
//         }
//     ];

//     return (
//         <div className='w-64 bg-card border-r border-border h-screen sticky top-0'>
//             {/* Logo */}
//             <div className='p-6 border-b border-border'>
//                 <div className='flex items-center space-x-3'>
//                     <div className='p-2 bg-primary/20 rounded-lg'>
//                         <Shield className='h-6 w-6 text-primary' />
//                     </div>
//                     <div>
//                         <h1 className='text-xl font-bold text-textPrimary'>ShieldGPT</h1>
//                         <p className='text-sm text-textMuted'>LLM Safety Gateway</p>
//                     </div>
//                 </div>
//             </div>

//             {/* Navigation */}
//             <nav className='p-4 space-y-2'>
//                 {menuItems.map((item) => {
//                     const Icon = item.icon;
//                     const isActive = location.pathname === item.path;

//                     return (
//                         <Link
//                             key={item.name}
//                             to={item.path}
//                             className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${isActive
//                                     ? 'bg-primary/20 text-primary shadow-glow'
//                                     : 'text-textMuted hover:text-textPrimary hover:bg-border/50'
//                                 }`}
//                         >
//                             <Icon className='h-5 w-5' />
//                             <span className='font-medium'>{item.name}</span>
//                         </Link>
//                     );
//                 })}
//             </nav>
//         </div>
//     );
// };

// export default Sidebar;