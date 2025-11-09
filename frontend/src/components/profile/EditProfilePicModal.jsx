import React, { useState, useCallback } from 'react';
import { X, UploadCloud } from 'lucide-react';
// You would typically install this: `npm install react-dropzone`
// For this dummy component, we'll simulate its basic behavior.

function EditProfilePicModal({ currentAvatar, onClose, onSave }) {
  const [newImage, setNewImage] = useState(null);
  const [preview, setPreview] = useState(null);

  // Simulates file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setNewImage(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  // Simulates dropping a file
  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setNewImage(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleSave = () => {
    // In a real app, you would upload `newImage` to your server,
    // get back a new URL, and then call onSave(newUrl).
    // For this dummy version, we'll just pass back the local blob URL.
    if (preview) {
      onSave(preview);
    }
  };

  return (
    // Backdrop (dimmed)
    <div 
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-50 p-4 backdrop-blur-sm"
    >
      {/* Modal Content */}
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-lg bg-white dark:bg-gray-800 rounded-lg shadow-xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b dark:border-gray-700">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Update Profile Picture
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4">
          <div className="flex justify-center items-center gap-6">
            <span className="text-sm font-medium text-gray-500">Current</span>
            <img 
              src={currentAvatar} 
              alt="Current" 
              className="h-24 w-24 rounded-full object-cover bg-gray-200" 
            />
            {preview && (
              <>
                <span className="text-sm font-medium text-gray-500">New</span>
                <img 
                  src={preview} 
                  alt="Preview" 
                  className="h-24 w-24 rounded-full object-cover" 
                />
              </>
            )}
          </div>

          {/* Simulated Dropzone */}
          <div 
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            className="relative border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-10 text-center cursor-pointer hover:border-indigo-500 dark:hover:border-indigo-400"
          >
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="flex flex-col items-center">
              <UploadCloud className="h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                <span className="font-semibold text-indigo-600 dark:text-indigo-400">Click to upload</span> or drag and drop
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">PNG, JPG, GIF up to 5MB</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 bg-gray-50 dark:bg-gray-700/50 border-t dark:border-gray-700 rounded-b-lg">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 dark:bg-gray-600 dark:text-gray-200 dark:border-gray-500 dark:hover:bg-gray-500"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!newImage}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed dark:disabled:bg-indigo-800 dark:disabled:text-gray-400"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

export default EditProfilePicModal;