import { useState } from 'react';
import { Award, MessageCircle, Heart, Send, Image, Trash2, X } from 'lucide-react';
import ConfirmModal from '../components/ConfirmModal'; // ✅ import this
import DashboardLayout from '../components/layout/DashboardLayout';

export default function Forums() {
  const [posts, setPosts] = useState([
    { id: 1, author: 'Anonymous Student', content: 'Can anyone explain how photosynthesis works? I have a test tomorrow!', likes: 5, comments: [], timestamp: '2h ago', image: null, isOwn: false },
    { id: 2, author: 'Anonymous Student', content: 'Need help with algebra homework - quadratic equations are confusing', likes: 8, comments: [], timestamp: '4h ago', image: null, isOwn: false },
  ]);
  const [newPost, setNewPost] = useState('');
  const [newImage, setNewImage] = useState(null);
  const [userPoints, setUserPoints] = useState(120);
  const [activeCommentPost, setActiveCommentPost] = useState(null);
  const [commentText, setCommentText] = useState('');
  const [likedPosts, setLikedPosts] = useState(new Set());
  const [confirmData, setConfirmData] = useState(null); // ✅ new state

  const handlePost = () => {
    if (newPost.trim()) {
      setPosts([{
        id: posts.length + 1,
        author: 'You (Anonymous)',
        content: newPost,
        likes: 0,
        comments: [],
        timestamp: 'Just now',
        image: newImage,
        isOwn: true
      }, ...posts]);
      setNewPost('');
      setNewImage(null);
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setNewImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleLike = (postId) => {
    if (!likedPosts.has(postId)) {
      setPosts(posts.map(post => 
        post.id === postId ? { ...post, likes: post.likes + 1 } : post
      ));
      setLikedPosts(new Set([...likedPosts, postId]));
      setUserPoints(userPoints + 5);
    }
  };

  const handleComment = (postId) => {
    if (commentText.trim()) {
      setPosts(posts.map(post => 
        post.id === postId 
          ? { 
              ...post, 
              comments: [...post.comments, {
                id: Date.now(),
                author: 'You (Anonymous)',
                content: commentText,
                timestamp: 'Just now'
              }]
            } 
          : post
      ));
      setUserPoints(userPoints + 10);
      setCommentText('');
      setActiveCommentPost(null);
    }
  };

  // ✅ Updated delete handlers
  const handleDeletePost = (postId) => {
    setConfirmData({
      message: 'Are you sure you want to delete this post?',
      onConfirm: () => {
        setPosts(posts.filter(post => post.id !== postId));
        setConfirmData(null);
      },
    });
  };

  const handleDeleteComment = (postId, commentId) => {
    setConfirmData({
      message: 'Are you sure you want to delete this comment?',
      onConfirm: () => {
        setPosts(posts.map(post => 
          post.id === postId 
            ? { ...post, comments: post.comments.filter(c => c.id !== commentId) }
            : post
        ));
        setConfirmData(null);
      },
    });
  };

  return (
    <DashboardLayout user="STUDENT">
    <div className="max-w-4xl mx-auto px-4 py-6">
      {/* Points Display */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Community Forums</h1>
          <p className="text-slate-600 mt-1">Ask questions and help your peers anonymously</p>
        </div>
        <div className="flex items-center gap-2 bg-slate-900 text-white px-5 py-3 rounded-full">
          <Award className="w-5 h-5" />
          <span className="font-semibold">{userPoints} pts</span>
        </div>
      </div>

      {/* Create Post */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-4">
        <textarea
          value={newPost}
          onChange={(e) => setNewPost(e.target.value)}
          placeholder="Ask a question or share homework tips... (posted anonymously)"
          className="w-full p-3 border border-slate-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-slate-900"
          rows="3"
        />
        
        {newImage && (
          <div className="relative mt-3">
            <img src={newImage} alt="Upload preview" className="w-full max-h-64 object-cover rounded-lg" />
            <button
              onClick={() => setNewImage(null)}
              className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        <div className="flex justify-between items-center mt-3">
          <div className="flex items-center gap-2">
            <label className="cursor-pointer text-slate-600 hover:text-slate-900 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
              <Image className="w-5 h-5" />
            </label>
            <p className="text-sm text-slate-500">Posted as Anonymous Student</p>
          </div>
          <button
            onClick={handlePost}
            disabled={!newPost.trim()}
            className="bg-slate-900 text-white px-6 py-2 rounded-full font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Post
          </button>
        </div>
      </div>

      {/* Info Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <p className="text-sm text-blue-900">
          💡 <strong>Earn points:</strong> Comment to help others (+10 pts) • Like helpful posts (+5 pts)
        </p>
      </div>

      {/* Posts Feed */}
      <div className="space-y-4">
        {posts.map((post) => (
          <div key={post.id} className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0">
                <span className="text-slate-600 font-semibold">?</span>
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-slate-900">{post.author}</span>
                    <span className="text-slate-500 text-sm">• {post.timestamp}</span>
                  </div>
                  {post.isOwn && (
                    <button
                      onClick={() => handleDeletePost(post.id)}
                      className="text-red-500 hover:text-red-600 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
                <p className="text-slate-700 mb-3">{post.content}</p>
                
                {post.image && (
                  <img src={post.image} alt="Post content" className="w-full max-h-96 object-cover rounded-lg mb-3" />
                )}

                <div className="flex items-center gap-4 mb-3">
                  <button
                    onClick={() => handleLike(post.id)}
                    className={`flex items-center gap-2 transition-colors ${
                      likedPosts.has(post.id) 
                        ? 'text-red-500' 
                        : 'text-slate-600 hover:text-red-500'
                    }`}
                  >
                    <Heart className={`w-5 h-5 ${likedPosts.has(post.id) ? 'fill-current' : ''}`} />
                    <span className="text-sm font-medium">{post.likes}</span>
                  </button>
                  <button
                    onClick={() => setActiveCommentPost(activeCommentPost === post.id ? null : post.id)}
                    className="flex items-center gap-2 text-slate-600 hover:text-blue-500 transition-colors"
                  >
                    <MessageCircle className="w-5 h-5" />
                    <span className="text-sm font-medium">{post.comments.length}</span>
                  </button>
                </div>

                {/* Comments Section */}
                {post.comments.length > 0 && (
                  <div className="mt-4 space-y-3 pl-4 border-l-2 border-slate-200">
                    {post.comments.map((comment) => (
                      <div key={comment.id} className="bg-slate-50 rounded-lg p-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-medium text-sm text-slate-900">{comment.author}</span>
                              <span className="text-slate-500 text-xs">• {comment.timestamp}</span>
                            </div>
                            <p className="text-slate-700 text-sm">{comment.content}</p>
                          </div>
                          {comment.author.includes('You') && (
                            <button
                              onClick={() => handleDeleteComment(post.id, comment.id)}
                              className="text-red-500 hover:text-red-600 transition-colors ml-2"
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Comment Input */}
                {activeCommentPost === post.id && (
                  <div className="mt-4 flex gap-2">
                    <input
                      type="text"
                      value={commentText}
                      onChange={(e) => setCommentText(e.target.value)}
                      placeholder="Write a helpful comment..."
                      className="flex-1 p-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                      onKeyPress={(e) => e.key === 'Enter' && handleComment(post.id)}
                    />
                    <button
                      onClick={() => handleComment(post.id)}
                      disabled={!commentText.trim()}
                      className="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Send
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
  {confirmData && (
        <ConfirmModal
          message={confirmData.message}
          onConfirm={confirmData.onConfirm}
          onCancel={() => setConfirmData(null)}
        />
      )}
      
    </div>
    </DashboardLayout>
  )
}