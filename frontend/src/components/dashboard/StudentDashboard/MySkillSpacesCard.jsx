import React from 'react';
import Card from '../../shared/Card';
import { Link } from 'react-router-dom';
import { useMySkillSpaces } from '../../../hooks/useMySkillSpaces';
import Button from '../../shared/Button';

const MySkillSpacesCard = () => {
  // No user needed, hook provides all dummy data
  const { skillspaces } = useMySkillSpaces(); 

  return (
    <Card title="My SkillSpaces">
      <ul className="space-y-3">
        {skillspaces.map((space) => (
          <li key={space.id} className="flex items-center space-x-2">
            <span className="text-sm font-semibold text-gray-500">{space.name.split('/')[0]}</span>
            <Link 
              to={`/s/${space.slug}`} 
              className="font-medium text-gray-800 hover:underline"
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