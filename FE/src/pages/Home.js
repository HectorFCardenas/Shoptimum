import React, { useState } from 'react';
import './Home.css';

function Home() {
  const [view, setView] = useState('week'); // 'week' or 'month'
  const [currentDate, setCurrentDate] = useState(new Date());

  const meals = {
    breakfast: 'Avocado Toast with Eggs',
    lunch: 'Grilled Chicken Salad',
    dinner: 'Teriyaki Salmon with Rice',
  };

  const getDaysInWeek = (startDate) => {
    const days = [];
    const start = new Date(startDate);
    start.setDate(start.getDate() - start.getDay());
    for (let i = 0; i < 7; i++) {
      const date = new Date(start);
      date.setDate(start.getDate() + i);
      days.push(date);
    }
    return days;
  };

  const getDaysInMonth = (date) => {
    const days = [];
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    let current = new Date(firstDay);

    while (current <= lastDay) {
      days.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }

    return days;
  };

  const handlePrevious = () => {
    const newDate = new Date(currentDate);
    if (view === 'week') {
      newDate.setDate(currentDate.getDate() - 7);
    } else {
      newDate.setMonth(currentDate.getMonth() - 1);
    }
    setCurrentDate(newDate);
  };

  const handleNext = () => {
    const newDate = new Date(currentDate);
    if (view === 'week') {
      newDate.setDate(currentDate.getDate() + 7);
    } else {
      newDate.setMonth(currentDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  const formatDate = (date) =>
    date.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' });

    const renderCalendar = () => {
      if (view === 'week') {
        const weekDays = getDaysInWeek(currentDate);
        return (
          <div className="calendar-grid-week">
            {weekDays.map((day, index) => (
              <div key={index} className="calendar-card">
                <h3>{formatDate(day)}</h3>
                <div className="meal breakfast">
                  <p>Breakfast: {meals.breakfast}</p>
                </div>
                <div className="meal lunch">
                  <p>Lunch: {meals.lunch}</p>
                </div>
                <div className="meal dinner">
                  <p>Dinner: {meals.dinner}</p>
                </div>
              </div>
            ))}
          </div>
        );
      } else {
        const monthDays = getDaysInMonth(currentDate);
        return (
          <div className="calendar-grid-month">
            {monthDays.map((day, index) => (
              <div key={index} className="calendar-card">
                <h3>{formatDate(day)}</h3>
                <div className="meal breakfast">
                  <p>Breakfast: {meals.breakfast}</p>
                </div>
                <div className="meal lunch">
                  <p>Lunch: {meals.lunch}</p>
                </div>
                <div className="meal dinner">
                  <p>Dinner: {meals.dinner}</p>
                </div>
              </div>
            ))}
          </div>
        );
      }
    };

  return (
    <div className="home-container">
      <header className="calendar-header">
        <button onClick={handlePrevious} className="nav-button">
          &lt;
        </button>
        <h2 className="calendar-title">
          {view === 'week'
            ? `Week of ${formatDate(getDaysInWeek(currentDate)[0])}`
            : currentDate.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}
        </h2>
        <button onClick={handleNext} className="nav-button">
          &gt;
        </button>
        <div className="view-toggle">
          <label className="switch">
            <input
              type="checkbox"
              checked={view === 'month'}
              onChange={() => setView(view === 'week' ? 'month' : 'week')}
            />
            <span className="slider round"></span>
          </label>
          <span>{view === 'week' ? 'Week View' : 'Month View'}</span>
        </div>
      </header>
      {renderCalendar()}
    </div>
  );
}

export default Home;