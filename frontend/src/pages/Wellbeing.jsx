import React, { useEffect, useState, useRef } from 'react'
import DashboardLayout from '../components/layout/DashboardLayout'
import Card from '../components/shared/Card'
import Button from '../components/shared/Button'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ConfirmModal from '../components/ConfirmModal'
import { Heart, Smile, Zap, BookOpen, MessageSquare, Shield, Youtube, X, Send } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

// --- DUMMY DATA START ---
const DUMMY_WELLBEING_DATA = {
  emotions: [
    { id: 1, label: 'Happy', icon: Smile, color: 'text-green-500', bgColor: 'bg-green-50' },
    { id: 2, label: 'Calm', icon: Shield, color: 'text-blue-500', bgColor: 'bg-blue-50' },
    { id: 3, label: 'Tired', icon: Zap, color: 'text-yellow-500', bgColor: 'bg-yellow-50' },
    { id: 4, label: 'Stressed', icon: Heart, color: 'text-red-500', bgColor: 'bg-red-50' },
  ],
  resources: [
    { title: 'Daily Mindful Minutes', type: 'Audio Guide', description: 'A 5-minute guided meditation to reset your focus.', icon: Youtube, action: 'https://www.youtube.com/watch?v=inpok4MKVLM' },
    { title: 'Talking to an Advisor', type: 'Support Chat', description: 'Immediate connection to a trained school advisor (Mon-Fri, 9am-5pm).', icon: MessageSquare, action: 'chat' },
    { title: 'Parent/Guardian Guide to School Stress', type: 'PDF', description: 'Resources for parents to understand and support their childrens emotional health.', icon: Shield, action: 'document' },
  ],
  checkInHistory: [
    { date: 'Oct 1, 2025', mood: 'Calm', note: 'Feeling good after finishing my science project.' },
    { date: 'Sep 28, 2025', mood: 'Tired', note: 'Long day of extracurriculars.' },
  ]
}
// --- DUMMY DATA END ---

