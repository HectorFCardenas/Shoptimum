import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './SetInitialRecommendations.css';

const SetInitialRecommendations = () => {
  const [step, setStep] = useState(1);
  const [dietaryRestrictions, setDietaryRestrictions] = useState([]);
  const [recipes] = useState([
    "Spaghetti Carbonara",
    "Grilled Chicken Salad",
    "Vegan Tacos",
    "Keto Pancakes",
    "Gluten-Free Pizza",
    "Paleo Beef Stew",
  ]); // Mock recipes
  const [selectedRecipes, setSelectedRecipes] = useState([]);
  const navigate = useNavigate();

  const dietOptions = [
    "Vegetarian",
    "Vegan",
    "Keto",
    "Gluten-Free",
    "Pescatarian",
    "Paleo",
  ];

  const handleDietarySelect = (diet) => {
    setDietaryRestrictions((prev) =>
      prev.includes(diet)
        ? prev.filter((item) => item !== diet)
        : [...prev, diet]
    );
  };

  const handleRecipeSelect = (recipe) => {
    setSelectedRecipes((prev) =>
      prev.includes(recipe)
        ? prev.filter((item) => item !== recipe)
        : [...prev, recipe]
    );
  };

  const canProceed = () => {
    if (step === 1) {
      return dietaryRestrictions.length > 0;
    } else if (step === 2) {
      return selectedRecipes.length >= 5;
    }
    return false;
  };

  const handleNext = () => {
    if (step === 1) {
      // Store dietary restrictions
      localStorage.setItem("dietaryRestrictions", JSON.stringify(dietaryRestrictions));
      setStep(2);
    } else if (step === 2) {
      // Store selected recipes
      localStorage.setItem("selectedRecipes", JSON.stringify(selectedRecipes));
      navigate("/home"); // Redirect to a welcome page or home
    }
  };

  return (
    <div className="set-recommendations-page">
      {step === 1 && (
        <>
          <h1>Step 1: Set Your Dietary Restrictions</h1>
          <div className="diet-options">
            {dietOptions.map((diet) => (
              <div
                key={diet}
                className={`diet-bubble ${
                  dietaryRestrictions.includes(diet) ? "selected" : ""
                }`}
                onClick={() => handleDietarySelect(diet)}
              >
                {diet}
              </div>
            ))}
          </div>
        </>
      )}

      {step === 2 && (
        <>
          <h1>Step 2: Select Your Favorite Recipes</h1>
          <div className="recipes-container">
            {recipes.map((recipe) => (
              <div
                key={recipe}
                className={`recipe-bubble ${
                  selectedRecipes.includes(recipe) ? "selected" : ""
                }`}
                onClick={() => handleRecipeSelect(recipe)}
              >
                {recipe}
              </div>
            ))}
          </div>
        </>
      )}

      <button
        className="next-button"
        onClick={handleNext}
        disabled={!canProceed()}
      >
        {step === 1 ? "Next" : "Finish"}
      </button>
    </div>
  );
};

export default SetInitialRecommendations;