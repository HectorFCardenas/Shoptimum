import React, { useState } from "react";

function Preferences() {
  const [preferences, setPreferences] = useState({
    diet: [], // Array to hold selected diets
    allergies: [], // Array to hold selected allergens
    bannedIngredients: "",
  });

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
    "Wheat"
  ]; 

  const handleMultiSelectChange = (field, value) => {
    setPreferences((prev) => {
      const updatedArray = prev[field].includes(value)
        ? prev[field].filter((item) => item !== value) // Remove if already selected
        : [...prev[field], value]; // Add if not selected
      return { ...prev, [field]: updatedArray };
    });
  };

  const handleChange = (e) => {
    setPreferences({
      ...preferences,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent the default form submission behavior
  
    try {
      const response = await fetch("http://127.0.0.1:5000/preferences", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(preferences), // Send the preferences object as JSON
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
    <div className="page">
      <h2>Set Your Preferences</h2>
      <form onSubmit={handleSubmit} className="preferences-form">
        <fieldset>
          <legend>Diet:</legend>
          {dietOptions.map((option) => (
            <label key={option}>
              <input
                type="checkbox"
                name="diet"
                value={option}
                checked={preferences.diet.includes(option)}
                onChange={() => handleMultiSelectChange("diet", option)}
              />
              {option}
            </label>
          ))}
        </fieldset>
        <fieldset>
          <legend>Allergies:</legend>
          {allergyOptions.map((option) => (
            <label key={option}>
              <input
                type="checkbox"
                name="allergies"
                value={option}
                checked={preferences.allergies.includes(option)}
                onChange={() => handleMultiSelectChange("allergies", option)}
              />
              {option}
            </label>
          ))}
        </fieldset>
        <label>
          Banned Ingredients:
          <input
            type="text"
            name="bannedIngredients"
            value={preferences.bannedIngredients}
            onChange={handleChange}
            placeholder="E.g., pork, gluten"
          />
        </label>
        <button type="submit">Save Preferences</button>
      </form>
    </div>
  );
}

export default Preferences;