const Wellbeing = () => {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [selectedMood, setSelectedMood] = useState(null)
  const [checkInMessage, setCheckInMessage] = useState(null)
  const [showMeditationGuide, setShowMeditationGuide] = useState(false)
  const [modalConfig, setModalConfig] = useState(null)
  const [showChatModal, setShowChatModal] = useState(false)
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [isChatLoading, setIsChatLoading] = useState(false)
  const [checkInHistory, setCheckInHistory] = useState(DUMMY_WELLBEING_DATA.checkInHistory)
  const [showParentGuide, setShowParentGuide] = useState(false)
  const chatEndRef = useRef(null)

  useEffect(() => {
    // Simulate loading data
    const loadData = async () => {
      setLoading(true)
      await new Promise(resolve => setTimeout(resolve, 500))
      setLoading(false)
    }
    loadData()
  }, [])

  useEffect(() => {
    // Auto-scroll chat to bottom
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages, isChatLoading])

  const handleCheckIn = (mood) => {
    setSelectedMood(mood)
    setShowMeditationGuide(false)

    const message = `Mood logged: Feeling ${mood.label}! Take a moment for yourself.`
    setCheckInMessage({ mood: mood.label, message, timestamp: new Date() })

    console.log(`[WELLBEING CHECK-IN] User ${user?.first_name || 'Guest'} checked in as: ${mood.label}`);

    // Auto-clear notification after 5 seconds
    setTimeout(() => {
      setCheckInMessage(null)
    }, 5000)
  }

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = { role: 'user', content: chatInput };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setIsChatLoading(true);

    try {
      // Using HuggingFace Inference API (free tier, no signup needed)
      const response = await fetch(
        'https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            inputs: chatInput,
            parameters: {
              max_length: 150,
              temperature: 0.8,
              top_p: 0.9
            }
          })
        }
      );

      const data = await response.json();
      
      let botReply = "I'm here to listen and support you. How can I help you today?";
      
      if (data && data[0] && data[0].generated_text) {
        botReply = data[0].generated_text;
      } else if (data && data.error) {
        // Fallback responses if API is loading or rate limited
        const supportiveResponses = [
          "I understand. Take your time to share what's on your mind.",
          "That sounds challenging. I'm here to help you through this.",
          "Thank you for sharing. How are you feeling about this situation?",
          "I'm listening. Would you like to tell me more about what's on your mind?",
          "It's okay to feel this way. What would help you feel better right now?",
          "I hear you. Sometimes just talking about things can help. What else is bothering you?",
          "That's completely valid. How long have you been feeling this way?"
        ];
        botReply = supportiveResponses[Math.floor(Math.random() * supportiveResponses.length)];
      }

      setChatMessages(prev => [...prev, { role: 'assistant', content: botReply }]);
    } catch (error) {
      console.error('Chat error:', error);
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "I'm here to support you. Please tell me more about what's on your mind." 
      }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleResourceAction = (resource) => {
    setCheckInMessage(null);

    if (resource.type === 'Audio Guide') {
      setShowMeditationGuide(true);
      console.log(`[ACTION] Opening meditation guide for: ${resource.title}`);
    } else if (resource.type === 'Support Chat') {
      setShowMeditationGuide(false);
      setShowChatModal(true);
      setChatMessages([
        { role: 'assistant', content: 'Hello! I\'m your School Support Advisor. I\'m here to listen and help. How are you feeling today?' }
      ]);
      console.log(`[ACTION] Initiating chat for: ${resource.title}`);
    } else if (resource.action === 'document') {
        setShowMeditationGuide(false);
        console.log(`[NAVIGATION] Opening resource page for: ${resource.title}`);
        setModalConfig({
            title: "Parent/Guardian Guide to School Stress",
            message: (
                <div className="text-left text-sm text-slate-600 space-y-2">
                    <p>This guide provides valuable insights and practical tips to help you understand and support your child's emotional wellbeing during their school years.</p>
                    <ul className="list-disc list-inside space-y-1">
                        <li><strong>Understanding Stress:</strong> Learn to recognize the signs of stress in your child.</li>
                        <li><strong>Effective Communication:</strong> Discover techniques for open and supportive conversations.</li>
                        <li><strong>Coping Strategies:</strong> Find healthy coping mechanisms for both you and your child.</li>
                        <li><strong>School Resources:</strong> Information on how to collaborate with the school for support.</li>
                    </ul>
                    <p className="font-semibold pt-2">Would you like to open the full document now?</p>
                </div>
            ),
            onConfirm: () => {
                setModalConfig(null);
                console.log('Resource opened');
                window.open('https://parenting-ed.org/wp-content/themes/parenting-ed/files/handouts/stress_management.pdf', '_blank');
            },
            onCancel: () => setModalConfig(null),
            confirmText: 'Open Document',
            cancelText: 'Cancel'
        });
    } else {
      setShowMeditationGuide(false);
      console.log(`[NAVIGATION] Opening resource page for: ${resource.title}`);
      setModalConfig({
        message: `Opening the full document/resource page for: ${resource.title}`,
        onConfirm: () => {
          setModalConfig(null);
          console.log('Resource opened');
        },
        onCancel: () => setModalConfig(null),
        confirmText: 'OK'
      });
    }
  };

  const renderMeditationGuide = () => (
    <Card className="mb-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-slate-900 flex items-center">
            <Youtube className="w-6 h-6 mr-2 text-red-600" />
            Mindful Minute Audio
          </h2>
          <button
            onClick={() => setShowMeditationGuide(false)}
            className="p-2 rounded-lg hover:bg-white/50 transition-colors"
          >
            <X className="w-5 h-5 text-slate-600" />
          </button>
        </div>
        
        {/* Real YouTube Embed */}
        <div className="relative pt-[56.25%] mb-4 rounded-xl overflow-hidden shadow-lg">
          <iframe
            className="absolute inset-0 w-full h-full"
            src="https://www.youtube.com/embed/inpok4MKVLM"
            title="5 Minute Guided Meditation"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
        </div>
        
        <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4">
          <p className="text-sm text-slate-700 leading-relaxed">
            <span className="font-semibold">Meditation Guide:</span> Find a comfortable position, either sitting or lying down. Close your eyes gently. Take a deep breath in through your nose, filling your belly like a balloon. Hold it for a moment... and slowly exhale through your mouth, letting all the tension melt away. Focus only on the sound of your breath. If your mind wanders, gently bring your focus back to the breath. You are safe, you are calm.
          </p>
        </div>
      </div>
    </Card>
  )

  if (loading) {
    return (
      <DashboardLayout role={user?.role || 'STUDENT'}>
        <LoadingSpinner size="xl" text="Loading wellbeing hub..." />
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout role={user?.role || 'STUDENT'}>
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl p-6 md:p-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-pink-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl" />
          
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-2">
              <Heart className="w-8 h-8 text-pink-400" />
              <h1 className="text-3xl md:text-4xl font-bold text-white">Wellbeing Hub</h1>
            </div>
            <p className="text-slate-300 text-lg">
              Your safe space for emotional check-ins and support resources.
            </p>
          </div>
        </div>
        
        {/* In-Page Check-In Notification */}
        {checkInMessage && (
          <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center justify-between animate-fade-in">
            <div>
              <p className="font-semibold text-slate-900">
                Check-In Successful: <span className="text-green-700">{checkInMessage.mood}</span>
              </p>
              <p className="text-sm text-slate-600 mt-1">{checkInMessage.message}</p>
            </div>
            <button
              onClick={() => setCheckInMessage(null)}
              className="p-2 rounded-lg hover:bg-green-100 transition-colors"
            >
              <X className="w-5 h-5 text-slate-600" />
            </button>
          </div>
        )}

        {/* Mood Check-In Section */}
        <Card title="How are you feeling right now?" subtitle="Track your emotional wellbeing">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            {DUMMY_WELLBEING_DATA.emotions.map((mood) => {
              const Icon = mood.icon
              const isSelected = selectedMood && selectedMood.id === mood.id
              return (
                <button
                  key={mood.id}
                  onClick={() => handleCheckIn(mood)}
                  className={`p-6 rounded-xl flex flex-col items-center justify-center transition-all border-2 ${mood.bgColor} ${
                    isSelected ? 'border-slate-900 scale-[1.02] shadow-lg' : 'border-slate-200 hover:border-slate-300 hover:shadow-md'
                  }`}
                >
                  <Icon className={`w-10 h-10 mb-2 ${mood.color}`} />
                  <span className="font-semibold text-slate-700">{mood.label}</span>
                </button>
              )
            })}
          </div>
          {selectedMood && (
            <p className="mt-4 text-sm text-center text-slate-600">
              You last checked in as <span className="font-semibold">{selectedMood.label}</span>.
            </p>
          )}
        </Card>

        {/* Conditional Meditation Guide */}
        {showMeditationGuide && renderMeditationGuide()}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Support Resources */}
          <div className="lg:col-span-2">
            <Card title="Support Resources" subtitle="Tools and guidance for your wellbeing">
              <div className="space-y-4 mt-4">
                {DUMMY_WELLBEING_DATA.resources.map((resource, index) => {
                  const Icon = resource.icon
                  return (
                    <div key={index} className="p-4 bg-slate-50 rounded-xl flex items-start space-x-4 hover:bg-slate-100 transition-colors border border-slate-200">
                      <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shrink-0 shadow-sm">
                        <Icon className="w-6 h-6 text-slate-700" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-slate-900">{resource.title}</h3>
                        <p className="text-sm text-slate-600 mb-3">{resource.description}</p>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleResourceAction(resource)} 
                        >
                          {resource.type === 'Support Chat' ? 'Start Chat' : 'Access Resource'}
                        </Button>
                        {resource.type === 'Audio Guide' && (
                          <p className="text-xs text-slate-500 mt-2">
                            Source: YouTube (Embedded Player)
                          </p>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <Card title="Your Check-In History" subtitle="Recent mood logs">
              <div className="space-y-3 mt-4">
                {DUMMY_WELLBEING_DATA.checkInHistory.map((item, index) => (
                  <div key={index} className="border-b border-slate-200 pb-3 last:border-b-0 last:pb-0">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-semibold text-slate-900">{item.mood}</span>
                      <span className="text-xs text-slate-500">{item.date}</span>
                    </div>
                    <p className="text-sm text-slate-600 italic">"{item.note}"</p>
                  </div>
                ))}
                {DUMMY_WELLBEING_DATA.checkInHistory.length === 0 && (
                  <p className="text-sm text-slate-500 text-center py-4">No recent check-ins recorded.</p>
                )}
              </div>
            </Card>
            
            <Card className="bg-red-50 border-red-200">
              <div className="p-5">
                <h3 className="text-lg font-bold text-slate-900 mb-2 flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-red-600" />
                  Need Immediate Help?
                </h3>
                <p className="text-sm text-slate-700 mb-4">
                  If this is an emergency, please use your local emergency number.
                </p>
                <div className="bg-white rounded-lg p-3 border border-red-200">
                  <p className="text-sm font-semibold text-slate-900">
                    School Hotline: <span className="text-red-700">(555) 123-4567</span>
                  </p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {modalConfig && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl p-6 w-[90%] max-w-md border border-slate-200">
            {modalConfig.title && (
                <h2 className="text-xl font-bold text-slate-900 mb-4">{modalConfig.title}</h2>
            )}
            <div className="text-slate-900 mb-4">
                {modalConfig.message}
            </div>
            <div className="flex justify-end gap-3">
              {modalConfig.onCancel && (
                <button
                  onClick={modalConfig.onCancel}
                  className="px-6 py-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-900 font-medium transition-colors"
                >
                  {modalConfig.cancelText || 'Cancel'}
                </button>
              )}
              <button
                onClick={modalConfig.onConfirm}
                className="px-6 py-2 rounded-full bg-slate-900 hover:bg-slate-800 text-white font-medium transition-colors"
              >
                {modalConfig.confirmText || 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Chat Modal */}
      {showChatModal && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl w-[90%] max-w-2xl h-[600px] flex flex-col border border-slate-200">
            {/* Chat Header */}
            <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">School Support Advisor</h3>
                  <p className="text-xs text-slate-600">Here to listen and help</p>
                </div>
              </div>
              <button
                onClick={() => setShowChatModal(false)}
                className="p-2 rounded-lg hover:bg-white/50 transition-colors"
              >
                <X className="w-5 h-5 text-slate-600" />
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatMessages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[75%] rounded-2xl px-4 py-2.5 ${
                      msg.role === 'user'
                        ? 'bg-slate-900 text-white'
                        : 'bg-slate-100 text-slate-900'
                    }`}
                  >
                    <p className="text-sm leading-relaxed">{msg.content}</p>
                  </div>
                </div>
              ))}
              {isChatLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-100 rounded-2xl px-4 py-2.5">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Chat Input */}
            <div className="p-4 border-t border-slate-200 bg-slate-50">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                  placeholder="Type your message..."
                  className="flex-1 px-4 py-2.5 border border-slate-300 rounded-full focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent text-sm"
                  disabled={isChatLoading}
                />
                <button
                  onClick={sendChatMessage}
                  disabled={!chatInput.trim() || isChatLoading}
                  className="px-6 py-2.5 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-full font-medium transition-colors text-sm flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  Send
                </button>
              </div>
              <p className="text-xs text-slate-500 mt-2 text-center">
                This is a supportive AI assistant. For emergencies, call (555) 123-4567
              </p>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  )
}

export default Wellbeing