import React, { useEffect, useState } from 'react';
import RecommendationItem from '../components/RecommendationItem';

function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    const mockData = [
      {id: 1, name: 'Grilled Chicken Salad', description: 'A healthy salad with grilled chicken and fresh veggies.'},
      {id: 2, name: 'Quinoa Bowl', description: 'A nutritious quinoa bowl with mixed vegetables.'},
    ];
    setRecommendations(mockData);
  }, []);

  return (
    <div className="page">
      <h2>Your Recommendations</h2>
      <div className="recommendations-list">
        {recommendations.map((item) => (
          <RecommendationItem key={item.id} item={item} />
        ))}
      </div>
    </div>
  );
}

export default Recommendations;