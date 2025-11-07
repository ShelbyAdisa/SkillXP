import React, { useEffect, useState } from 'react'
import DashboardLayout from '../components/layout/DashboardLayout'
import { useAuth } from '../context/AuthContext'
import Card from '../components/shared/Card'
import Button from '../components/shared/Button'
import Badge from '../components/shared/Badge'
import LoadingSpinner from '../components/shared/LoadingSpinner'
// import { elibraryApi } from '../services/dashboardApi' // Keeping the API import for future use
import { BookOpen } from 'lucide-react'

// Reusable Notification Modal Component (Simulated ConfirmModal - for ELibrary actions)
const NotificationModal = ({ title, message, variant, onConfirm, onClose }) => {
    let colorClass = 'border-slate-500';
    let titleColor = 'text-slate-900';
    let buttonColor = 'slate';
    if (variant === 'success') {
      colorClass = 'border-green-500';
      titleColor = 'text-green-700';
      buttonColor = 'success';
    } else if (variant === 'confirm') {
      colorClass = 'border-blue-500';
      titleColor = 'text-blue-700';
      buttonColor = 'primary';
    }

    return (
      <div className="fixed inset-0 bg-gray-900 bg-opacity-50 z-[60] flex items-center justify-center p-4 sm:p-8">
        <Card className={`max-w-md w-full p-6 border-t-4 ${colorClass} shadow-xl transform transition-all`}>
          <div className="flex justify-between items-start">
            <h3 className={`text-xl font-bold ${titleColor}`}>{title}</h3>
            <button onClick={onClose} className="text-slate-500 hover:text-slate-700 text-2xl ml-4">
              &times;
            </button>
          </div>
          <p className="mt-4 text-slate-700 whitespace-pre-wrap">{message}</p>
          <div className="mt-6 flex justify-end space-x-3">
            {variant === 'confirm' && (
              <Button size="sm" variant="outline" color="slate" onClick={onClose}>
                Cancel
              </Button>
            )}
            <Button 
              size="sm" 
              variant="primary" 
              color={buttonColor} 
              onClick={variant === 'confirm' ? onConfirm : onClose}
            >
              {variant === 'confirm' ? 'Confirm Open' : 'Close'}
            </Button>
          </div>
        </Card>
      </div>
    );
};

// --- DUMMY DATA START ---
const DUMMY_RESOURCES = [
  {
    id: 'b1',
    title: 'Adventures in Number Land: Addition Basics',
    description: 'An introductory book focused on single-digit addition and basic counting techniques.',
    preview_content: 'This book uses charming characters and simple scenarios (counting apples, stacking blocks) to teach the concept of adding numbers from 1 to 10. Includes practice pages and a cheerful narrative.',
    full_content: 'FULL BOOK CONTENT: Chapter 1: Counting apples (1+1=2). Chapter 2: The Block Tower Challenge (2+3=5). Chapter 3: The Big Race (Final Quiz). Enjoy this fully immersive digital book designed for Grade 1 Math students.',
    resource_type: 'Book',
    category: 'Mathematics',
  },
  {
    id: 'b2',
    title: 'The Phonics Factory: Mastering CVC Words',
    description: 'A comprehensive guide to blending consonant-vowel-consonant (CVC) words for reading fluency.',
    preview_content: 'Focuses on short vowel sounds in CVC word families like -at, -en, and -ip. Features colorful pages with large, easy-to-read text and exercises for young readers (Ages 5-7).',
    full_content: 'FULL BOOK CONTENT: Lesson 1: The short "a" sound (cat, mat, sat). Lesson 2: The short "e" sound (bed, red, pet). Lesson 3: Blending practice and comprehension checks. This is a core resource for Grade 1 English Literacy.',
    resource_type: 'Book',
    category: 'English',
  },
  {
    id: 'b3',
    title: 'Junior Scientist Handbook: Magnets',
    description: 'A hands-on guide exploring magnetism through safe, simple home experiments.',
    preview_content: 'Discover what materials are magnetic and how magnets interact. Each experiment is clearly laid out with simple instructions and materials commonly found at home or school.',
    full_content: 'FULL BOOK CONTENT: Experiment 1: The Floating Paperclip. Experiment 2: Making a Compass. Summary: The science of poles and attraction. This book is suitable for Grade 2 Science classes.',
    resource_type: 'Book',
    category: 'Science',
  },
  {
    id: 'b4',
    title: 'Drawing Animals: Beginner Shapes',
    description: 'Teaches children to draw animals using only basic shapes (circles, squares, triangles).',
    preview_content: 'A fun artistic resource that breaks down complex animal forms into easy-to-draw geometric shapes, encouraging motor skills and creativity.',
    full_content: 'FULL BOOK CONTENT: Step-by-step guides for drawing a cat, a dog, a bird, and a fish. Includes tips on shading and coloring techniques. Designed for Primary School Art classes.',
    resource_type: 'Book',
    category: 'Art',
  },
  {
    id: 'b5',
    title: 'My Community and Me: Citizenship',
    description: 'An introduction to civic duties, community roles, and being a good citizen.',
    preview_content: 'Covers topics like community helpers (police, fire, doctors), basic rules and laws, and the importance of helping others in the neighborhood.',
    full_content: 'FULL BOOK CONTENT: Section 1: Who helps us? Section 2: School Rules and Home Rules. Section 3: Voting (Simplified Concept). Core content for Grade 2 Social Studies.',
    resource_type: 'Book',
    category: 'Social Studies',
  },
];

