import React from 'react';
import { CogIcon } from '@heroicons/react/24/outline';

const Settings = () => {
    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div>
                <h1 className="text-3xl font-bold text-text-primary">Settings</h1>
                <p className="text-text-muted mt-1">Configure your AI safety gateway</p>
            </div>

            {/* Coming Soon */}
            <div className="bg-card-bg rounded-xl p-12 border border-border-color border-dashed text-center">
                <CogIcon className="h-16 w-16 text-text-muted mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-text-primary mb-2">Settings Coming Soon</h3>
                <p className="text-text-muted">Configuration options will be available in the next update</p>
            </div>
        </div>
    );
};

export default Settings;