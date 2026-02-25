export const WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
export const DURATIONS = ["30 min", "45 min", "60 min", "75 min", "90 min"];
export const GOALS = ["Hypertrophy", "Strength", "Fat loss", "General fitness"];
export const EQUIPMENT = ["Barbell", "Dumbbell", "Machine", "Bodyweight"];

// educated guess based on weight and height got from chatgpt 
export const ONE_RM_GUESSES = {
  male: {
    beginner: [
      { weight: 60, height: 165, squat: 47.5, bench: 32.5, deadlift: 57.5, ohp: 22.5 },
      { weight: 75, height: 175, squat: 55.0, bench: 37.5, deadlift: 75.0, ohp: 25.0 },
      { weight: 85, height: 190, squat: 60.0, bench: 37.5, deadlift: 90.0, ohp: 27.5 },
      { weight: 100, height: 190, squat: 80.0, bench: 52.5, deadlift: 100.0, ohp: 35.0 },
    ],
    intermediate: [
      { weight: 60, height: 165, squat: 95.0, bench: 80.0, deadlift: 115.0, ohp: 50.0 },
      { weight: 75, height: 175, squat: 112.5, bench: 95.0, deadlift: 150.0, ohp: 60.0 },
      { weight: 85, height: 190, squat: 120.0, bench: 95.0, deadlift: 177.5, ohp: 65.0 },
      { weight: 100, height: 190, squat: 157.5, bench: 130.0, deadlift: 200.0, ohp: 80.0 },
    ],
    advanced: [
      { weight: 60, height: 165, squat: 142.5, bench: 110.0, deadlift: 142.5, ohp: 70.0 },
      { weight: 75, height: 175, squat: 170.0, bench: 130.0, deadlift: 187.5, ohp: 82.5 },
      { weight: 85, height: 190, squat: 182.5, bench: 135.0, deadlift: 222.5, ohp: 90.0 },
      { weight: 100, height: 190, squat: 235.0, bench: 185.0, deadlift: 250.0, ohp: 110.0 },
    ],
  },
  female: {
    beginner: [
      { weight: 50, height: 160, squat: 32.5, bench: 17.5, deadlift: 40.0, ohp: 12.5 },
      { weight: 60, height: 165, squat: 35.0, bench: 20.0, deadlift: 50.0, ohp: 15.0 },
      { weight: 70, height: 175, squat: 40.0, bench: 22.5, deadlift: 62.5, ohp: 17.5 },
      { weight: 85, height: 175, squat: 52.5, bench: 30.0, deadlift: 72.5, ohp: 20.0 },
    ],
    intermediate: [
      { weight: 50, height: 160, squat: 60.0, bench: 37.5, deadlift: 70.0, ohp: 20.0 },
      { weight: 60, height: 165, squat: 70.0, bench: 42.5, deadlift: 90.0, ohp: 25.0 },
      { weight: 70, height: 175, squat: 77.5, bench: 45.0, deadlift: 110.0, ohp: 27.5 },
      { weight: 85, height: 175, squat: 102.5, bench: 62.5, deadlift: 127.5, ohp: 35.0 },
    ],
    advanced: [
      { weight: 50, height: 160, squat: 90.0, bench: 52.5, deadlift: 95.0, ohp: 30.0 },
      { weight: 60, height: 165, squat: 102.5, bench: 60.0, deadlift: 120.0, ohp: 32.5 },
      { weight: 70, height: 175, squat: 112.5, bench: 62.5, deadlift: 147.5, ohp: 37.5 },
      { weight: 85, height: 175, squat: 152.5, bench: 90.0, deadlift: 170.0, ohp: 47.5 },
    ],
  },
};
