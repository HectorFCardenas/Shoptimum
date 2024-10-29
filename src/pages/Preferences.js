import React, { useState } from 'react';

function Preferences() {
  const [preferences, setPreferences] = useState({
    diet: '',
    allergies: '',
    bannedIngredients: '',
  });

  const handleChange = (e) => {
    setPreferences({
      ...preferences,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Preferences submitted:', preferences);
  };

  return (
    <div className="page">
      <h2>Set Your Preferences</h2>
      <form onSubmit={handleSubmit} className="preferences-form">
        <label>Diet:<select name="diet" value={preferences.diet} onChange={handleChange}>
            <option value="">Select Diet</option>
            <option value="none">None</option>
            <option value="vegetarian">Vegetarian</option>
            <option value="keto">Keto</option>
          </select>
        </label>
        <label>Allergies:<input type="text" name="allergies" value={preferences.allergies} onChange={handleChange} placeholder="E.g., peanuts, shellfish"/>
        </label>
        <label>Banned Ingredients:<input type="text" name="bannedIngredients" value={preferences.bannedIngredients} onChange={handleChange} placeholder="E.g., pork, gluten"/>
        </label>
        <button type="submit">Save Preferences</button>
      </form>
    </div>
  );
}

export default Preferences;