import React, { useState } from 'react';
import './App.css';

const productTypes = [
  'Booklet', 'Brochure', 'Flyer', 'Signage', 'Business Cards', 'Posters', 'Banners', 'Stickers', 'Catalogues', 'Newsletters'
];

const finishedSizes = [
  'A6 (105 × 148mm)', 'A5 (148 × 210mm)', 'A4 (210 × 297mm)', 'A3 (297 × 420mm)', 
  'DL (99 × 210mm)', 'Custom Size'
];

const coverStockOptions = [
  '300gsm Gloss Art', '300gsm Matt Art', '350gsm Silk', '400gsm Uncoated',
  '250gsm Gloss Art', '250gsm Matt Art', '300gsm Uncoated', '350gsm Gloss Art'
];

const textStockOptions = [
  '80gsm Uncoated', '100gsm Uncoated', '115gsm Gloss Art', '128gsm Gloss Art',
  '150gsm Gloss Art', '170gsm Gloss Art', '200gsm Gloss Art', '250gsm Gloss Art'
];

const finishingOptions = [
  'Matt Laminate', 'Gloss Laminate', 'Spot UV', 'Foiling (Gold)', 'Foiling (Silver)', 'Foiling (Other)',
  'Embossing', 'Debossing', 'Die Cutting', 'Perfect Binding', 'Saddle Stitching'
];

const deliveryLocations = [
  'Metro Melbourne', 'Regional Victoria', 'Interstate (NSW)', 'Interstate (QLD)', 
  'Interstate (SA)', 'Interstate (WA)', 'Interstate (TAS)', 'Interstate (NT)', 'Interstate (ACT)'
];

const inkOptions = [
  'CMYK', 'Black Only', 'Custom'
];

