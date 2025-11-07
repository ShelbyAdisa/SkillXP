import React, { useState } from "react";
import Header from "./Header";
import Hero from "./Hero";
import XPBar from "./XPBar";
import CourseCard from "./CourseCard";
import Leaderboard from "./Leaderboard";

export default function LearningHub() {
  const [showLeaderboard, setShowLeaderboard] = useState(true);

  const [userData] = useState({
    name: "Alex Chen",
    currentXP: 2450,
    nextLevelXP: 3000,
    level: 12,
  });

  const [courses] = useState([
    {
      id: 1,
      name: "Advanced Mathematics",
      instructor: "Dr. Sarah Johnson",
      thumbnail: "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&h=200&fit=crop",
      xp: 340,
      dueDate: "Oct 12",
      progress: 68,
      accentColor: "#2563EB"
    },
    {
      id: 2,
      name: "Web Development",
      instructor: "Prof. Michael Park",
      thumbnail: "https://images.unsplash.com/photo-1593720213428-28a5b9e94613?w=400&h=200&fit=crop",
      xp: 520,
      dueDate: "Oct 10",
      progress: 82,
      accentColor: "#7C3AED"
    },
    {
      id: 3,
      name: "Data Structures",
      instructor: "Dr. Emily Rodriguez",
      thumbnail: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=200&fit=crop",
      xp: 180,
      dueDate: "Oct 15",
      progress: 45,
      accentColor: "#059669"
    },
    {
      id: 4,
      name: "Digital Marketing",
      instructor: "Lisa Anderson",
      thumbnail: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=200&fit=crop",
      xp: 620,
      dueDate: "Oct 9",
      progress: 91,
      accentColor: "#EA580C"
    },
    {
      id: 5,
      name: "Machine Learning",
      instructor: "Dr. James Wilson",
      thumbnail: "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=400&h=200&fit=crop",
      xp: 290,
      dueDate: "Oct 14",
      progress: 34,
      accentColor: "#DC2626"
    },
    {
      id: 6,
      name: "UX Design Principles",
      instructor: "Nina Patel",
      thumbnail: "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop",
      xp: 450,
      dueDate: "Oct 11",
      progress: 76,
      accentColor: "#DB2777"
    }
  ]);

  const [leaderboard] = useState([
    { rank: 1, name: "Jordan Lee", xp: 4250, avatar: "JL" },
    { rank: 2, name: "Sam Rivera", xp: 3890, avatar: "SR" },
    { rank: 3, name: "Alex Chen", xp: 2450, avatar: "AC", isCurrentUser: true },
    { rank: 4, name: "Morgan Taylor", xp: 2310, avatar: "MT" },
    { rank: 5, name: "Casey Kim", xp: 2180, avatar: "CK" },
    { rank: 6, name: "Riley Brooks", xp: 1950, avatar: "RB" },
    { rank: 7, name: "Dakota Smith", xp: 1820, avatar: "DS" },
    { rank: 8, name: "Avery Chen", xp: 1675, avatar: "AC" }
  ]);

  return (
    <div className="min-h-screen bg-slate-50">
      <Header
        userName={userData.name}
        showLeaderboard={showLeaderboard}
        setShowLeaderboard={setShowLeaderboard}
      />

      <div className="max-w-[1400px] mx-auto px-8 py-8">
        {/* Hero Section */}
        <Hero 
          userName={userData.name}
          streak={7}
          coursesInProgress={courses.length}
        />

        <XPBar
          level={userData.level}
          currentXP={userData.currentXP}
          nextLevelXP={userData.nextLevelXP}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      </div>

      <Leaderboard
        leaderboard={leaderboard}
        showLeaderboard={showLeaderboard}
        setShowLeaderboard={setShowLeaderboard}
      />
    </div>
  );
}