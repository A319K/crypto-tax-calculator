import { FileText, Trash2, Eye } from 'lucide-react';

const ReportsList = ({ reports, onViewReport, onDeleteReport }) => {
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    if (!reports || reports.length === 0) {
        return (
            <div className="text-center text-gray-500 py-8">
                No reports yet. Upload a CSV file to get started.
            </div>
        );
    }

    return (
        <div className="w-full max-w-4xl mx-auto space-y-4">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Past Reports</h3>

            {reports.map((report) => (
                <div
                    key={report.id}
                    className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
                >
                    <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-4 flex-1">
                            <FileText className="h-6 w-6 text-blue-600 mt-1" />
                            <div className="flex-1">
                                <h4 className="font-semibold text-gray-800">{report.filename}</h4>
                                <p className="text-sm text-gray-500 mt-1">
                                    {formatDate(report.upload_date)}
                                </p>
                                <div className="mt-3 flex items-center space-x-4 text-sm">
                  <span className={`font-medium ${
                      report.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatCurrency(report.total_gain_loss)}
                  </span>
                                    <span className="text-gray-600">
                    {report.num_transactions} transaction{report.num_transactions !== 1 ? 's' : ''}
                  </span>
                                </div>
                            </div>
                        </div>

                        <div className="flex space-x-2">
                            <button
                                onClick={() => onViewReport(report.id)}
                                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                title="View Report"
                            >
                                <Eye className="h-5 w-5" />
                            </button>
                            <button
                                onClick={() => onDeleteReport(report.id)}
                                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Delete Report"
                            >
                                <Trash2 className="h-5 w-5" />
                            </button>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default ReportsList;