import React, { useState } from 'react';
import PromptInput from '../components/PromptInput';
import ResultPanel from '../components/ResultPanel';
import { analyzePromptEnhanced, analyzePrompt, checkEnhancedFeaturesAvailable } from '../services/api';

const SafetyCheck = () => {
    const [result, setResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [analysisHistory, setAnalysisHistory] = useState([]);
    const [useEnhanced, setUseEnhanced] = useState(true);

    const handleAnalyze = async (prompt) => {
        setIsLoading(true);
        setError(null);

        try {
            console.log('Starting analysis for prompt:', prompt.substring(0, 50) + '...');

            // Try enhanced API first, fallback to legacy
            let response;

            if (useEnhanced) {
                response = await analyzePromptEnhanced(prompt);

                // If enhanced fails, fallback to legacy
                if (!response.success) {
                    console.warn('Enhanced API failed, trying legacy:', response.error);
                    response = await analyzePrompt(prompt);
                    setUseEnhanced(false); // Disable enhanced for future calls
                }
            } else {
                response = await analyzePrompt(prompt);
            }

            console.log('API Response:', response);

            if (response.success && response.data) {
                const data = response.data;

                // Transform the response to ensure compatibility
                const transformedResult = {
                    status: data.status || 'success',
                    decision: data.decision,
                    risk_score: data.risk_score || 0,
                    risk_level: data.risk_level || 'LOW',
                    explanation: data.explanation || 'No explanation available',
                    confidence: data.confidence || 'medium',
                    threat_detected: data.threat_detected || data.risk_score > 0.3,

                    // Prompt information
                    original_prompt: data.original_prompt || prompt,
                    processed_prompt: data.processed_prompt || prompt,
                    prompt_modified: data.prompt_modified || false,

                    // Filter results with proper validation
                    filter_results: data.filter_results || {},
                    detailed_filters: data.detailed_filters || null,
                    filter_summary: data.filter_summary || null,

                    // Performance metrics
                    processing_time_seconds: data.processing_time_seconds || 0,
                    timestamp: data.timestamp || new Date().toISOString(),

                    // Additional metadata
                    pipeline_version: data.pipeline_version || '2.0.0',
                    request_id: data.request_id || `req_${Date.now()}`,

                    // Sanitization info (if available)
                    sanitization_result: data.sanitization_result || null
                };

                setResult(transformedResult);

                // Add to history
                setAnalysisHistory(prev => [{
                    id: Date.now(),
                    prompt: prompt.substring(0, 100) + (prompt.length > 100 ? '...' : ''),
                    decision: transformedResult.decision,
                    risk_score: transformedResult.risk_score,
                    timestamp: transformedResult.timestamp,
                    method: useEnhanced ? 'enhanced' : 'legacy'
                }, ...prev.slice(0, 9)]); // Keep last 10 analyses

                setError(null);

            } else {
                // Handle API error responses
                setError(`Analysis failed: ${response.error || 'Unknown error'}`);
                setResult(null);
            }

        } catch (err) {
            console.error('Analysis error:', err);

            // Provide more specific error messages
            if (err.message?.includes('timeout')) {
                setError('Analysis request timed out. Please try again.');
            } else if (err.message?.includes('Network error')) {
                setError('Cannot connect to SafeX server. Please check if the backend is running.');
            } else {
                setError(`Failed to analyze prompt: ${err.message || 'Unknown error'}`);
            }

            setResult(null);
        } finally {
            setIsLoading(false);
        }
    };

    const clearHistory = () => {
        setAnalysisHistory([]);
    };

    const clearAll = () => {
        setResult(null);
        setError(null);
        setAnalysisHistory([]);
    };

    // Check enhanced features on component mount
    React.useEffect(() => {
        const checkFeatures = async () => {
            try {
                const featuresCheck = await checkEnhancedFeaturesAvailable();
                setUseEnhanced(featuresCheck.available);
                console.log('Enhanced features:', featuresCheck.available ? 'Available' : 'Not available');
            } catch (err) {
                console.warn('Could not check enhanced features:', err);
                setUseEnhanced(false);
            }
        };

        checkFeatures();
    }, []);

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                        <span className="text-blue-500 text-xl">🛡️</span>
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Safety Check</h1>
                        <p className="text-gray-600 mt-1">
                            Test prompt safety with real-time AI analysis
                            {useEnhanced && <span className="text-green-600 text-sm ml-2">(Enhanced Mode)</span>}
                        </p>
                    </div>
                </div>

                {/* Action Buttons */}
                {(result || analysisHistory.length > 0) && (
                    <div className="flex space-x-2">
                        {analysisHistory.length > 0 && (
                            <button
                                onClick={clearHistory}
                                className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
                            >
                                Clear History
                            </button>
                        )}
                        <button
                            onClick={clearAll}
                            className="px-4 py-2 text-sm bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors"
                        >
                            Clear All
                        </button>
                    </div>
                )}
            </div>

            {/* System Status */}
            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-green-800 font-medium">SafeX Security System</span>
                    <span className="text-green-600">Online & Ready</span>
                    {useEnhanced && <span className="text-green-600 text-sm">(Enhanced Analysis Available)</span>}
                </div>
            </div>

            {/* Error Banner */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 animate-in slide-in-from-top-2 duration-300">
                    <div className="flex items-center space-x-3">
                        <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center flex-shrink-0">
                            <span className="text-white text-xs font-bold">!</span>
                        </div>
                        <div className="flex-1">
                            <span className="text-red-700 font-medium">Error:</span>
                            <span className="text-red-600 ml-2">{error}</span>
                        </div>
                        <button
                            onClick={() => setError(null)}
                            className="text-red-500 hover:text-red-700 transition-colors"
                        >
                            ×
                        </button>
                    </div>
                </div>
            )}

            {/* Input Section */}
            <PromptInput onAnalyze={handleAnalyze} isLoading={isLoading} />

            {/* Results Section */}
            <ResultPanel result={result} isLoading={isLoading} />

            {/* Analysis History */}
            {analysisHistory.length > 0 && (
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Analyses</h3>
                    <div className="space-y-3">
                        {analysisHistory.map((analysis) => (
                            <div
                                key={analysis.id}
                                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                            >
                                <div className="flex-1">
                                    <p className="text-sm text-gray-700 font-mono">
                                        {analysis.prompt}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">
                                        {new Date(analysis.timestamp).toLocaleString()}
                                        <span className="ml-2 text-blue-600">({analysis.method})</span>
                                    </p>
                                </div>
                                <div className="flex items-center space-x-3">
                                    <span className={`px-2 py-1 text-xs font-medium rounded ${analysis.decision === 'ALLOW'
                                            ? 'bg-green-100 text-green-700'
                                            : analysis.decision === 'SANITIZE'
                                                ? 'bg-yellow-100 text-yellow-700'
                                                : 'bg-red-100 text-red-700'
                                        }`}>
                                        {analysis.decision}
                                    </span>
                                    <span className="text-sm text-gray-600 font-mono">
                                        {(analysis.risk_score * 100).toFixed(1)}%
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default SafetyCheck;














// import React, { useState } from 'react';
// import PromptInput from '../components/PromptInput';
// import ResultPanel from '../components/ResultPanel';
// import { analyzePrompt } from '../services/api';

// const SafetyCheck = () => {
//     const [result, setResult] = useState(null);
//     const [isLoading, setIsLoading] = useState(false);
//     const [error, setError] = useState(null);
//     const [analysisHistory, setAnalysisHistory] = useState([]);

//     const handleAnalyze = async (prompt) => {
//         setIsLoading(true);
//         setError(null);

//         try {
//             console.log('Starting analysis for prompt:', prompt.substring(0, 50) + '...');

//             // Call the API
//             const response = await analyzePrompt(prompt);
//             console.log('API Response:', response);

//             // Handle the response based on the new backend structure
//             if (response.status === 'success' || response.decision) {
//                 // Transform the response to match expected format
//                 const transformedResult = {
//                     status: response.status || 'success',
//                     decision: response.decision,
//                     risk_score: response.risk_score || 0,
//                     risk_level: response.risk_level || 'LOW',
//                     explanation: response.explanation || 'No explanation available',
//                     confidence: response.confidence || 'medium',
//                     threat_detected: response.threat_detected || response.risk_score > 0.3,

//                     // Prompt information
//                     original_prompt: response.original_prompt || prompt,
//                     processed_prompt: response.processed_prompt || prompt,
//                     prompt_modified: response.prompt_modified || false,

//                     // Filter results with proper validation
//                     filter_results: response.filter_results || {},

//                     // Performance metrics
//                     processing_time_seconds: response.processing_time_seconds || 0,
//                     timestamp: response.timestamp || new Date().toISOString(),

//                     // Additional metadata
//                     pipeline_version: response.pipeline_version || '2.0.0',
//                     request_id: response.request_id || `req_${Date.now()}`,

//                     // Sanitization info (if available)
//                     sanitization_result: response.sanitization_result || null
//                 };

//                 setResult(transformedResult);

//                 // Add to history
//                 setAnalysisHistory(prev => [{
//                     id: Date.now(),
//                     prompt: prompt.substring(0, 100) + (prompt.length > 100 ? '...' : ''),
//                     decision: transformedResult.decision,
//                     risk_score: transformedResult.risk_score,
//                     timestamp: transformedResult.timestamp
//                 }, ...prev.slice(0, 9)]); // Keep last 10 analyses

//                 setError(null);

//             } else if (response.status === 'error') {
//                 // Handle error responses from backend
//                 setError(`Analysis failed: ${response.error || 'Unknown error'}`);
//                 setResult(null);
//             } else {
//                 // Handle unexpected response format
//                 console.warn('Unexpected response format:', response);
//                 setError('Received unexpected response format from server');
//                 setResult(null);
//             }

//         } catch (err) {
//             console.error('Analysis error:', err);

//             // Provide more specific error messages
//             if (err.code === 'NETWORK_ERROR') {
//                 setError('Cannot connect to SafeX server. Please check if the backend is running.');
//             } else if (err.code === 'TIMEOUT') {
//                 setError('Analysis request timed out. Please try again.');
//             } else if (err.response?.status === 400) {
//                 setError(`Invalid request: ${err.response.data?.error || 'Bad request'}`);
//             } else if (err.response?.status === 503) {
//                 setError('SafeX service is temporarily unavailable. Please try again later.');
//             } else {
//                 setError(`Failed to analyze prompt: ${err.message || 'Unknown error'}`);
//             }

//             setResult(null);
//         } finally {
//             setIsLoading(false);
//         }
//     };

//     const clearHistory = () => {
//         setAnalysisHistory([]);
//     };

//     const clearAll = () => {
//         setResult(null);
//         setError(null);
//         setAnalysisHistory([]);
//     };

//     return (
//         <div className="space-y-6">
//             {/* Page Header */}
//             <div className="flex items-center justify-between">
//                 <div className="flex items-center space-x-3">
//                     <div className="w-10 h-10 bg-primary/20 rounded-lg flex items-center justify-center">
//                         <span className="text-primary text-xl">🛡️</span>
//                     </div>
//                     <div>
//                         <h1 className="text-3xl font-bold text-textPrimary">Safety Check</h1>
//                         <p className="text-textMuted mt-1">Test prompt safety with real-time AI analysis</p>
//                     </div>
//                 </div>

//                 {/* Action Buttons */}
//                 {(result || analysisHistory.length > 0) && (
//                     <div className="flex space-x-2">
//                         {analysisHistory.length > 0 && (
//                             <button
//                                 onClick={clearHistory}
//                                 className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
//                             >
//                                 Clear History
//                             </button>
//                         )}
//                         <button
//                             onClick={clearAll}
//                             className="px-4 py-2 text-sm bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors"
//                         >
//                             Clear All
//                         </button>
//                     </div>
//                 )}
//             </div>

//             {/* System Status */}
//             <div className="bg-green-50 border border-green-200 rounded-xl p-4">
//                 <div className="flex items-center space-x-3">
//                     <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
//                     <span className="text-green-800 font-medium">SafeX Security System</span>
//                     <span className="text-green-600">Online & Ready</span>
//                 </div>
//             </div>

//             {/* Error Banner */}
//             {error && (
//                 <div className="bg-red-50 border border-red-200 rounded-xl p-4 animate-in slide-in-from-top-2 duration-300">
//                     <div className="flex items-center space-x-3">
//                         <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center flex-shrink-0">
//                             <span className="text-white text-xs font-bold">!</span>
//                         </div>
//                         <div className="flex-1">
//                             <span className="text-red-700 font-medium">Error:</span>
//                             <span className="text-red-600 ml-2">{error}</span>
//                         </div>
//                         <button
//                             onClick={() => setError(null)}
//                             className="text-red-500 hover:text-red-700 transition-colors"
//                         >
//                             ×
//                         </button>
//                     </div>
//                 </div>
//             )}

//             {/* Input Section */}
//             <PromptInput onAnalyze={handleAnalyze} isLoading={isLoading} />

//             {/* Results Section */}
//             <ResultPanel result={result} isLoading={isLoading} />

//             {/* Analysis History */}
//             {analysisHistory.length > 0 && (
//                 <div className="bg-white rounded-xl border border-borderPrimary p-6">
//                     <h3 className="text-lg font-semibold text-textPrimary mb-4">Recent Analyses</h3>
//                     <div className="space-y-3">
//                         {analysisHistory.map((analysis) => (
//                             <div
//                                 key={analysis.id}
//                                 className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
//                             >
//                                 <div className="flex-1">
//                                     <p className="text-sm text-gray-700 font-mono">
//                                         {analysis.prompt}
//                                     </p>
//                                     <p className="text-xs text-gray-500 mt-1">
//                                         {new Date(analysis.timestamp).toLocaleString()}
//                                     </p>
//                                 </div>
//                                 <div className="flex items-center space-x-3">
//                                     <span className={`px-2 py-1 text-xs font-medium rounded ${analysis.decision === 'ALLOW'
//                                             ? 'bg-green-100 text-green-700'
//                                             : analysis.decision === 'SANITIZE'
//                                                 ? 'bg-yellow-100 text-yellow-700'
//                                                 : 'bg-red-100 text-red-700'
//                                         }`}>
//                                         {analysis.decision}
//                                     </span>
//                                     <span className="text-sm text-gray-600 font-mono">
//                                         {(analysis.risk_score * 100).toFixed(1)}%
//                                     </span>
//                                 </div>
//                             </div>
//                         ))}
//                     </div>
//                 </div>
//             )}
//         </div>
//     );
// };

// export default SafetyCheck;




// // import React, { useState } from 'react';
// // import PromptInput from '../components/PromptInput';
// // import ResultPanel from '../components/ResultPanel';
// // import { analyzePrompt } from '../services/api';

// // const SafetyCheck = () => {
// //     const [result, setResult] = useState(null);
// //     const [isLoading, setIsLoading] = useState(false);
// //     const [error, setError] = useState(null);

// //     const handleAnalyze = async (prompt) => {
// //         setIsLoading(true);
// //         setError(null);

// //         try {
// //             const response = await analyzePrompt(prompt);

// //             if (response.success) {
// //                 setResult(response.data);
// //             } else {
// //                 setError(response.error);
// //                 setResult(null);
// //             }
// //         } catch (err) {
// //             setError('Failed to analyze prompt. Please try again.');
// //             setResult(null);
// //         } finally {
// //             setIsLoading(false);
// //         }
// //     };

// //     return (
// //         <div className="space-y-6">
// //             {/* Page Header */}
// //             <div className="flex items-center space-x-3">
// //                 <div className="w-10 h-10 bg-primary/20 rounded-lg flex items-center justify-center">
// //                     <span className="text-primary text-xl">🛡️</span>
// //                 </div>
// //                 <div>
// //                     <h1 className="text-3xl font-bold text-textPrimary">Safety Check</h1>
// //                     <p className="text-textMuted mt-1">Test prompt safety with real-time AI analysis</p>
// //                 </div>
// //             </div>

// //             {/* Error Banner */}
// //             {error && (
// //                 <div className="bg-danger/10 border border-danger/30 rounded-xl p-4 animate-in slide-in-from-top-2 duration-300">
// //                     <div className="flex items-center space-x-3">
// //                         <div className="w-5 h-5 bg-danger rounded-full flex items-center justify-center">
// //                             <span className="text-white text-xs font-bold">!</span>
// //                         </div>
// //                         <div>
// //                             <span className="text-danger font-medium">Error:</span>
// //                             <span className="text-textPrimary ml-2">{error}</span>
// //                         </div>
// //                     </div>
// //                 </div>
// //             )}

// //             {/* Input Section */}
// //             <PromptInput onAnalyze={handleAnalyze} isLoading={isLoading} />

// //             {/* Results Section */}
// //             <ResultPanel result={result} isLoading={isLoading} />
// //         </div>
// //     );
// // };

// // export default SafetyCheck;












// // import React, { useState } from 'react';
// // import PromptInput from '../components/PromptInput';
// // import ResultPanel from '../components/ResultPanel';
// // import { analyzePrompt } from '../services/api';

// // const SafetyCheck = () => {
// //     const [result, setResult] = useState(null);
// //     const [isLoading, setIsLoading] = useState(false);
// //     const [error, setError] = useState(null);

// //     const handleAnalyze = async (prompt) => {
// //         setIsLoading(true);
// //         setError(null);

// //         try {
// //             const response = await analyzePrompt(prompt);

// //             if (response.success) {
// //                 setResult(response.data);
// //             } else {
// //                 setError(response.error);
// //                 setResult(null);
// //             }
// //         } catch (err) {
// //             setError('Failed to analyze prompt. Please try again.');
// //             setResult(null);
// //         } finally {
// //             setIsLoading(false);
// //         }
// //     };

// //     return (
// //         <div className="space-y-6">
// //             {/* Page Header */}
// //             <div>
// //                 <h1 className="text-3xl font-bold text-text-primary">Safety Check</h1>
// //                 <p className="text-text-muted mt-1">Test prompt safety with real-time AI analysis</p>
// //             </div>

// //             {/* Error Banner */}
// //             {error && (
// //                 <div className="bg-danger-color bg-opacity-10 border border-danger-color border-opacity-30 rounded-xl p-4">
// //                     <div className="flex items-center space-x-2">
// //                         <span className="text-danger-color font-medium">Error:</span>
// //                         <span className="text-text-primary">{error}</span>
// //                     </div>
// //                 </div>
// //             )}

// //             {/* Input Section */}
// //             <PromptInput onAnalyze={handleAnalyze} isLoading={isLoading} />

// //             {/* Results Section */}
// //             <ResultPanel result={result} isLoading={isLoading} />
// //         </div>
// //     );
// // };

// // export default SafetyCheck;