const CATEGORIES = ['Mathematics', 'English', 'Science', 'Art', 'Social Studies'];
const RESOURCE_TYPES = ['Book', 'Interactive Guide', 'Worksheet Pack']; // Simplified resource types
// --- DUMMY DATA END ---


const ELibrary = () => {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [resources, setResources] = useState([]) // Stores all base resources
  const [q, setQ] = useState('')
  const [activeTab, setActiveTab] = useState('all') // Changed default tab to 'all' for simplicity

  // Filter States
  const [activeCategory, setActiveCategory] = useState(null)
  const [activeResourceType, setActiveResourceType] = useState(null)
  
  // Modal States
  const [previewModal, setPreviewModal] = useState(null); // For book preview text
  const [confirmOpenModal, setConfirmOpenModal] = useState(null); // For opening confirmation
  const [fullBookContent, setFullBookContent] = useState(null); // For displaying book content

  useEffect(() => {
    const loadDummyData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        await new Promise(resolve => setTimeout(resolve, 500))

        setResources(DUMMY_RESOURCES)

      } catch (e) {
        console.error('Error loading library:', e)
        //setError(e.response?.data?.message || 'Failed to load library')
      } finally {
        setLoading(false)
      }
    }
    loadDummyData()
  }, [])

  const onSearch = (e) => {
    e.preventDefault()
    // Logic is handled by getFilteredResources based on 'q'
    // Ensure filters are reset or included in search logic if needed, but for now, search filters the existing view.
    setFullBookContent(null);
  }
  
  const handlePreview = (resource) => {
    setConfirmOpenModal(null); // Close other modals
    setFullBookContent(null);
    setPreviewModal({
        title: `Preview: ${resource.title}`,
        message: resource.preview_content,
        resource,
    });
  }

  const handleOpenRequest = (resource) => {
    setPreviewModal(null); // Close other modals
    setFullBookContent(null);
    setConfirmOpenModal({
        title: `Open Digital Book`,
        message: `Are you sure you want to open "${resource.title}"? This will load the full digital resource.`,
        resource,
    });
  }

  const handleOpenConfirm = (resource) => {
    setConfirmOpenModal(null); // Close confirmation modal
    
    // Simulate opening the full book
    console.log(`[ACTION] Opening Full Book: ${resource.title}`);
    setFullBookContent(resource);
  }

  // Handle resource actions for sidebar filters
  const handleFilterClick = (type, value) => {
    setFullBookContent(null);
    if (type === 'category') {
      setActiveCategory(activeCategory === value ? null : value);
    } else if (type === 'resource_type') {
      setActiveResourceType(activeResourceType === value ? null : value);
    }
  }


  const getFilteredResources = () => {
    const lowerQ = q.toLowerCase().trim()
    
    return resources.filter(resource => {
      const searchMatch = !lowerQ || 
        resource.title.toLowerCase().includes(lowerQ) || 
        resource.description.toLowerCase().includes(lowerQ)

      const categoryMatch = !activeCategory || resource.category === activeCategory
      const typeMatch = !activeResourceType || resource.resource_type === activeResourceType
      
      return searchMatch && categoryMatch && typeMatch
    })
  }

  const renderResourceCard = (resource) => (
    <Card key={resource.id} className="hover:shadow-lg transition-shadow">
      <div className="p-6">
        <div className="flex items-start gap-4">
          {/* Resource icon/thumbnail - Fixed Book icon */}
          <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center shrink-0">
            <BookOpen className="w-6 h-6 text-slate-600" />
          </div>

          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">{resource.title}</h3>
            <p className="text-sm text-slate-600 mb-3 line-clamp-2">
              {resource.description || 'No description available'}
            </p>

            <div className="flex items-center gap-2">
              {resource.resource_type && (
                <Badge variant="slate">{resource.resource_type}</Badge>
              )}
              {resource.category && (
                <Badge variant="outline">{resource.category}</Badge>
              )}
            </div>

            <div className="flex items-center justify-end mt-4">
              <div className="flex gap-2">
                <Button 
                  size="sm" 
                  variant="outline" 
                  color="slate"
                  onClick={() => handlePreview(resource)}
                >
                  Preview
                </Button>
                <Button 
                  size="sm" 
                  variant="primary" 
                  color="slate"
                  onClick={() => handleOpenRequest(resource)}
                >
                  Open
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
  
  // Renders the full book content (modal)
  const renderFullBookView = () => {
    if (!fullBookContent) return null;

    return (
      <div className="fixed inset-0 bg-gray-900 bg-opacity-90 z-50 overflow-y-auto p-4 sm:p-8">
        <Card className="max-w-4xl mx-auto my-4 p-8">
          <div className="flex justify-between items-start mb-6 border-b pb-4">
            <div>
              <h2 className="text-3xl font-bold text-slate-900">📖 {fullBookContent.title}</h2>
              <p className="text-md text-slate-600 mt-1">Full Digital Edition</p>
            </div>
            <Button variant="outline" color="slate" onClick={() => setFullBookContent(null)}>
              Close Book
            </Button>
          </div>

          <div className="h-[60vh] overflow-y-auto p-4 border border-slate-200 rounded-lg bg-white shadow-inner">
            <h3 className="text-xl font-semibold text-slate-800 mb-4">Book Content:</h3>
            <p className="text-slate-700 whitespace-pre-wrap">{fullBookContent.full_content}</p>
            <p className="mt-8 text-sm text-slate-500 italic">
                -- End of Simulated Content --
            </p>
          </div>
        </Card>
      </div>
    );
  };


  const resourcesToDisplay = getFilteredResources()
  const displayTitle = (activeCategory || activeResourceType) 
    ? (activeCategory || activeResourceType) + ' Resources'
    : 'All Resources'

  if (loading) {
    return (
      <DashboardLayout role={user?.role}>
        <div className="flex items-center justify-center min-h-[60vh]">
          <LoadingSpinner text="Loading library..." />
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout role={user?.role}>
      
      {/* Modals */}
      {previewModal && (
        <NotificationModal 
          title={previewModal.title}
          message={previewModal.message}
          variant="default"
          onClose={() => setPreviewModal(null)}
        />
      )}
      {confirmOpenModal && (
        <NotificationModal 
          title={confirmOpenModal.title}
          message={confirmOpenModal.message}
          variant="confirm"
          onConfirm={() => handleOpenConfirm(confirmOpenModal.resource)}
          onClose={() => setConfirmOpenModal(null)}
        />
      )}

      {/* Full Book View */}
      {fullBookContent && renderFullBookView()}


      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">eLibrary</h1>
          <p className="text-slate-600">
            A curated collection of digital books and learning resources.
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <form onSubmit={onSearch} className="relative">
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-4 py-3 pr-12 text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-transparent"
              placeholder="Search for book titles and subjects..."
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-slate-600 hover:text-slate-900"
            >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            </button>
          </form>
        </div>

        {/* Main Content Grid with Sidebar */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Sidebar for filtering - Column 1 */}
          <div className="lg:col-span-1">

            {/* Category Filter */}
            <Card className="p-4 mb-8">
              <h2 className="text-lg font-bold text-slate-900 mb-4 px-2">
                Subject Categories
              </h2>
              <div className="space-y-1">
                {CATEGORIES.map(category => (
                  <button 
                    key={category}
                    onClick={() => handleFilterClick('category', category)}
                    className={`w-full text-left px-4 py-2 rounded-lg transition-colors flex justify-between items-center ${
                      activeCategory === category
                        ? 'bg-slate-200 text-slate-900 font-semibold'
                        : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    {category}
                    {activeCategory === category && (
                      <svg className="w-4 h-4 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </button>
                ))}
              </div>
            </Card>
            
            {/* Resource Type Filter */}
            <Card className="p-4">
              <h2 className="text-lg font-bold text-slate-900 mb-4 px-2">
                Resource Types
              </h2>
              <div className="space-y-1">
                {RESOURCE_TYPES.map(type => (
                  <button 
                    key={type}
                    onClick={() => handleFilterClick('resource_type', type)}
                    className={`w-full text-left px-4 py-2 rounded-lg transition-colors flex justify-between items-center ${
                      activeResourceType === type
                        ? 'bg-slate-200 text-slate-900 font-semibold'
                        : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    {type}
                    {activeResourceType === type && (
                      <svg className="w-4 h-4 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </button>
                ))}
              </div>
            </Card>
          </div>

          {/* Main Resource List - Columns 2-4 */}
          <div className="lg:col-span-3">
            <h2 className="text-2xl font-bold text-slate-900 mb-6 capitalize">
              {displayTitle}
            </h2>
            
            {resourcesToDisplay.length > 0 ? (
              <div className="space-y-4">
                {resourcesToDisplay.map(renderResourceCard)}
              </div>
            ) : (
              // Empty State for filtered/searched results
              <Card>
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <BookOpen className="w-8 h-8 text-slate-400" />
                  </div>
                  <h3 className="text-lg font-medium text-slate-900 mb-2">No Books Found</h3>
                  <p className="text-slate-600">
                    Try clearing your current filters or searching again.
                  </p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}

export default ELibrary