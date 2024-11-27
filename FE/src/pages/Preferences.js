import React, { useState } from "react";
import "./Preferences.css";

function Preferences() {
  const [preferences, setPreferences] = useState({
    diet: [],
    allergies: [],
    bannedIngredients: "",
  });

  const [bannedList, setBannedList] = useState([]);

  const dietOptions = [
    "None",
    "Vegetarian",
    "Lacto-Vegetarian",
    "Ovo-Vegetarian",
    "Vegan",
    "Ketogenic",
    "Gluten Free",
    "Pescetarian",
    "Paleo",
    "Primal",
    "Low FODMAP",
    "Whole30",
  ];

  const allergyOptions = [
    "Dairy",
    "Peanut",
    "Soy",
    "Egg",
    "Seafood",
    "Sulfite",
    "Gluten",
    "Sesame",
    "Tree Nut",
    "Grain",
    "Shellfish",
    "Wheat",
  ];

  const handleMultiSelectChange = (field, value) => {
    setPreferences((prev) => {
      const updatedArray = prev[field].includes(value)
        ? prev[field].filter((item) => item !== value)
        : [...prev[field], value];
      return { ...prev, [field]: updatedArray };
    });
  };

  const handleBannedChange = (e) => {
    setPreferences({ ...preferences, bannedIngredients: e.target.value });
  };

  const addBannedIngredient = () => {
    if (preferences.bannedIngredients.trim() && !bannedList.includes(preferences.bannedIngredients.trim())) {
      setBannedList([...bannedList, preferences.bannedIngredients.trim()]);
      setPreferences({ ...preferences, bannedIngredients: "" });
    }
  };

  const removeBannedIngredient = (ingredient) => {
    setBannedList(bannedList.filter((item) => item !== ingredient));
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addBannedIngredient();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:5000/preferences", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ...preferences, bannedIngredients: bannedList }),
      });

      if (!response.ok) {
        throw new Error("Failed to update preferences");
      }

      const data = await response.json();
      console.log("Preferences submitted successfully:", data);
    } catch (error) {
      console.error("Error submitting preferences:", error);
    }
  };

  return (
    <div className="preferences-container">
      <h2 className="preferences-title">Set Your Preferences</h2>
      <form onSubmit={handleSubmit} className="preferences-form">
        <div className="preferences-section">
          <h3>Dietary Preferences</h3>
          <div className="preferences-options">
            {dietOptions.map((option) => (
              <label key={option} className="preferences-option">
                {option}
                <input
                  type="checkbox"
                  name="diet"
                  value={option}
                  checked={preferences.diet.includes(option)}
                  onChange={() => handleMultiSelectChange("diet", option)}
                />
              </label>
            ))}
          </div>
        </div>
        <div className="preferences-section">
          <h3>Allergy Information</h3>
          <div className="preferences-options">
            {allergyOptions.map((option) => (
              <label key={option} className="preferences-option">
                {option}
                <input
                  type="checkbox"
                  name="allergies"
                  value={option}
                  checked={preferences.allergies.includes(option)}
                  onChange={() => handleMultiSelectChange("allergies", option)}
                />
              </label>
            ))}
          </div>
        </div>
        <div className="preferences-section">
          <h3>Banned Ingredients</h3>
          <div className="banned-input-container">
            <input
              type="text"
              name="bannedIngredients"
              value={preferences.bannedIngredients}
              onChange={handleBannedChange}
              onKeyPress={handleKeyPress}
              placeholder="Type an ingredient and press Enter or +"
              className="preferences-input"
            />
            <button
              type="button"
              onClick={addBannedIngredient}
              className="add-button"
            >
              +
            </button>
          </div>
          <ul className="banned-list">
            {bannedList.map((ingredient, index) => (
              <li key={index} className="banned-item">
                {ingredient}
                <button
                  type="button"
                  className="remove-button"
                  onClick={() => removeBannedIngredient(ingredient)}
                >
                  x
                </button>
              </li>
            ))}
          </ul>
        </div>
        <button type="submit" className="preferences-button">
          Save Preferences
        </button>
      </form>
    </div>
  );
}

export default Preferences;