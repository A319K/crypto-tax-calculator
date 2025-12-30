import { DollarSign, TrendingUp, TrendingDown, Calendar } from 'lucide-react';

const TaxSummary = ({ report }) => {
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
        });
    };

    const isProfit = report.total_gain_loss >= 0;

    return (
        <div className="w-full max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold text-gray-800">Tax Report</h2>
                    <span className="text-sm text-gray-500">
            {formatDate(report.upload_date)}
          </span>
                </div>
                <p className="text-gray-600">File: {report.filename}</p>
            </div>

            {/* Main Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Total Gain/Loss */}
                <div className={`rounded-lg shadow-md p-6 ${
                    isProfit ? 'bg-green-50 border-l-4 border-green-500' : 'bg-red-50 border-l-4 border-red-500'
                }`}>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-600">Total Gain/Loss</span>
                        <DollarSign className={`h-5 w-5 ${isProfit ? 'text-green-600' : 'text-red-600'}`} />
                    </div>
                    <p className={`text-3xl font-bold ${isProfit ? 'text-green-700' : 'text-red-700'}`}>
                        {formatCurrency(report.total_gain_loss)}
                    </p>
                </div>

                {/* Short-term */}
                <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-600">Short-term</span>
                        <TrendingUp className="h-5 w-5 text-orange-600" />
                    </div>
                    <p className="text-2xl font-bold text-gray-800">
                        {formatCurrency(report.short_term_gain_loss)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                        {report.num_short_term} transaction{report.num_short_term !== 1 ? 's' : ''}
                    </p>
                </div>

                {/* Long-term */}
                <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-600">Long-term</span>
                        <Calendar className="h-5 w-5 text-blue-600" />
                    </div>
                    <p className="text-2xl font-bold text-gray-800">
                        {formatCurrency(report.long_term_gain_loss)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                        {report.num_long_term} transaction{report.num_long_term !== 1 ? 's' : ''}
                    </p>
                </div>
            </div>

            {/* Tax Filing Info */}
            <div className="bg-blue-50 rounded-lg shadow-md p-6 border-l-4 border-blue-500">
                <h3 className="font-semibold text-gray-800 mb-2">Tax Filing Information</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                    <li>• Short-term gains are taxed as ordinary income</li>
                    <li>• Long-term gains qualify for reduced capital gains rates</li>
                    <li>• Report on IRS Form 8949 and Schedule D</li>
                    <li>• Keep this report for your tax records</li>
                </ul>
            </div>
        </div>
    );
};

export default TaxSummary;