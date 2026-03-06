import React, { useState } from 'react';
import PromptInput from '../components/PromptInput';
import ResultPanel from '../components/ResultPanel';
import { analyzePrompt } from '../services/api';

const SafetyCheck = () => {
    const [result, setResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleAnalyze = async (prompt) => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await analyzePrompt(prompt);

            if (response.success) {
                setResult(response.data);
            } else {
                setError(response.error);
                setResult(null);
            }
        } catch (err) {
            setError('Failed to analyze prompt. Please try again.');
            setResult(null);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div>
                <h1 className="text-3xl font-bold text-text-primary">Safety Check</h1>
                <p className="text-text-muted mt-1">Test prompt safety with real-time AI analysis</p>
            </div>

            {/* Error Banner */}
            {error && (
                <div className="bg-danger-color bg-opacity-10 border border-danger-color border-opacity-30 rounded-xl p-4">
                    <div className="flex items-center space-x-2">
                        <span className="text-danger-color font-medium">Error:</span>
                        <span className="text-text-primary">{error}</span>
                    </div>
                </div>
            )}

            {/* Input Section */}
            <PromptInput onAnalyze={handleAnalyze} isLoading={isLoading} />

            {/* Results Section */}
            <ResultPanel result={result} isLoading={isLoading} />
        </div>
    );
};

export default SafetyCheck;