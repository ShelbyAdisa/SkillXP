import React, { useState, useEffect, useMemo } from 'react';
import { Bus, Clock, AlertCircle, ChevronDown, ChevronUp, Navigation } from 'lucide-react';
import DashboardLayout from '../components/layout/DashboardLayout';
import { useAuth } from '../context/AuthContext';

const Transportation = () => {
  const { user } = useAuth();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [expandedRoute, setExpandedRoute] = useState(null);
  const [selectedRoute, setSelectedRoute] = useState(null);

  // Bus routes configuration with 4 rounds (2 morning, 2 afternoon)
  const busRoutes = [
    {
      id: 'route-a',
      name: 'Route A - North',
      color: '#2563EB',
      rounds: [
        {
          id: 'morning-1',
          type: 'pickup',
          label: 'Morning Pickup 1',
          stops: [
            { name: 'Maple Heights', time: '06:30', coords: { x: 15, y: 20 } },
            { name: 'Oak Avenue', time: '06:35', coords: { x: 25, y: 25 } },
            { name: 'Highland Park', time: '06:42', coords: { x: 35, y: 30 } },
            { name: 'Riverside', time: '06:48', coords: { x: 45, y: 25 } },
            { name: 'Northgate', time: '06:55', coords: { x: 55, y: 20 } },
            { name: 'School', time: '07:05', coords: { x: 50, y: 50 }, isSchool: true }
          ]
        },
        {
          id: 'morning-2',
          type: 'pickup',
          label: 'Morning Pickup 2',
          stops: [
            { name: 'Pine Street', time: '07:30', coords: { x: 20, y: 35 } },
            { name: 'Cedar Lane', time: '07:38', coords: { x: 30, y: 40 } },
            { name: 'Birch Road', time: '07:45', coords: { x: 40, y: 45 } },
            { name: 'Elm Court', time: '07:52', coords: { x: 55, y: 40 } },
            { name: 'School', time: '08:00', coords: { x: 50, y: 50 }, isSchool: true }
          ]
        },
        {
          id: 'afternoon-1',
          type: 'dropoff',
          label: 'Afternoon Drop-off 1',
          stops: [
            { name: 'School', time: '14:30', coords: { x: 50, y: 50 }, isSchool: true },
            { name: 'Northgate', time: '14:40', coords: { x: 55, y: 20 } },
            { name: 'Riverside', time: '14:47', coords: { x: 45, y: 25 } },
            { name: 'Highland Park', time: '14:53', coords: { x: 35, y: 30 } },
            { name: 'Oak Avenue', time: '15:00', coords: { x: 25, y: 25 } },
            { name: 'Maple Heights', time: '15:05', coords: { x: 15, y: 20 } }
          ]
        },
        {
          id: 'afternoon-2',
          type: 'dropoff',
          label: 'Afternoon Drop-off 2',
          stops: [
            { name: 'School', time: '15:30', coords: { x: 50, y: 50 }, isSchool: true },
            { name: 'Elm Court', time: '15:38', coords: { x: 55, y: 40 } },
            { name: 'Birch Road', time: '15:45', coords: { x: 40, y: 45 } },
            { name: 'Cedar Lane', time: '15:52', coords: { x: 30, y: 40 } },
            { name: 'Pine Street', time: '16:00', coords: { x: 20, y: 35 } }
          ]
        }
      ]
    },
    {
      id: 'route-b',
      name: 'Route B - South/East',
      color: '#7C3AED',
      rounds: [
        {
          id: 'morning-1',
          type: 'pickup',
          label: 'Morning Pickup 1',
          stops: [
            { name: 'Valley View', time: '06:30', coords: { x: 25, y: 75 } },
            { name: 'Southside', time: '06:37', coords: { x: 35, y: 70 } },
            { name: 'Medical Center', time: '06:44', coords: { x: 45, y: 65 } },
            { name: 'Pine Grove', time: '06:50', coords: { x: 60, y: 70 } },
            { name: 'Willow Creek', time: '06:57', coords: { x: 70, y: 75 } },
            { name: 'School', time: '07:05', coords: { x: 50, y: 50 }, isSchool: true }
          ]
        },
        {
          id: 'morning-2',
          type: 'pickup',
          label: 'Morning Pickup 2',
          stops: [
            { name: 'Eastwood', time: '07:30', coords: { x: 75, y: 55 } },
            { name: 'Sunrise Apt', time: '07:37', coords: { x: 80, y: 45 } },
            { name: 'Cedar Heights', time: '07:44', coords: { x: 65, y: 50 } },
            { name: 'Lakeside', time: '07:52', coords: { x: 60, y: 60 } },
            { name: 'School', time: '08:00', coords: { x: 50, y: 50 }, isSchool: true }
          ]
        },
        {
          id: 'afternoon-1',
          type: 'dropoff',
          label: 'Afternoon Drop-off 1',
          stops: [
            { name: 'School', time: '14:30', coords: { x: 50, y: 50 }, isSchool: true },
            { name: 'Willow Creek', time: '14:38', coords: { x: 70, y: 75 } },
            { name: 'Pine Grove', time: '14:45', coords: { x: 60, y: 70 } },
            { name: 'Medical Center', time: '14:51', coords: { x: 45, y: 65 } },
            { name: 'Southside', time: '14:58', coords: { x: 35, y: 70 } },
            { name: 'Valley View', time: '15:05', coords: { x: 25, y: 75 } }
          ]
        },
        {
          id: 'afternoon-2',
          type: 'dropoff',
          label: 'Afternoon Drop-off 2',
          stops: [
            { name: 'School', time: '15:30', coords: { x: 50, y: 50 }, isSchool: true },
            { name: 'Lakeside', time: '15:38', coords: { x: 60, y: 60 } },
            { name: 'Cedar Heights', time: '15:46', coords: { x: 65, y: 50 } },
            { name: 'Sunrise Apt', time: '15:53', coords: { x: 80, y: 45 } },
            { name: 'Eastwood', time: '16:00', coords: { x: 75, y: 55 } }
          ]
        }
      ]
    }
  ];

  // Update current time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Parse time string to minutes since midnight
  const parseTimeToMinutes = (timeStr) => {
    const [time, period] = timeStr.split(' ');
    const [hours, minutes] = time.split(':').map(Number);
    let totalMinutes = hours * 60 + minutes;
    
    // Handle 24-hour format (no AM/PM)
    if (!period) {
      return totalMinutes;
    }
    
    // Handle AM/PM format
    if (period === 'PM' && hours !== 12) {
      totalMinutes += 12 * 60;
    } else if (period === 'AM' && hours === 12) {
      totalMinutes -= 12 * 60;
    }
    
    return totalMinutes;
  };

  // Get current minutes since midnight
  const getCurrentMinutes = () => {
    const now = currentTime;
    return now.getHours() * 60 + now.getMinutes();
  };

  // Calculate bus position for a round
  const getBusPosition = (round) => {
    const currentMinutes = getCurrentMinutes();
    const startTime = parseTimeToMinutes(round.stops[0].time);
    const endTime = parseTimeToMinutes(round.stops[round.stops.length - 1].time);
    
    // Check if bus is active
    if (currentMinutes < startTime - 5 || currentMinutes > endTime + 5) {
      return null;
    }
    
    // Find current segment
    for (let i = 0; i < round.stops.length - 1; i++) {
      const stopTime = parseTimeToMinutes(round.stops[i].time);
      const nextStopTime = parseTimeToMinutes(round.stops[i + 1].time);
      
      if (currentMinutes >= stopTime && currentMinutes <= nextStopTime) {
        const progress = (currentMinutes - stopTime) / (nextStopTime - stopTime);
        const currentCoords = round.stops[i].coords;
        const nextCoords = round.stops[i + 1].coords;
        
        return {
          x: currentCoords.x + (nextCoords.x - currentCoords.x) * progress,
          y: currentCoords.y + (nextCoords.y - currentCoords.y) * progress,
          currentStop: i,
          nextStop: i + 1,
          progress,
          status: Math.abs(currentMinutes - stopTime) <= 2 ? 'on-time' : 'delayed'
        };
      }
    }
    
    return null;
  };

  // Get active rounds and their positions
  const activeBuses = useMemo(() => {
    const buses = [];
    busRoutes.forEach(route => {
      route.rounds.forEach(round => {
        const position = getBusPosition(round);
        if (position) {
          buses.push({
            routeId: route.id,
            routeName: route.name,
            roundId: round.id,
            roundLabel: round.label,
            color: route.color,
            position,
            round
          });
        }
      });
    });
    return buses;
  }, [currentTime]);

  // Get next bus for each route
  const getNextBus = (route) => {
    const currentMinutes = getCurrentMinutes();
    
    for (const round of route.rounds) {
      const startTime = parseTimeToMinutes(round.stops[0].time);
      if (startTime > currentMinutes) {
        return {
          round,
          minutesUntil: startTime - currentMinutes
        };
      }
    }
    
    // If no bus today, return first bus tomorrow
    const firstRound = route.rounds[0];
    const firstTime = parseTimeToMinutes(firstRound.stops[0].time);
    return {
      round: firstRound,
      minutesUntil: (24 * 60 - currentMinutes) + firstTime,
      tomorrow: true
    };
  };

  // Generate curved path between points
  const generatePath = (points) => {
    if (points.length < 2) return '';
    
    let path = `M ${points[0].x} ${points[0].y}`;
    
    for (let i = 1; i < points.length; i++) {
      const prev = points[i - 1];
      const curr = points[i];
      const cp1x = prev.x + (curr.x - prev.x) * 0.5;
      const cp1y = prev.y;
      const cp2x = prev.x + (curr.x - prev.x) * 0.5;
      const cp2y = curr.y;
      
      path += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${curr.x} ${curr.y}`;
    }
    
    return path;
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bus className="w-8 h-8 text-slate-900" />
              <div>
                <h1 className="text-3xl font-bold text-slate-900">Transportation</h1>
                <p className="text-slate-600 mt-1">Live bus tracking and schedules</p>
              </div>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 rounded-lg">
              <Clock className="w-5 h-5 text-slate-600" />
              <span className="font-mono font-medium text-slate-900">
                {currentTime.toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Map Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg border border-slate-200 p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-4">Live Route Map</h2>
              
              {/* Map Container with Background Image */}
              <div className="relative bg-slate-50 rounded-lg border border-slate-200 overflow-hidden">
                <div className="w-full h-[500px] relative">
                  {/* Map Background Image */}
                  <div 
                    className="absolute inset-0 bg-cover bg-center opacity-80"
                    style={{
                      backgroundImage: 'url("https://images.unsplash.com/photo-1569336415962-a4bd9f69cd83?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80")'
                    }}
                  />
                  
                  {/* Overlay for bus routes and stops */}
                  <svg viewBox="0 0 100 100" className="absolute inset-0 w-full h-full">
                    {/* Bus Routes - Show all routes at all times */}
                    <g id="routes">
                      {busRoutes.map(route => {
                        const isSelected = !selectedRoute || selectedRoute === route.id;
                        
                        return (
                          <g key={route.id} opacity={isSelected ? 1 : 0.3}>
                            {/* Draw route paths for ALL rounds */}
                            {route.rounds.map(round => (
                              <g key={round.id}>
                                <path
                                  d={generatePath(round.stops)}
                                  fill="none"
                                  stroke={route.color}
                                  strokeWidth="1.5"
                                  strokeDasharray="4,2"
                                  opacity="0.6"
                                />
                                
                                {/* Stop markers for ALL stops */}
                                {round.stops.map((stop, idx) => (
                                  <g key={`${round.id}-${idx}`}>
                                    <circle
                                      cx={stop.coords.x}
                                      cy={stop.coords.y}
                                      r="1.5"
                                      fill="white"
                                      stroke={route.color}
                                      strokeWidth="1"
                                    />
                                    {!stop.isSchool && (
                                      <text
                                        x={stop.coords.x}
                                        y={stop.coords.y - 3}
                                        textAnchor="middle"
                                        fontSize="2.5"
                                        fill={route.color}
                                        fontWeight="bold"
                                        className="font-sans"
                                      >
                                        {stop.name.split(' ')[0]}
                                      </text>
                                    )}
                                  </g>
                                ))}
                              </g>
                            ))}
                          </g>
                        );
                      })}
                    </g>
                    
                    {/* School Marker */}
                    <g id="school">
                      <circle
                        cx="50"
                        cy="50"
                        r="3"
                        fill="#DC2626"
                        stroke="#fff"
                        strokeWidth="1"
                      />
                      <text
                        x="50"
                        y="50"
                        textAnchor="middle"
                        fontSize="3"
                        fill="white"
                        fontWeight="bold"
                        dy="1"
                        className="font-sans"
                      >
                        S
                      </text>
                      <text
                        x="50"
                        y="56"
                        textAnchor="middle"
                        fontSize="2.5"
                        fill="#DC2626"
                        fontWeight="bold"
                        className="font-sans"
                      >
                        School
                      </text>
                    </g>
                    
                    {/* Active Buses */}
                    <g id="buses">
                      {activeBuses.map((bus, idx) => (
                        <g key={`${bus.routeId}-${bus.roundId}`}>
                          {/* Bus icon with animation */}
                          <g transform={`translate(${bus.position.x}, ${bus.position.y})`}>
                            {/* Pulsing circle */}
                            <circle r="3" fill={bus.color} opacity="0.4">
                              <animate
                                attributeName="r"
                                values="3;5;3"
                                dur="2s"
                                repeatCount="indefinite"
                              />
                              <animate
                                attributeName="opacity"
                                values="0.4;0.1;0.4"
                                dur="2s"
                                repeatCount="indefinite"
                              />
                            </circle>
                            
                            {/* Bus icon */}
                            <rect
                              x="-2.5"
                              y="-2"
                              width="5"
                              height="4"
                              rx="1"
                              fill={bus.color}
                              stroke="white"
                              strokeWidth="0.5"
                            />
                            <circle
                              cx="-1"
                              cy="2.5"
                              r="0.8"
                              fill="#374151"
                            />
                            <circle
                              cx="1"
                              cy="2.5"
                              r="0.8"
                              fill="#374151"
                            />
                            <text
                              x="0"
                              y="0"
                              textAnchor="middle"
                              fontSize="2"
                              fill="white"
                              fontWeight="bold"
                              dy="0.5"
                              className="font-sans"
                            >
                              B
                            </text>
                          </g>
                          
                          {/* Route label near bus */}
                          <text
                            x={bus.position.x}
                            y={bus.position.y - 6}
                            textAnchor="middle"
                            fontSize="2.5"
                            fill={bus.color}
                            fontWeight="bold"
                            className="font-sans"
                          >
                            {bus.routeName.split(' ')[1]}
                          </text>
                        </g>
                      ))}
                    </g>
                  </svg>
                  
                  {/* Map Legend */}
                  <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg border border-slate-200">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-red-600 rounded-full"></div>
                        <span className="text-xs font-medium text-slate-700">School</span>
                      </div>
                      {busRoutes.map(route => (
                        <div key={route.id} className="flex items-center gap-2">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: route.color }}
                          ></div>
                          <span className="text-xs font-medium text-slate-700">
                            {route.name.split(' - ')[0]}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Route Filter */}
              <div className="mt-4 flex flex-wrap gap-2">
                <button
                  onClick={() => setSelectedRoute(null)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    !selectedRoute 
                      ? 'bg-slate-900 text-white' 
                      : 'text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  All Routes
                </button>
                {busRoutes.map(route => (
                  <button
                    key={route.id}
                    onClick={() => setSelectedRoute(route.id === selectedRoute ? null : route.id)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      selectedRoute === route.id 
                        ? 'bg-slate-900 text-white' 
                        : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: route.color }}
                    />
                    {route.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          {/* Schedule & Status Panel */}
          <div className="space-y-4">
            {/* Active Buses */}
            <div className="bg-white rounded-lg border border-slate-200 p-6">
              <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                <Navigation className="w-5 h-5 text-slate-700" />
                Active Buses ({activeBuses.length})
              </h3>
              
              {activeBuses.length > 0 ? (
                <div className="space-y-3">
                  {activeBuses.map(bus => (
                    <div 
                      key={`${bus.routeId}-${bus.roundId}`} 
                      className="p-3 bg-slate-50 rounded-lg border border-slate-200 hover:bg-slate-100 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-slate-900">{bus.routeName}</span>
                        <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full">
                          Active
                        </span>
                      </div>
                      <div className="text-sm text-slate-600">
                        <p>{bus.roundLabel}</p>
                        <p className="mt-1">
                          Next: {bus.round.stops[bus.position.nextStop]?.name}
                        </p>
                        <p className="text-xs mt-1 text-slate-500">
                          ETA: {bus.round.stops[bus.position.nextStop]?.time}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-500 text-sm">No buses currently active</p>
              )}
            </div>
            
            {/* Route Schedules */}
            <div className="bg-white rounded-lg border border-slate-200 p-6">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Route Schedules</h3>
              
              <div className="space-y-3">
                {busRoutes.map(route => {
                  const nextBus = getNextBus(route);
                  const isExpanded = expandedRoute === route.id;
                  
                  return (
                    <div key={route.id} className="border border-slate-200 rounded-lg overflow-hidden">
                      <button
                        onClick={() => setExpandedRoute(isExpanded ? null : route.id)}
                        className="w-full p-4 text-left hover:bg-slate-100 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div 
                              className="w-10 h-10 rounded-lg flex items-center justify-center"
                              style={{ backgroundColor: `${route.color}20` }}
                            >
                              <Bus className="w-5 h-5" style={{ color: route.color }} />
                            </div>
                            <div>
                              <h4 className="font-medium text-slate-900">{route.name}</h4>
                              <p className="text-sm text-slate-600">
                                Next: {nextBus.round.label} in {nextBus.minutesUntil} min
                                {nextBus.tomorrow && ' (tomorrow)'}
                              </p>
                            </div>
                          </div>
                          {isExpanded ? (
                            <ChevronUp className="w-5 h-5 text-slate-400" />
                          ) : (
                            <ChevronDown className="w-5 h-5 text-slate-400" />
                          )}
                        </div>
                      </button>
                      
                      {isExpanded && (
                        <div className="px-4 pb-4 border-t border-slate-200">
                          <div className="mt-4 space-y-4">
                            {route.rounds.map(round => (
                              <div key={round.id}>
                                <h5 className="font-medium text-slate-700 mb-2 text-sm">
                                  {round.label}
                                </h5>
                                <div className="grid grid-cols-2 gap-2 text-xs">
                                  {round.stops.map((stop, idx) => (
                                    <div key={idx} className="flex items-center gap-2">
                                      <span className="text-slate-500">{stop.time}</span>
                                      <span className="text-slate-700">{stop.name}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
            
            {/* Info */}
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
              <div className="flex gap-3">
                <AlertCircle className="w-5 h-5 text-slate-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-slate-900 mb-1">Live Tracking</p>
                  <p className="text-slate-700">
                    Bus positions update in real-time. Morning pickups: 6:30-8:00 AM. 
                    Afternoon drop-offs: 2:30-4:00 PM.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Transportation;