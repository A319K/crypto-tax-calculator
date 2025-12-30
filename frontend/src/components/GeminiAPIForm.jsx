import { useState } from 'react';
import { Key, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';

const GeminiAPIForm = ({ onSync, isLoading }) => {
    const [apiKey, setApiKey] = useState('');
    const [apiSecret, setApiSecret] = useState('');
    const [isSandbox, setIsSandbox] = useState(true);
    const [symbol, setSymbol] = useState('btcusd');
    const [limit, setLimit] = useState(500);
    const [testStatus, setTestStatus] = useState(null); // 'success', 'error', or null

    const handleTest = async () => {
        if (!apiKey || !apiSecret) {
            alert('Please enter both API key and secret');
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/api-keys/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_key: apiKey,
                    api_secret: apiSecret,
                    is_sandbox: isSandbox,
                }),
            });

            if (response.ok) {
                setTestStatus('success');
            } else {
                setTestStatus('error');
            }
        } catch (error) {
            setTestStatus('error');
        }
    };

    const handleSync = () => {
        if (!apiKey || !apiSecret) {
            alert('Please enter both API key and secret');
            return;
        }

        onSync({
            apiKey,
            apiSecret,
            isSandbox,
            symbol,
            limit,
        });
    };

    return (
        <div className="w-full max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center space-x-3 mb-6">
                <Key className="h-6 w-6 text-blue-600" />
                <h3 className="text-xl font-semibold text-gray-800">
                    Connect Gemini Account
                </h3>
            </div>

            <div className="space-y-4">
                {/* Sandbox Toggle */}
                <div className="flex items-center space-x-3">
                    <input
                        type="checkbox"
                        id="sandbox"
                        checked={isSandbox}
                        onChange={(e) => setIsSandbox(e.target.checked)}
                        className="h-4 w-4 text-blue-600 rounded"
                    />
                    <label htmlFor="sandbox" className="text-sm text-gray-700">
                        Use Sandbox (Testing) Environment
                    </label>
                </div>

                {/* API Key */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        API Key
                    </label>
                    <input
                        type="text"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="Enter your Gemini API key"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={isLoading}
                    />
                </div>

                {/* API Secret */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        API Secret
                    </label>
                    <input
                        type="password"
                        value={apiSecret}
                        onChange={(e) => setApiSecret(e.target.value)}
                        placeholder="Enter your Gemini API secret"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={isLoading}
                    />
                </div>

                {/* Symbol Selection */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Trading Pair
                    </label>
                    <select
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={isLoading}
                    >
                        <option value="btcusd">BTC/USD</option>
                        <option value="ethusd">ETH/USD</option>
                        <option value="solusd">SOL/USD</option>
                        <option value="avaxusd">AVAX/USD</option>
                    </select>
                </div>

                {/* Limit */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Max Transactions (up to 500)
                    </label>
                    <input
                        type="number"
                        value={limit}
                        onChange={(e) => setLimit(Math.min(500, Math.max(1, parseInt(e.target.value) || 1)))}
                        min="1"
                        max="500"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={isLoading}
                    />
                </div>

                {/* Test Status */}
                {testStatus && (
                    <div className={`flex items-center space-x-2 p-3 rounded-lg ${
                        testStatus === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                    }`}>
                        {testStatus === 'success' ? (
                            <>
                                <CheckCircle className="h-5 w-5" />
                                <span>API credentials are valid!</span>
                            </>
                        ) : (
                            <>
                                <AlertCircle className="h-5 w-5" />
                                <span>Invalid API credentials. Please check and try again.</span>
                            </>
                        )}
                    </div>
                )}

                {/* Action Buttons */}
                <div className="flex space-x-3">
                    <button
                        onClick={handleTest}
                        disabled={isLoading}
                        className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
                    >
                        <Key className="h-4 w-4" />
                        <span>Test Connection</span>
                    </button>

                    <button
                        onClick={handleSync}
                        disabled={isLoading}
                        className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
                    >
                        <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                        <span>{isLoading ? 'Syncing...' : 'Sync & Calculate'}</span>
                    </button>
                </div>

                {/* Instructions */}
                <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-sm text-blue-800 font-medium mb-2">
                        How to get your Gemini API keys:
                    </p>
                    <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
                        <li>Log in to your Gemini account</li>
                        <li>Go to Settings → API</li>
                        <li>Create a new API key with "Auditor" role</li>
                        <li>Copy the API Key and Secret</li>
                        <li>For testing, use Sandbox environment first</li>
                    </ol>
                </div>
            </div>
        </div>
    );
};

export default GeminiAPIForm;