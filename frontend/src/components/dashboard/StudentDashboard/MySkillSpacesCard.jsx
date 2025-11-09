import React from 'react';
import Card from '../../shared/Card';
import { Link } from 'react-router-dom';
import { useMySkillSpaces } from '../../../hooks/useMySkillSpaces';
import Button from '../../shared/Button';
import { Book } from 'lucide-react'; // 1. Import an icon

const MySkillSpacesCard = () => {
  // No user needed, hook provides all dummy data
  const { skillspaces } = useMySkillSpaces(); 

  return (
    <Card title="My SkillSpaces">
      <ul className="space-y-3">
        {skillspaces.map((space) => (
          <li key={space.id} className="flex items-center space-x-2">
            {/* 2. Add the icon here */}
            <Book className="w-4 h-4 text-[#82959B] shrink-0" />
            
            {/* 3. Update text colors for dark theme */}
            <span className="text-sm font-semibold text-[#82959B]">{space.name.split('/')[0]}</span>
            <Link 
              to={`/s/${space.slug}`} 
              className="font-medium text-[#D7DADC] hover:underline"
            >
              {space.slug}
            </Link>
          </li>
        ))}
      </ul>
      <Button variant="outline" className="w-full mt-4">Browse All</Button>
    </Card>
  );
};

export default MySkillSpacesCard;