function App() {
  const [formData, setFormData] = useState({
    clientName: '',
    productType: '',
    finishedSize: '',
    pageCount: '',
    sidedness: 'single',
    coverStock: '',
    textStock: '',
    finishingOptions: [],
    quantity: '',
    deliveryLocation: '',
    specialRequirements: '',
    inkType: '',
    pmsColors: false,
    pmsColorCount: 1
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');
  const [currentQuote, setCurrentQuote] = useState(null);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleFinishingChange = (option) => {
    setFormData(prev => ({
      ...prev,
      finishingOptions: prev.finishingOptions.includes(option)
        ? prev.finishingOptions.filter(item => item !== option)
        : [...prev.finishingOptions, option]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitMessage('');

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      // Convert camelCase to snake_case for backend
      const backendData = {
        client_name: formData.clientName,
        product_type: formData.productType,
        finished_size: formData.finishedSize,
        page_count: parseInt(formData.pageCount),
        sidedness: formData.sidedness,
        cover_stock: formData.coverStock,
        text_stock: formData.textStock,
        finishing_options: formData.finishingOptions,
        quantity: parseInt(formData.quantity),
        delivery_location: formData.deliveryLocation,
        special_requirements: formData.specialRequirements,
        ink_type: formData.inkType,
        pms_colors: formData.pmsColors,
        pms_color_count: parseInt(formData.pmsColorCount)
      };

      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/quotes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backendData),
      });

      if (response.ok) {
        const result = await response.json();
        setCurrentQuote(result);
        setSubmitMessage(`Quote generated successfully! Quote ID: ${result.quote_id}`);
        // Reset form
        setFormData({
          clientName: '',
          productType: '',
          finishedSize: '',
          pageCount: '',
          sidedness: 'single',
          coverStock: '',
          textStock: '',
          finishingOptions: [],
          quantity: '',
          deliveryLocation: '',
          specialRequirements: '',
          inkType: '',
          pmsColors: false,
          pmsColorCount: 1
        });
      } else {
        setSubmitMessage('Error generating quote. Please try again.');
      }
    } catch (error) {
      setSubmitMessage('Error connecting to server. Please try again.');
    }

    setIsSubmitting(false);
  };

  const handleExportQuote = async () => {
    if (!currentQuote) return;
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/quotes/${currentQuote.quote_id}/export`, {
        method: 'GET',
        headers: {
          'Accept': 'application/pdf',
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `quote_${currentQuote.quote_id}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        alert('Error exporting quote. Please try again.');
      }
    } catch (error) {
      alert('Error exporting quote. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Print Quote Assistant</h1>
          <p className="text-gray-600 text-lg">Professional Quote Generation Tool</p>
          <div className="w-24 h-1 bg-indigo-500 mx-auto mt-4 rounded-full"></div>
        </div>

        {/* Main Form */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              
              {/* Client Information Section */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
                  <span className="bg-indigo-100 text-indigo-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">1</span>
                  Client Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="clientName" className="block text-sm font-medium text-gray-700 mb-2">
                      Client Name *
                    </label>
                    <input
                      type="text"
                      id="clientName"
                      name="clientName"
                      value={formData.clientName}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                      placeholder="Enter client name"
                    />
                  </div>
                </div>
              </div>

              {/* Product Specifications Section */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
                  <span className="bg-indigo-100 text-indigo-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">2</span>
                  Product Specifications
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  
                  <div>
                    <label htmlFor="productType" className="block text-sm font-medium text-gray-700 mb-2">
                      Product Type *
                    </label>
                    <select
                      id="productType"
                      name="productType"
                      value={formData.productType}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                    >
                      <option value="">Select product type</option>
                      {productTypes.map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="finishedSize" className="block text-sm font-medium text-gray-700 mb-2">
                      Finished Size *
                    </label>
                    <select
                      id="finishedSize"
                      name="finishedSize"
                      value={formData.finishedSize}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                    >
                      <option value="">Select size</option>
                      {finishedSizes.map(size => (
                        <option key={size} value={size}>{size}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="pageCount" className="block text-sm font-medium text-gray-700 mb-2">
                      Page Count *
                    </label>
                    <input
                      type="number"
                      id="pageCount"
                      name="pageCount"
                      value={formData.pageCount}
                      onChange={handleInputChange}
                      required
                      min="1"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                      placeholder="e.g., 4"
                    />
                  </div>

                  <div>
                    <label htmlFor="sidedness" className="block text-sm font-medium text-gray-700 mb-2">
                      Printing *
                    </label>
                    <div className="flex space-x-4">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="sidedness"
                          value="single"
                          checked={formData.sidedness === 'single'}
                          onChange={handleInputChange}
                          className="mr-2 text-indigo-600 focus:ring-indigo-500"
                        />
                        Single Sided
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="sidedness"
                          value="double"
                          checked={formData.sidedness === 'double'}
                          onChange={handleInputChange}
                          className="mr-2 text-indigo-600 focus:ring-indigo-500"
                        />
                        Double Sided
                      </label>
                    </div>
                  </div>

                  <div>
                    <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-2">
                      Quantity *
                    </label>
                    <input
                      type="number"
                      id="quantity"
                      name="quantity"
                      value={formData.quantity}
                      onChange={handleInputChange}
                      required
                      min="1"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                      placeholder="e.g., 500"
                    />
                  </div>

                  <div>
                    <label htmlFor="inkType" className="block text-sm font-medium text-gray-700 mb-2">
                      Ink Type *
                    </label>
                    <select
                      id="inkType"
                      name="inkType"
                      value={formData.inkType}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                    >
                      <option value="">Select ink type</option>
                      {inkOptions.map(ink => (
                        <option key={ink} value={ink}>{ink}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* PMS Colors Section */}
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <label className="flex items-center mb-3">
                    <input
                      type="checkbox"
                      name="pmsColors"
                      checked={formData.pmsColors}
                      onChange={handleInputChange}
                      className="mr-3 text-indigo-600 focus:ring-indigo-500 rounded"
                    />
                    <span className="text-sm font-medium text-gray-700">PMS Colors Required</span>
                  </label>
                  
                  {formData.pmsColors && (
                    <div className="mt-3">
                      <label htmlFor="pmsColorCount" className="block text-sm font-medium text-gray-700 mb-2">
                        Number of PMS Colors
                      </label>
                      <select
                        id="pmsColorCount"
                        name="pmsColorCount"
                        value={formData.pmsColorCount}
                        onChange={handleInputChange}
                        className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                      >
                        {[1,2,3,4,5,6,7,8].map(num => (
                          <option key={num} value={num}>{num}</option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>
              </div>

              {/* Material Specifications Section */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
                  <span className="bg-indigo-100 text-indigo-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">3</span>
                  Material Specifications
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  
                  <div>
                    <label htmlFor="coverStock" className="block text-sm font-medium text-gray-700 mb-2">
                      Cover Stock
                    </label>
                    <select
                      id="coverStock"
                      name="coverStock"
                      value={formData.coverStock}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                    >
                      <option value="">Select cover stock</option>
                      {coverStockOptions.map(stock => (
                        <option key={stock} value={stock}>{stock}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="textStock" className="block text-sm font-medium text-gray-700 mb-2">
                      Text Stock
                    </label>
                    <select
                      id="textStock"
                      name="textStock"
                      value={formData.textStock}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                    >
                      <option value="">Select text stock</option>
                      {textStockOptions.map(stock => (
                        <option key={stock} value={stock}>{stock}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Finishing Options Section */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
                  <span className="bg-indigo-100 text-indigo-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">4</span>
                  Finishing Options
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {finishingOptions.map(option => (
                    <label key={option} className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors duration-200">
                      <input
                        type="checkbox"
                        checked={formData.finishingOptions.includes(option)}
                        onChange={() => handleFinishingChange(option)}
                        className="mr-3 text-indigo-600 focus:ring-indigo-500 rounded"
                      />
                      <span className="text-sm text-gray-700">{option}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Delivery Section */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
                  <span className="bg-indigo-100 text-indigo-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">5</span>
                  Delivery Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  
                  <div>
                    <label htmlFor="deliveryLocation" className="block text-sm font-medium text-gray-700 mb-2">
                      Delivery Location *
                    </label>
                    <select
                      id="deliveryLocation"
                      name="deliveryLocation"
                      value={formData.deliveryLocation}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                    >
                      <option value="">Select delivery location</option>
                      {deliveryLocations.map(location => (
                        <option key={location} value={location}>{location}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="specialRequirements" className="block text-sm font-medium text-gray-700 mb-2">
                      Special Requirements
                    </label>
                    <textarea
                      id="specialRequirements"
                      name="specialRequirements"
                      value={formData.specialRequirements}
                      onChange={handleInputChange}
                      rows="3"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                      placeholder="Any special requirements or notes..."
                    />
                  </div>
                </div>
              </div>

              {/* Submit Section */}
              <div className="pt-4">
                <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
                  <div className="text-sm text-gray-600">
                    * Required fields
                  </div>
                  <div className="flex gap-3">
                    {currentQuote && (
                      <button
                        type="button"
                        onClick={handleExportQuote}
                        className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center"
                      >
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Export PDF
                      </button>
                    )}
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200 flex items-center justify-center"
                    >
                      {isSubmitting ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          Generating Quote...
                        </>
                      ) : (
                        'Generate Quote'
                      )}
                    </button>
                  </div>
                </div>
                
                {submitMessage && (
                  <div className={`mt-4 p-4 rounded-lg ${submitMessage.includes('successfully') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {submitMessage}
                  </div>
                )}
              </div>
            </form>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          Print Quote Assistant • Professional Quote Generation Tool
        </div>
      </div>
    </div>
  );
}

export default App;