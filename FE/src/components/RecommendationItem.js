import React from 'react';
import './RecommendationItem.css';

function RecommendationItem({ item }) {
  const handleAddToGroceryList = () => {
    console.log('Added to grocery list:', item.name);
  };

  return (
    <div className="recommendation-item">
      <h3>{item.name}</h3>
      <p>{item.description}</p>
      <button onClick={handleAddToGroceryList}>Add to Grocery List</button>
    </div>
  );
}

export default RecommendationItem;