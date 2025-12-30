import { useState, useEffect } from 'react';
import { Calculator } from 'lucide-react';
import FileUpload from './components/FileUpload';
import TaxSummary from './components/TaxSummary';
import TransactionTable from './components/TransactionTable';
import ReportsList from './components/ReportsList';
import { uploadCSV, getAllReports, getReport, deleteReport } from './services/api';
import GeminiAPIForm from './components/GeminiAPIForm';

function App() {
    const [loading, setLoading] = useState(false);
    const [currentReport, setCurrentReport] = useState(null);
    const [allReports, setAllReports] = useState([]);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'reports'

    useEffect(() => {
        loadReports();
    }, []);

    const loadReports = async () => {
        try {
            const reports = await getAllReports();
            setAllReports(reports);
        } catch (err) {
            console.error('Error loading reports:', err);
        }
    };

    const handleFileUpload = async (file) => {
        setLoading(true);
        setError(null);

        try {
            const uploadResult = await uploadCSV(file);
            const reportData = await getReport(uploadResult.report_id);
            setCurrentReport(reportData);
            await loadReports();
            setActiveTab('upload'); // Stay on upload tab to show results
        } catch (err) {
            setError(err.response?.data?.detail || 'Error uploading file. Please try again.');
            console.error('Error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleViewReport = async (reportId) => {
        setLoading(true);
        try {
            const reportData = await getReport(reportId);
            setCurrentReport(reportData);
            setActiveTab('upload'); // Switch to upload tab to show report
        } catch (err) {
            setError('Error loading report');
            console.error('Error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteReport = async (reportId) => {
        if (!window.confirm('Are you sure you want to delete this report?')) {
            return;
        }

        try {
            await deleteReport(reportId);
            await loadReports();
            if (currentReport && currentReport.report_id === reportId) {
                setCurrentReport(null);
            }
        } catch (err) {
            setError('Error deleting report');
            console.error('Error:', err);
        }
    };

    const handleNewCalculation = () => {
        setCurrentReport(null);
        setError(null);
    };

    const handleAPISync = async (apiData) => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('http://127.0.0.1:8000/gemini/sync', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_key: apiData.apiKey,
                    api_secret: apiData.apiSecret,
                    is_sandbox: apiData.isSandbox,
                    symbol: apiData.symbol,
                    limit: apiData.limit,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to sync from Gemini');
            }

            const result = await response.json();
            const reportData = await getReport(result.report_id);
            setCurrentReport(reportData);
            await loadReports();
            setActiveTab('upload'); // Show results
        } catch (err) {
            setError(err.message || 'Error syncing from Gemini');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
                    <div className="flex items-center space-x-3">
                        <Calculator className="h-8 w-8 text-blue-600" />
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">
                                Crypto Tax Calculator
                            </h1>
                            <p className="text-sm text-gray-600">
                                Calculate capital gains for Gemini transactions
                            </p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Tabs */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
                <div className="border-b border-gray-200">
                    <nav className="-mb-px flex space-x-8">
                        <button
                            onClick={() => setActiveTab('upload')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${
                                activeTab === 'upload'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            Calculate Taxes
                        </button>
                        <button
                            onClick={() => setActiveTab('reports')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${
                                activeTab === 'reports'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            Past Reports ({allReports.length})
                        </button>
                    </nav>
                </div>
            </div>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
                {error && (
                    <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded">
                        <p className="text-red-700">{error}</p>
                    </div>
                )}

                {activeTab === 'upload' && (
                    <div className="space-y-8">
                        {!currentReport && (
                            <FileUpload onFileUpload={handleFileUpload} isLoading={loading} />
                        )}

                        {currentReport && (
                            <>
                                <div className="flex justify-end">
                                    <button
                                        onClick={handleNewCalculation}
                                        className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                                    >
                                        New Calculation
                                    </button>
                                </div>

                                <TaxSummary report={currentReport} />

                                {currentReport.capital_gains && currentReport.capital_gains.length > 0 && (
                                    <TransactionTable capitalGains={currentReport.capital_gains} />
                                )}
                            </>
                        )}
                    </div>
                )}

                {activeTab === 'reports' && (
                    <ReportsList
                        reports={allReports}
                        onViewReport={handleViewReport}
                        onDeleteReport={handleDeleteReport}
                    />
                )}
            </main>

            {/* Footer */}
            <footer className="bg-white border-t border-gray-200 mt-12">
                <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
                    <p className="text-center text-sm text-gray-500">
                        ⚠️ For educational purposes only. Consult a tax professional for official tax advice.
                    </p>
                </div>
            </footer>
        </div>
    );
}

export default App;