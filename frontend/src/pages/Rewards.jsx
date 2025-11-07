import { useState } from 'react';
import { Award, Gift, CheckCircle, Lock } from 'lucide-react';
import DashboardLayout from '../components/layout/DashboardLayout';

export default function Rewards() {
  const [userPoints, setUserPoints] = useState(120);
  const [selectedReward, setSelectedReward] = useState(null);

  const rewards = [
    { id: 1, name: 'Free School Lunch', points: 50, icon: '🍽️', description: 'One free meal at the cafeteria' },
    { id: 2, name: 'Bus Pass', points: 80, icon: '🚌', description: 'One free bus ride home' },
    { id: 3, name: 'School Supplies Pack', points: 150, icon: '📚', description: 'Notebook, pens, and pencils' },
    { id: 4, name: 'Library Late Fee Waiver', points: 30, icon: '📖', description: 'Waive one late fee' },
    { id: 5, name: 'Locker Rental', points: 200, icon: '🔐', description: 'Free locker for one semester' },
  ];

  const handleRedeem = (reward) => {
    setSelectedReward(reward);
  };

  const confirmRedeem = () => {
    if (selectedReward && userPoints >= selectedReward.points) {
      setUserPoints((prev) => prev - selectedReward.points);
    }
    setSelectedReward(null);
  };

  const cancelRedeem = () => {
    setSelectedReward(null);
  };

  return (
    <DashboardLayout user="STUDENT">
      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Redeem Your Points</h2>
            <p className="text-slate-600">Help others and earn rewards for essential school items</p>
          </div>
          <div className="flex items-center gap-2 bg-slate-900 text-white px-5 py-3 rounded-full">
            <Award className="w-5 h-5" />
            <span className="font-semibold">{userPoints} pts</span>
          </div>
        </div>

        {/* Rewards Grid */}
        <div className="grid gap-4">
          {rewards.map((reward) => {
            const canRedeem = userPoints >= reward.points;
            return (
              <div
                key={reward.id}
                className={`bg-white rounded-xl border-2 p-6 transition-all ${
                  canRedeem
                    ? 'border-slate-900 hover:shadow-lg'
                    : 'border-slate-200 opacity-60'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-4xl">{reward.icon}</div>
                    <div>
                      <h3 className="font-semibold text-lg text-slate-900">
                        {reward.name}
                      </h3>
                      <p className="text-slate-600 text-sm">{reward.description}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <Gift className="w-4 h-4 text-slate-500" />
                        <span className="font-medium text-slate-900">{reward.points} points</span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleRedeem(reward)}
                    disabled={!canRedeem}
                    className={`px-6 py-3 rounded-full font-medium flex items-center gap-2 transition-all ${
                      canRedeem
                        ? 'bg-slate-900 text-white hover:bg-slate-800'
                        : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                    }`}
                  >
                    {canRedeem ? (
                      <>
                        <CheckCircle className="w-5 h-5" />
                        Redeem
                      </>
                    ) : (
                      <>
                        <Lock className="w-5 h-5" />
                        Locked
                      </>
                    )}
                  </button>
                </div>
                {!canRedeem && (
                  <div className="mt-4 bg-slate-50 rounded-lg p-3">
                    <p className="text-sm text-slate-600">
                      You need <strong>{reward.points - userPoints} more points</strong> to unlock this reward
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Confirmation Modal integrated directly */}
      {selectedReward && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center">
          <div className="bg-white rounded-xl shadow-xl p-6 w-[90%] max-w-sm border border-slate-200">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">
              {`Redeem ${selectedReward.name} for ${selectedReward.points} points?`}
            </h3>
            <div className="flex justify-center gap-3">
              <button
                onClick={cancelRedeem}
                className="px-6 py-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-900 font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmRedeem}
                className="px-6 py-2 rounded-full bg-slate-900 hover:bg-slate-800 text-white font-medium transition-colors"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}