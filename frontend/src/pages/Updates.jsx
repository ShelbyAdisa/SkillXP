import { useState } from 'react';
import { Bell, Trash2, Send, Calendar } from 'lucide-react';
import ConfirmModal from '../components/ConfirmModal';

export default function Updates() {
  // Change this to true to see admin view
  const [isAdmin, setIsAdmin] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [updateToDelete, setUpdateToDelete] = useState(null);
  
  const [updates, setUpdates] = useState([
    {
      id: 1,
      title: 'School Assembly Tomorrow',
      content: 'There will be a mandatory assembly tomorrow at 9 AM in the main hall. All students must attend.',
      timestamp: '2 hours ago',
      date: 'Oct 09, 2025'
    },
    {
      id: 2,
      title: 'Library Hours Extended',
      content: 'The library will now be open until 8 PM on weekdays to give students more study time.',
      timestamp: '1 day ago',
      date: 'Oct 08, 2025'
    },
    {
      id: 3,
      title: 'Sports Day Registration',
      content: 'Registration for Sports Day is now open! Sign up at the front office before Friday.',
      timestamp: '3 days ago',
      date: 'Oct 06, 2025'
    }
  ]);

  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');

  const handlePublish = () => {
    if (newTitle.trim() && newContent.trim()) {
      setUpdates([{
        id: updates.length + 1,
        title: newTitle,
        content: newContent,
        timestamp: 'Just now',
        date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
      }, ...updates]);
      setNewTitle('');
      setNewContent('');
    }
  };

  const handleDelete = (id) => {
    setUpdateToDelete(id);
    setDeleteModalOpen(true);
  };

  const confirmDelete = () => {
    setUpdates(updates.filter(update => update.id !== updateToDelete));
    setDeleteModalOpen(false);
    setUpdateToDelete(null);
  };

  const cancelDelete = () => {
    setDeleteModalOpen(false);
    setUpdateToDelete(null);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-lg bg-slate-900 flex items-center justify-center">
            <Bell className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">School Updates</h1>
            <p className="text-slate-600 text-sm">
              {isAdmin ? 'Publish announcements to all students' : 'Stay informed about school news'}
            </p>
          </div>
        </div>
        
        {/* Admin toggle (for demo purposes) */}
        <button
          onClick={() => setIsAdmin(!isAdmin)}
          className="px-4 py-2 rounded-full text-sm font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors"
        >
          {isAdmin ? 'Student View' : 'Admin View'}
        </button>
      </div>

      {/* Admin - Publish Update */}
      {isAdmin && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6">
          <h2 className="font-semibold text-lg text-slate-900 mb-4">Publish New Update</h2>
          
          <input
            type="text"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Update title..."
            className="w-full p-3 border border-slate-200 rounded-lg mb-3 focus:outline-none focus:ring-2 focus:ring-slate-900"
          />
          
          <textarea
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            placeholder="Update content..."
            className="w-full p-3 border border-slate-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-slate-900"
            rows="4"
          />
          
          <div className="flex justify-end mt-3">
            <button
              onClick={handlePublish}
              disabled={!newTitle.trim() || !newContent.trim()}
              className="bg-slate-900 text-white px-6 py-2 rounded-full font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              Publish Update
            </button>
          </div>
        </div>
      )}

      {/* Updates List */}
      <div className="space-y-4">
        {updates.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <Bell className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500">No updates yet</p>
          </div>
        ) : (
          updates.map((update) => (
            <div key={update.id} className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="w-4 h-4 text-slate-500" />
                    <span className="text-sm text-slate-500">{update.date} • {update.timestamp}</span>
                  </div>
                  <h3 className="font-semibold text-lg text-slate-900 mb-2">
                    {update.title}
                  </h3>
                  <p className="text-slate-700 leading-relaxed">
                    {update.content}
                  </p>
                </div>
                
                {isAdmin && (
                  <button
                    onClick={() => handleDelete(update.id)}
                    className="text-red-500 hover:text-red-600 transition-colors p-2"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Confirm Delete Modal */}
      {deleteModalOpen && (
        <ConfirmModal
          message="Are you sure you want to delete this update?"
          onConfirm={confirmDelete}
          onCancel={cancelDelete}
        />
      )}
    </div>
  );
}