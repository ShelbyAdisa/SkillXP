import React, { useState } from 'react';
import { Plus, Clock, AlertCircle, Users, DollarSign, Trash2, CheckCircle, XCircle, Lock } from 'lucide-react';
import ConfirmModal from '../components/ConfirmModal';

const Transparency = () => {
  const [polls, setPolls] = useState([
    {
      id: 1,
      title: 'Emergency Roof Repairs - East Wing',
      description: 'Immediate repairs needed for water damage in classrooms 201-205. Contractor quotes received.',
      budget: 28000,
      deadline: '2025-10-12',
      status: 'active',
      urgent: true,
      votes: { yes: 18, no: 4 },
      totalVoters: 22,
      createdBy: 'Facilities Director - Mr. Johnson',
      createdAt: '2025-10-08'
    },
    {
      id: 2,
      title: 'New School Bus Procurement',
      description: 'Replace Bus #7 (15 years old) with new 52-passenger vehicle. Three bids evaluated.',
      budget: 95000,
      deadline: '2025-10-30',
      status: 'active',
      urgent: false,
      votes: { yes: 34, no: 12 },
      totalVoters: 46,
      createdBy: 'Transportation Coordinator - Mrs. Martinez',
      createdAt: '2025-10-01'
    },
    {
      id: 3,
      title: 'Playground Safety Surface Replacement',
      description: 'Replace worn playground surface with impact-absorbing material. Current surface fails safety inspection.',
      budget: 22000,
      deadline: '2025-09-30',
      status: 'closed',
      urgent: false,
      votes: { yes: 51, no: 2 },
      totalVoters: 53,
      createdBy: 'Safety Committee - Mr. Williams',
      createdAt: '2025-09-10',
      closureNote: 'Motion passed with overwhelming support (96% approval). Project awarded to SafePlay Industries. Installation scheduled for October 15-20 during fall break. Expected completion before students return.'
    }
  ]);

  const [isAdmin, setIsAdmin] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [pollToClose, setPollToClose] = useState(null);
  const [closureNote, setClosureNote] = useState('');
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [voteConfirmModal, setVoteConfirmModal] = useState({ open: false, pollId: null, voteType: null });
  const [pollToDelete, setPollToDelete] = useState(null);
  const [userVotes, setUserVotes] = useState({});
  
  const [newPoll, setNewPoll] = useState({
    title: '',
    description: '',
    budget: '',
    deadline: '',
    createdBy: '',
    urgent: false
  });

  const handleCreatePoll = () => {
    if (!newPoll.title || !newPoll.description || !newPoll.budget || !newPoll.deadline || !newPoll.createdBy) {
      return;
    }
    const poll = {
      id: polls.length + 1,
      ...newPoll,
      budget: parseFloat(newPoll.budget),
      status: 'active',
      votes: { yes: 0, no: 0 },
      totalVoters: 0,
      createdAt: new Date().toISOString().split('T')[0]
    };
    setPolls([poll, ...polls]);
    setShowCreateModal(false);
    setNewPoll({
      title: '',
      description: '',
      budget: '',
      deadline: '',
      createdBy: '',
      urgent: false
    });
  };

  const handleVoteClick = (pollId, voteType) => {
    setVoteConfirmModal({ open: true, pollId, voteType });
  };

  const confirmVote = () => {
    const { pollId, voteType } = voteConfirmModal;
    
    setPolls(polls.map(poll => {
      if (poll.id === pollId && poll.status === 'active' && !userVotes[pollId]) {
        const updatedVotes = { ...poll.votes };
        updatedVotes[voteType]++;

        return {
          ...poll,
          votes: updatedVotes,
          totalVoters: poll.totalVoters + 1
        };
      }
      return poll;
    }));
    
    setUserVotes({ ...userVotes, [pollId]: voteType });
    setVoteConfirmModal({ open: false, pollId: null, voteType: null });
  };

  const cancelVote = () => {
    setVoteConfirmModal({ open: false, pollId: null, voteType: null });
  };

  const handleClosePoll = (pollId) => {
    setPollToClose(pollId);
    setShowCloseModal(true);
  };

  const confirmClosePoll = () => {
    if (!closureNote.trim()) {
      alert('Please provide a resolution summary');
      return;
    }

    setPolls(polls.map(poll => 
      poll.id === pollToClose 
        ? { ...poll, status: 'closed', closureNote: closureNote }
        : poll
    ));
    
    setShowCloseModal(false);
    setPollToClose(null);
    setClosureNote('');
  };

  const handleDeletePoll = (pollId) => {
    setPollToDelete(pollId);
    setDeleteModalOpen(true);
  };

  const confirmDelete = () => {
    setPolls(polls.filter(poll => poll.id !== pollToDelete));
    const newUserVotes = { ...userVotes };
    delete newUserVotes[pollToDelete];
    setUserVotes(newUserVotes);
    setDeleteModalOpen(false);
    setPollToDelete(null);
  };

  const cancelDelete = () => {
    setDeleteModalOpen(false);
    setPollToDelete(null);
  };

  const getVotePercentage = (votes, total) => {
    return total > 0 ? ((votes / total) * 100).toFixed(1) : 0;
  };

  const isDeadlinePassed = (deadline) => {
    return new Date(deadline) < new Date();
  };

  const urgentCount = polls.filter(p => p.status === 'active' && p.urgent).length;

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 mb-1">School Governance Board</h1>
          <p className="text-slate-600">Parents voting on school budget proposals and capital expenditures</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsAdmin(!isAdmin)}
            className="px-4 py-2 rounded-full text-sm font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors"
          >
            {isAdmin ? 'Parent View' : 'Admin View'}
          </button>
          {isAdmin && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 bg-slate-900 text-white px-5 py-2.5 rounded-full hover:bg-slate-800 transition-colors font-medium"
            >
              <Plus size={18} />
              Submit Proposal
            </button>
          )}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-5 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600 text-sm font-medium">Urgent Proposals</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">{urgentCount}</p>
            </div>
            <div className="w-12 h-12 rounded-lg bg-red-100 flex items-center justify-center">
              <AlertCircle className="text-red-600" size={24} />
            </div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600 text-sm font-medium">Total Participants</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">
                {polls.reduce((sum, p) => sum + p.totalVoters, 0)}
              </p>
            </div>
            <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
              <Users className="text-blue-600" size={24} />
            </div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600 text-sm font-medium">Total Budget</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">
                ${polls.filter(p => p.status === 'active').reduce((sum, p) => sum + p.budget, 0).toLocaleString()}
              </p>
            </div>
            <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center">
              <DollarSign className="text-green-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Polls List */}
      <div className="space-y-4">
        {polls.map(poll => {
          const yesPercent = getVotePercentage(poll.votes.yes, poll.totalVoters);
          const noPercent = getVotePercentage(poll.votes.no, poll.totalVoters);
          const deadlinePassed = isDeadlinePassed(poll.deadline);
          const userVote = userVotes[poll.id];
          const canVote = poll.status === 'active' && !deadlinePassed && !userVote;

          return (
            <div key={poll.id} className="bg-white rounded-xl border border-slate-200">
              <div className="p-5">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-lg font-semibold text-slate-900">{poll.title}</h3>
                      {poll.urgent && poll.status === 'active' && (
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-700">
                          URGENT
                        </span>
                      )}
                      {poll.status === 'closed' && (
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
                          CLOSED
                        </span>
                      )}
                    </div>
                    <p className="text-slate-700 text-sm leading-relaxed mb-3">{poll.description}</p>
                    <div className="flex items-center gap-4 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <DollarSign size={14} />
                        ${poll.budget.toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock size={14} />
                        {poll.status === 'closed' ? 'Closed' : deadlinePassed ? 'Expired' : `Deadline: ${poll.deadline}`}
                      </span>
                      <span className="flex items-center gap-1">
                        <Users size={14} />
                        {poll.totalVoters} votes cast
                      </span>
                    </div>
                  </div>
                  {isAdmin && poll.status === 'active' && (
                    <div className="ml-4 flex gap-2">
                      <button
                        onClick={() => handleClosePoll(poll.id)}
                        className="px-3 py-1.5 text-sm bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-lg transition-colors font-medium"
                      >
                        Close Poll
                      </button>
                      <button
                        onClick={() => handleDeletePoll(poll.id)}
                        className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete proposal"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  )}
                </div>

                {/* Voting Section */}
                {poll.status === 'active' && !deadlinePassed && (
                  <div className="mb-4 pt-4 border-t border-slate-200">
                    {userVote ? (
                      <div className="bg-slate-50 rounded-lg p-4 text-center border border-slate-200">
                        <Lock className="w-5 h-5 text-slate-500 mx-auto mb-2" />
                        <p className="text-sm text-slate-700 font-medium">
                          You voted: <span className={userVote === 'yes' ? 'text-green-600' : 'text-red-600'}>
                            {userVote === 'yes' ? 'Yes' : 'No'}
                          </span>
                        </p>
                        <p className="text-xs text-slate-500 mt-1">Your vote has been recorded. Results will be visible when the poll closes.</p>
                      </div>
                    ) : (
                      <div className="flex gap-3">
                        <button
                          onClick={() => handleVoteClick(poll.id, 'yes')}
                          className="flex-1 py-2.5 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 bg-white border-2 border-green-600 text-green-700 hover:bg-green-50"
                        >
                          <CheckCircle size={18} />
                          Vote Yes
                        </button>
                        <button
                          onClick={() => handleVoteClick(poll.id, 'no')}
                          className="flex-1 py-2.5 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 bg-white border-2 border-red-600 text-red-700 hover:bg-red-50"
                        >
                          <XCircle size={18} />
                          Vote No
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Results Section - Only show if closed */}
                {poll.status === 'closed' && (
                  <div className="space-y-3 pt-4 border-t border-slate-200">
                    <div>
                      <div className="flex justify-between text-sm mb-1.5">
                        <span className="text-slate-700 font-medium flex items-center gap-1.5">
                          <div className="w-3 h-3 bg-green-500 rounded"></div>
                          Approve
                        </span>
                        <span className="text-slate-600 font-medium">{poll.votes.yes} ({yesPercent}%)</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full transition-all duration-500" 
                          style={{ width: `${yesPercent}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1.5">
                        <span className="text-slate-700 font-medium flex items-center gap-1.5">
                          <div className="w-3 h-3 bg-red-500 rounded"></div>
                          Reject
                        </span>
                        <span className="text-slate-600 font-medium">{poll.votes.no} ({noPercent}%)</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2">
                        <div 
                          className="bg-red-500 h-2 rounded-full transition-all duration-500" 
                          style={{ width: `${noPercent}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Hidden Results Message */}
                {poll.status === 'active' && userVote && (
                  <div className="pt-4 border-t border-slate-200">
                    <p className="text-sm text-slate-500 italic text-center py-2">
                      Results will be visible when the poll closes
                    </p>
                  </div>
                )}

                {/* Closure Note */}
                {poll.status === 'closed' && poll.closureNote && (
                  <div className="mt-4 pt-4 border-t border-slate-200">
                    <h4 className="text-sm font-semibold text-slate-900 mb-2">Resolution Summary</h4>
                    <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-200">
                      {poll.closureNote}
                    </p>
                  </div>
                )}

                <div className="mt-4 pt-3 border-t border-slate-200 text-xs text-slate-500">
                  Submitted by {poll.createdBy} on {poll.createdAt}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Create Poll Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto border border-slate-200">
            <h2 className="text-2xl font-bold text-slate-900 mb-1">Submit New Proposal</h2>
            <p className="text-sm text-slate-600 mb-6">Faculty and staff only - All proposals require board review</p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Proposal Title</label>
                <input
                  type="text"
                  value={newPoll.title}
                  onChange={(e) => setNewPoll({ ...newPoll, title: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 text-sm"
                  placeholder="e.g., Library Expansion Project"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Detailed Description</label>
                <textarea
                  value={newPoll.description}
                  onChange={(e) => setNewPoll({ ...newPoll, description: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 text-sm resize-none"
                  rows="4"
                  placeholder="Provide comprehensive details about the proposal, justification, and expected outcomes..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Budget Amount ($)</label>
                  <input
                    type="number"
                    value={newPoll.budget}
                    onChange={(e) => setNewPoll({ ...newPoll, budget: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 text-sm"
                    placeholder="25000"
                    min="0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Voting Deadline</label>
                  <input
                    type="date"
                    value={newPoll.deadline}
                    onChange={(e) => setNewPoll({ ...newPoll, deadline: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Submitted By (Name & Title)</label>
                <input
                  type="text"
                  value={newPoll.createdBy}
                  onChange={(e) => setNewPoll({ ...newPoll, createdBy: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 text-sm"
                  placeholder="e.g., Principal Dr. Smith"
                />
              </div>

              <div className="flex items-center gap-3 pt-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newPoll.urgent}
                    onChange={(e) => setNewPoll({ ...newPoll, urgent: e.target.checked })}
                    className="w-4 h-4 text-red-600 border-slate-300 rounded focus:ring-red-500"
                  />
                  <span className="text-sm font-medium text-slate-700">Mark as urgent</span>
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2.5 border border-slate-200 text-slate-700 rounded-full font-medium hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleCreatePoll}
                  className="flex-1 px-4 py-2.5 bg-slate-900 text-white rounded-full font-medium hover:bg-slate-800 transition-colors"
                >
                  Submit Proposal
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Close Poll Modal */}
      {showCloseModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full p-6 border border-slate-200">
            <h2 className="text-2xl font-bold text-slate-900 mb-1">Close Poll & Add Resolution</h2>
            <p className="text-sm text-slate-600 mb-6">Provide a summary of the final decision and next steps</p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Resolution Summary</label>
                <textarea
                  value={closureNote}
                  onChange={(e) => setClosureNote(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 text-sm resize-none"
                  rows="6"
                  placeholder="Motion passed/rejected with X% approval. Include details about contractor selection, timeline, next steps, etc..."
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCloseModal(false);
                    setPollToClose(null);
                    setClosureNote('');
                  }}
                  className="flex-1 px-4 py-2.5 border border-slate-200 text-slate-700 rounded-full font-medium hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={confirmClosePoll}
                  className="flex-1 px-4 py-2.5 bg-slate-900 text-white rounded-full font-medium hover:bg-slate-800 transition-colors"
                >
                  Close Poll
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Vote Confirmation Modal */}
      {voteConfirmModal.open && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center">
          <div className="bg-white rounded-xl shadow-xl p-6 w-[90%] max-w-sm border border-slate-200">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">
              Are you sure you want to vote {voteConfirmModal.voteType === 'yes' ? 'YES' : 'NO'}? You cannot change your vote once submitted.
            </h3>
            <div className="flex justify-center gap-3">
              <button
                onClick={cancelVote}
                className="px-6 py-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-900 font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmVote}
                className="px-6 py-2 rounded-full bg-slate-900 hover:bg-slate-800 text-white font-medium transition-colors"
              >
                Confirm Vote
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirm Delete Modal */}
      {deleteModalOpen && (
        <ConfirmModal
          message="Are you sure you want to delete this proposal? This action cannot be undone."
          onConfirm={confirmDelete}
          onCancel={cancelDelete}
        />
      )}
    </div>
  );
};

export default Transparency;