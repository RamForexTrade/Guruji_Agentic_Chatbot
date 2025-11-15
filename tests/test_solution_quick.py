"""Quick test of solution generation"""

from agents.solution_generator import SolutionGenerator
from agents.agent_types import EmotionalState, LifeSituation, UserLocation

# Test with values from your conversation
emotion = EmotionalState.DEPRESSION  # "hopeless" maps to depression
situation = LifeSituation.UNKNOWN  # not extracted yet
location = UserLocation.HOME_INDOOR

wisdom_text = "This too shall pass. In the darkness, remember that light is just around the corner. - Gurudev"

try:
    solution = SolutionGenerator.generate(
        emotion=emotion,
        situation=situation,
        location=location,
        age=30,
        tone="warm",
        user_name="Venkat",
        wisdom_text=wisdom_text
    )

    formatted = SolutionGenerator.format_solution(solution, location)

    print("="*60)
    print("4-PART SOLUTION TEST")
    print("="*60)
    print(formatted)
    print("\n✅ Solution generation works!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
