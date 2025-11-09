import React from 'react';
import { Mail, Phone, Home, Hash } from 'lucide-react';

function DetailItem({ icon, label, value }) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex-shrink-0 pt-1">
        {React.createElement(icon, { className: "h-5 w-5 text-gray-400" })}
      </div>
      <div>
        <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">{label}</dt>
        <dd className="mt-1 text-sm text-gray-900 dark:text-white">{value}</dd>
      </div>
    </div>
  );
}

function PersonalDetails({ info }) {
  return (
    <dl className="space-y-4">
      <DetailItem icon={Hash} label="Student ID" value={info.studentId} />
      <DetailItem icon={Mail} label="Email" value={info.email} />
      <DetailItem icon={Phone} label="Phone" value={info.phone} />
      <DetailItem icon={Home} label="Address" value={info.address} />
    </dl>
  );
}

export default PersonalDetails;