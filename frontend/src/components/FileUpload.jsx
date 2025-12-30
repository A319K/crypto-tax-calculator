import { useState } from 'react';
import { Upload, FileText, X } from 'lucide-react';

const FileUpload = ({ onFileUpload, isLoading }) => {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (file) => {
        if (!file.name.endsWith('.csv')) {
            alert('Please upload a CSV file');
            return;
        }
        setSelectedFile(file);
    };

    const handleUpload = () => {
        if (selectedFile) {
            onFileUpload(selectedFile);
        }
    };

    const clearFile = () => {
        setSelectedFile(null);
    };

    return (
        <div className="w-full max-w-2xl mx-auto">
            <div
                className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    dragActive
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    accept=".csv"
                    onChange={handleChange}
                    disabled={isLoading}
                />

                {!selectedFile ? (
                    <div className="space-y-4">
                        <Upload className="mx-auto h-12 w-12 text-gray-400" />
                        <div>
                            <label
                                htmlFor="file-upload"
                                className="cursor-pointer text-blue-600 hover:text-blue-500 font-medium"
                            >
                                Choose a file
                            </label>
                            <span className="text-gray-600"> or drag and drop</span>
                        </div>
                        <p className="text-sm text-gray-500">
                            Gemini CSV files only
                        </p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div className="flex items-center justify-center space-x-2">
                            <FileText className="h-8 w-8 text-green-500" />
                            <span className="font-medium text-gray-700">{selectedFile.name}</span>
                            <button
                                onClick={clearFile}
                                className="text-red-500 hover:text-red-700"
                                disabled={isLoading}
                            >
                                <X className="h-5 w-5" />
                            </button>
                        </div>
                        <button
                            onClick={handleUpload}
                            disabled={isLoading}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                        >
                            {isLoading ? 'Calculating...' : 'Calculate Taxes'}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileUpload;