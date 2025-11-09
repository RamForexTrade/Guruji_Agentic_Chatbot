"""
Solution Generator for 4-Part Holistic Guidance
================================================

Generates complete solutions with:
1. Pranayama (breathing exercises)
2. Yoga Asana (physical exercises)
3. Wisdom Byte (verbatim from Gurudev's Knowledge Sheets)
4. Light Activity/Joke (age-appropriate)

All recommendations are tailored to:
- User's emotional state
- Life situation
- Physical location
- Age bracket
- Appropriate tone (warm, somber, playful)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

from agents.agent_types import (
    EmotionalState,
    LifeSituation,
    UserLocation,
    SeverityLevel
)

logger = logging.getLogger(__name__)


@dataclass
class PranayamaRecommendation:
    """Pranayama practice recommendation"""
    name: str
    description: str
    duration: str
    location_adaptations: Dict[str, str]  # How to adapt for different locations
    benefits: List[str]
    cautions: List[str] = None


@dataclass
class AsanaRecommendation:
    """Yoga asana recommendation"""
    name: str
    description: str
    duration: str
    location_adaptations: Dict[str, str]
    benefits: List[str]
    modifications: List[str]  # For beginners or limitations


@dataclass
class ActivitySuggestion:
    """Light activity or joke suggestion"""
    content: str
    activity_type: str  # joke, game, reflection, action
    age_appropriate: bool
    tone: str  # warm, playful, somber


@dataclass
class HolisticSolution:
    """Complete 4-part solution"""
    pranayama: PranayamaRecommendation
    asana: AsanaRecommendation
    wisdom: str  # Verbatim from Knowledge Sheets (provided by Wisdom Agent)
    activity: ActivitySuggestion
    personalized_intro: str
    tone: str


class PranayamaLibrary:
    """Library of pranayama practices mapped to emotional states"""

    @staticmethod
    def get_for_emotion(emotion: EmotionalState, location: UserLocation) -> PranayamaRecommendation:
        """Get appropriate pranayama for emotion and location"""

        pranayama_map = {
            EmotionalState.FEAR: PranayamaRecommendation(
                name="Nadi Shodhana (Alternate Nostril Breathing)",
                description="Gently close your right nostril with your thumb. Breathe in through the left nostril. Close the left nostril, open the right, and breathe out. Breathe in through the right, then switch. Continue for several rounds.",
                duration="5-10 minutes",
                location_adaptations={
                    "home_indoor": "Sit comfortably on a cushion or chair with your spine straight.",
                    "outdoor": "Find a quiet spot under a tree or on a bench.",
                    "office": "Sit at your desk, do this discreetly with gentle hand movements.",
                    "public_place": "Use a discreet variation - just focus on breathing through alternate nostrils mentally.",
                    "vehicle": "Not recommended while driving. If passenger, close eyes and practice."
                },
                benefits=["Calms anxiety", "Balances nervous system", "Reduces fear"],
                cautions=["Don't force the breath", "Stop if you feel dizzy"]
            ),

            EmotionalState.ANGER: PranayamaRecommendation(
                name="Sheetali Pranayama (Cooling Breath)",
                description="Roll your tongue into a tube. Breathe in slowly through the rolled tongue. Close your mouth and breathe out through your nose. Feel the cooling sensation calming your system.",
                duration="3-5 minutes",
                location_adaptations={
                    "home_indoor": "Sit in a comfortable position, spine erect.",
                    "outdoor": "Practice in fresh air for enhanced cooling effect.",
                    "office": "Can be done sitting at your desk, quite discreet.",
                    "public_place": "Find a quiet corner, practice subtly.",
                    "vehicle": "Safe for passengers, not while driving."
                },
                benefits=["Cools anger and frustration", "Calms the mind", "Reduces heat in the body"],
                cautions=["Avoid if you have a cold", "Don't overdo in cold weather"]
            ),

            EmotionalState.OVERWHELMED: PranayamaRecommendation(
                name="Diaphragmatic Breathing (Belly Breathing)",
                description="Place one hand on your chest, one on your belly. Breathe in deeply through your nose, letting your belly expand (not your chest). Breathe out slowly through your mouth. Feel the grounding effect.",
                duration="5-10 minutes",
                location_adaptations={
                    "home_indoor": "Lie down on your back with knees bent, or sit comfortably.",
                    "outdoor": "Lie on grass or sit on a bench.",
                    "office": "Sit in your chair, both feet on the ground.",
                    "public_place": "Sit comfortably, can be done very discreetly.",
                    "vehicle": "Passengers can practice sitting upright."
                },
                benefits=["Grounds and centers", "Reduces overwhelm", "Activates relaxation response"],
                cautions=["Don't force belly expansion", "Keep breath natural"]
            ),

            EmotionalState.DEPRESSION: PranayamaRecommendation(
                name="Bhastrika Pranayama (Bellows Breath)",
                description="Take a deep breath in. Exhale forcefully through your nose while pulling your belly in. Immediately inhale forcefully, expanding the belly. Continue this rapid, rhythmic breathing for 10-20 rounds, then breathe normally.",
                duration="3-5 rounds with rest",
                location_adaptations={
                    "home_indoor": "Sit with spine straight, practice with vigor.",
                    "outdoor": "Energizing in fresh air and sunlight.",
                    "office": "Can be done seated, but might draw attention due to sound.",
                    "public_place": "Find a private spot, can be loud.",
                    "vehicle": "Not recommended - requires stability."
                },
                benefits=["Energizes body and mind", "Lifts heavy emotions", "Increases vitality"],
                cautions=["Avoid if pregnant, high BP, or heart issues", "Stop if dizzy"]
            ),

            EmotionalState.CONFUSION: PranayamaRecommendation(
                name="Simple Breath Awareness",
                description="Close your eyes. Observe your natural breath without changing it. Notice the air entering and leaving your nostrils. When the mind wanders, gently bring it back to the breath. Allow clarity to emerge.",
                duration="5-15 minutes",
                location_adaptations={
                    "home_indoor": "Sit in a quiet space, spine straight.",
                    "outdoor": "Perfect for nature settings, very calming.",
                    "office": "Very discreet, can be done at desk.",
                    "public_place": "Can be practiced anywhere quietly.",
                    "vehicle": "Safe for passengers."
                },
                benefits=["Brings mental clarity", "Calms racing thoughts", "Centers awareness"],
                cautions=["No major cautions"]
            ),

            EmotionalState.LONELINESS: PranayamaRecommendation(
                name="Heart-Centered Breathing",
                description="Place your hand on your heart. Breathe in imagining warmth and light filling your heart. Breathe out, sending that warmth to yourself and others. Feel connection with all beings through the breath.",
                duration="5-10 minutes",
                location_adaptations={
                    "home_indoor": "Sit or lie down in a comfortable space.",
                    "outdoor": "Beautiful in nature, feeling connected to all life.",
                    "office": "Gentle and discreet, can be done at desk.",
                    "public_place": "Subtle hand on heart, internal visualization.",
                    "vehicle": "Passenger seat works well."
                },
                benefits=["Reduces feelings of isolation", "Builds self-compassion", "Opens the heart"],
                cautions=["Be gentle with yourself"]
            ),

            EmotionalState.GUILT: PranayamaRecommendation(
                name="Ujjayi Breath (Ocean Breath) with Forgiveness",
                description="Slightly constrict the back of your throat. Breathe in and out through your nose, creating a soft ocean sound. With each exhale, release guilt and shame. With each inhale, welcome forgiveness and peace.",
                duration="5-10 minutes",
                location_adaptations={
                    "home_indoor": "Sit comfortably with eyes closed.",
                    "outdoor": "The ocean sound blends beautifully with nature.",
                    "office": "Keep the sound very soft so it's discreet.",
                    "public_place": "Practice quietly.",
                    "vehicle": "Good for passengers."
                },
                benefits=["Releases emotional burdens", "Cultivates self-forgiveness", "Calming"],
                cautions=["Keep throat relaxation gentle"]
            ),

            # Default pranayama for other states
            EmotionalState.UNKNOWN: PranayamaRecommendation(
                name="Natural Deep Breathing",
                description="Breathe in slowly through your nose for a count of 4. Hold gently for 4. Breathe out through your nose for 6. Pause for 2. Repeat.",
                duration="5-10 minutes",
                location_adaptations={
                    "home_indoor": "Sit comfortably anywhere.",
                    "outdoor": "Wonderful in fresh air.",
                    "office": "Very discreet.",
                    "public_place": "Can be done anywhere.",
                    "vehicle": "Safe for passengers."
                },
                benefits=["Calms the nervous system", "Brings present moment awareness", "Universally beneficial"],
                cautions=["Don't force the breath"]
            ),
        }

        # Get specific pranayama or default
        pranayama = pranayama_map.get(emotion, pranayama_map[EmotionalState.UNKNOWN])

        return pranayama


class AsanaLibrary:
    """Library of yoga asanas mapped to emotional states and locations"""

    @staticmethod
    def get_for_emotion(emotion: EmotionalState, location: UserLocation) -> AsanaRecommendation:
        """Get appropriate asana for emotion and location"""

        # Map emotions to asanas
        asana_map = {
            EmotionalState.FEAR: AsanaRecommendation(
                name="Child's Pose (Balasana)",
                description="Kneel on the floor. Sit back on your heels. Fold forward, bringing your forehead to the ground. Extend your arms forward or alongside your body. Breathe deeply, feeling safe and grounded.",
                duration="3-5 minutes",
                location_adaptations={
                    "home_indoor": "Use a yoga mat or soft carpet. Place a cushion under your forehead if needed.",
                    "outdoor": "Find a grassy area or use a mat/towel.",
                    "office": "If you have private space, you can do a seated variation leaning forward on your desk.",
                    "public_place": "Find a quiet, private area or skip this one.",
                    "vehicle": "Not suitable for vehicle."
                },
                benefits=["Deeply calming", "Grounds fear", "Safe surrender"],
                modifications=["Place cushion between thighs and calves if knees are tight", "Widen knees if pregnant"]
            ),

            EmotionalState.ANGER: AsanaRecommendation(
                name="Standing Forward Fold (Uttanasana)",
                description="Stand with feet hip-width apart. Hinge at your hips and fold forward, letting your head hang heavy. Bend your knees generously. Hold opposite elbows and sway gently side to side. Let anger drain out through your head.",
                duration="2-3 minutes",
                location_adaptations={
                    "home_indoor": "Stand on a mat or soft surface.",
                    "outdoor": "Wonderful in fresh air, very grounding.",
                    "office": "Can be done in a private space or even at your desk (seated forward fold).",
                    "public_place": "Find a quiet corner.",
                    "vehicle": "Not suitable."
                },
                benefits=["Releases tension", "Calms the mind", "Cools anger"],
                modifications=["Keep knees bent to protect lower back", "Place hands on chair or desk for support"]
            ),

            EmotionalState.OVERWHELMED: AsanaRecommendation(
                name="Legs Up the Wall (Viparita Karani)",
                description="Lie on your back with your hips close to a wall. Extend your legs up the wall. Arms rest by your sides, palms up. Close your eyes and breathe. Stay for 5-15 minutes. Feel the overwhelm draining away.",
                duration="5-15 minutes",
                location_adaptations={
                    "home_indoor": "Perfect for home - use a wall, put a pillow under your hips for comfort.",
                    "outdoor": "Use a tree or fence if available and private.",
                    "office": "Only if you have a private space.",
                    "public_place": "Not suitable.",
                    "vehicle": "Not suitable."
                },
                benefits=["Deeply restorative", "Calms nervous system", "Relieves overwhelm"],
                modifications=["Place cushion under hips for comfort", "Can bend knees if hamstrings are tight"]
            ),

            EmotionalState.DEPRESSION: AsanaRecommendation(
                name="Sun Salutations (Surya Namaskar) - Simplified",
                description="Stand tall. Raise arms overhead (inhale). Fold forward (exhale). Step back to plank. Lower down gently. Cobra or upward dog (inhale). Downward dog (exhale). Step forward, fold. Rise up, arms overhead. Return to standing. Repeat 3-5 rounds.",
                duration="5-10 minutes (3-5 rounds)",
                location_adaptations={
                    "home_indoor": "Use a yoga mat for comfort.",
                    "outdoor": "Energizing in the sunshine!",
                    "office": "Need private space and room to move.",
                    "public_place": "Only if you have a suitable area (park, quiet corner).",
                    "vehicle": "Not suitable."
                },
                benefits=["Energizes body and mind", "Uplifts mood", "Full body movement"],
                modifications=["Go at your own pace", "Modify poses as needed", "Can do gentle version"]
            ),

            EmotionalState.CONFUSION: AsanaRecommendation(
                name="Tree Pose (Vrksasana)",
                description="Stand on one leg. Place the sole of your other foot on your inner thigh or calf (not on knee). Bring palms together at your heart or raise arms overhead. Find a focal point. Balance for 30 seconds to 1 minute each side. Feel clarity emerge.",
                duration="1-2 minutes each side",
                location_adaptations={
                    "home_indoor": "Stand near a wall for support if needed.",
                    "outdoor": "Grounding to practice on earth or grass.",
                    "office": "Can be done in a small space.",
                    "public_place": "Suitable if you have space.",
                    "vehicle": "Not suitable."
                },
                benefits=["Brings focus and clarity", "Improves concentration", "Grounds the mind"],
                modifications=["Hold a wall or chair for balance", "Place foot lower on leg if needed"]
            ),

            EmotionalState.LONELINESS: AsanaRecommendation(
                name="Heart Opening Pose (Supported Fish Pose)",
                description="Lie on your back with a bolster or rolled blanket under your upper back. Let your heart lift. Arms rest out to the sides, palms up. Close your eyes. Breathe into your heart space. Feel openness and connection.",
                duration="5-10 minutes",
                location_adaptations={
                    "home_indoor": "Use a bolster, pillows, or rolled blanket/towels.",
                    "outdoor": "Can use a rolled mat or towel on grass.",
                    "office": "Only in private space.",
                    "public_place": "Not suitable.",
                    "vehicle": "Not suitable."
                },
                benefits=["Opens the heart", "Releases loneliness", "Promotes self-love"],
                modifications=["Adjust height of support for comfort", "Place blanket under head if needed"]
            ),

            EmotionalState.GUILT: AsanaRecommendation(
                name="Seated Twist (Ardha Matsyendrasana)",
                description="Sit with legs extended. Bend right knee, place right foot outside left thigh. Twist to the right, left elbow outside right knee. Right hand behind you. Breathe, gently twisting and releasing. Switch sides. Feel release of stuck emotions.",
                duration="1-2 minutes each side",
                location_adaptations={
                    "home_indoor": "Sit on a mat or folded blanket.",
                    "outdoor": "Can be done on grass or bench.",
                    "office": "Can do a chair variation - sit sideways on chair and twist.",
                    "public_place": "Bench variation works.",
                    "vehicle": "Gentle seated twist possible in passenger seat."
                },
                benefits=["Releases emotional tension", "Detoxifying", "Promotes letting go"],
                modifications=["Keep bottom leg straight if the full pose is uncomfortable", "Use chair for support"]
            ),

            # Default for unknown/other states
            EmotionalState.UNKNOWN: AsanaRecommendation(
                name="Cat-Cow Stretch (Marjaryasana-Bitilasana)",
                description="Come to hands and knees (tabletop). Inhale, arch your back, lift your heart (Cow). Exhale, round your spine, tuck your chin (Cat). Flow between these poses with your breath. Move slowly and mindfully.",
                duration="3-5 minutes",
                location_adaptations={
                    "home_indoor": "Use a yoga mat or soft carpet.",
                    "outdoor": "Use a mat or towel on grass.",
                    "office": "Need floor space and privacy.",
                    "public_place": "Only if suitable space available.",
                    "vehicle": "Not suitable."
                },
                benefits=["Gentle spinal mobility", "Calming and centering", "Good for everyone"],
                modifications=["Place cushion under knees", "Can do seated variation in chair"]
            ),
        }

        asana = asana_map.get(emotion, asana_map[EmotionalState.UNKNOWN])

        return asana


class ActivityLibrary:
    """Library of age-appropriate activities and jokes"""

    @staticmethod
    def get_for_profile(
        emotion: EmotionalState,
        age: Optional[int],
        tone: str
    ) -> ActivitySuggestion:
        """Get appropriate activity/joke based on profile"""

        # Determine age bracket
        if age and age < 18:
            age_bracket = "youth"
        elif age and age < 35:
            age_bracket = "young_adult"
        elif age and age < 60:
            age_bracket = "adult"
        else:
            age_bracket = "senior"

        # Somber tone - no jokes, gentle reflection
        if tone == "somber":
            return ActivitySuggestion(
                content="Take a moment today to write down one thing you're grateful for, even in this difficult time. Small gratitudes can be anchors of light.",
                activity_type="reflection",
                age_appropriate=True,
                tone="somber"
            )

        # Playful/warm tones - jokes and activities
        jokes_by_emotion = {
            EmotionalState.FEAR: {
                "youth": "Remember: Worrying is like a rocking chair. It gives you something to do, but doesn't get you anywhere! Try this: make your fear into a cartoon character - what would it look like? Would it have a funny voice? 😄",
                "young_adult": "Fun challenge: Every time a worry pops up today, counter it with 'Yeah, but what if everything works out perfectly?' Keep score of which side wins!",
                "adult": "Light practice: Write your biggest worry on a piece of paper. Now fold it into a paper airplane and launch it! (Seriously, try it - it's oddly therapeutic!) ✈️",
                "senior": "Gentle reminder: You've faced fears before and you're still here. That's pretty amazing. Today, smile at one worry and say 'Hello old friend, you don't scare me anymore.'"
            },
            EmotionalState.ANGER: {
                "youth": "Anger burn-off game: Do 10 jumping jacks. Still angry? Do 10 more! Keep going until you're laughing at yourself. Sometimes the best way to process anger is to literally shake it off! 💪",
                "young_adult": "Try this: Imagine your anger is a song. What genre would it be? Death metal? Heavy bass? Now imagine it as elevator music. Notice how your anger doesn't know what to do with itself! 🎵",
                "adult": "Practical tip: Write an angry letter to whoever/whatever upset you. Be completely honest. Then tear it up dramatically! Bonus points for throwing confetti after. You deserve a celebration for processing that emotion!",
                "senior": "Wisdom activity: Today, when you feel irritation rising, pause and ask: 'Will this matter in 5 years?' If yes, address it wisely. If no, maybe it's time to chuckle and let it go."
            },
            EmotionalState.OVERWHELMED: {
                "youth": "Overwhelm buster: Pick THREE things max to do today. Just three. Everything else can wait. Then reward yourself with something nice after each one! 🎁",
                "young_adult": "Try the 'Swiss Cheese' method: Don't try to finish everything. Just poke holes in your tasks - do 5 minutes here, 10 minutes there. Before you know it, tasks are done!",
                "adult": "Give yourself permission to say this magic word today: 'NO.' Practice in the mirror if needed. 'No, I can't take that on right now.' Feels good, doesn't it? 😊",
                "senior": "Gentle reminder: There's no medal for doing everything. But there's deep peace in doing what matters. Today, do less, enjoy more."
            },
        }

        # Get joke for emotion and age
        emotion_jokes = jokes_by_emotion.get(emotion, {})
        joke = emotion_jokes.get(age_bracket, "Here's a gentle reminder: This too shall pass. And you're doing better than you think. Really. 🌟")

        # If no specific joke, use a default warm activity
        if not joke or joke.startswith("Here's a gentle reminder"):
            default_activities = [
                "Today's micro-practice: Smile at yourself in the mirror for 10 seconds. Yes, really. No judgment, just a genuine smile to yourself. You might be surprised what happens! 😊",
                "Fun challenge: Find one thing today that makes you laugh. A meme, a video, a memory. Laughter is medicine, and you get to choose your dose!",
                "Gentle nudge: Do one small thing today that your future self will thank you for. Drink a glass of water? Take a 5-minute walk? You got this! 💪",
            ]
            joke = default_activities[hash(str(age) + emotion.value) % len(default_activities)]

        return ActivitySuggestion(
            content=joke,
            activity_type="game" if "game:" in joke.lower() or "challenge:" in joke.lower() else "playful_reminder",
            age_appropriate=True,
            tone=tone
        )


class SolutionGenerator:
    """Main solution generator - creates 4-part holistic solutions"""

    @staticmethod
    def generate(
        emotion: EmotionalState,
        situation: LifeSituation,
        location: UserLocation,
        age: Optional[int],
        tone: str,
        user_name: str,
        wisdom_text: str,  # Provided by Wisdom Agent after retrieval
        pranayama_text: Optional[str] = None,  # From Practice Agent (preferred)
        asana_text: Optional[str] = None  # From Practice Agent (preferred)
    ) -> HolisticSolution:
        """
        Generate complete 4-part solution.

        Args:
            emotion: User's predominant emotion
            situation: Life situation causing distress
            location: Physical location for practice adaptation
            age: User's age
            tone: Tone to use (warm, somber, playful)
            user_name: User's name for personalization
            wisdom_text: Verbatim wisdom from Knowledge Sheets
            pranayama_text: Pranayama from Practice Agent (if None, uses hardcoded)
            asana_text: Asana from Practice Agent (if None, uses hardcoded)

        Returns:
            HolisticSolution with all four parts
        """

        # 1. Get Pranayama
        # Use Practice Agent recommendation if available, otherwise fallback to hardcoded
        if pranayama_text:
            logger.info("Using pranayama from Practice Agent (retrieved from knowledge base)")
            pranayama = PranayamaRecommendation(
                name="Pranayama Practice",
                description=pranayama_text,
                duration="5-10 minutes",
                location_adaptations={},
                benefits=["Based on your current emotional state"],
                cautions=[]
            )
        else:
            logger.info("Using hardcoded pranayama (Practice Agent not available)")
            pranayama = PranayamaLibrary.get_for_emotion(emotion, location)

        # 2. Get Asana
        # Use Practice Agent recommendation if available, otherwise fallback to hardcoded
        if asana_text:
            logger.info("Using asana from Practice Agent (retrieved from knowledge base)")
            asana = AsanaRecommendation(
                name="Yoga Asana Practice",
                description=asana_text,
                duration="10-15 minutes",
                location_adaptations={},
                benefits=["Based on your current emotional state"],
                modifications=[]
            )
        else:
            logger.info("Using hardcoded asana (Practice Agent not available)")
            asana = AsanaLibrary.get_for_emotion(emotion, location)

        # 3. Wisdom is provided (verbatim from retrieval)
        # wisdom_text parameter

        # 4. Get Activity/Joke
        activity = ActivityLibrary.get_for_profile(emotion, age, tone)

        # Create personalized intro
        emotion_text = emotion.value.replace('_', ' ')
        situation_text = situation.value.replace('_', ' ')

        if tone == "somber":
            intro = f"Dear {user_name}, I'm here with you in this difficult time. Here's what might help bring some peace:"
        else:
            intro = f"{user_name}, I hear that you're experiencing {emotion_text} around {situation_text}. Here's a complete practice to help you find balance:"

        return HolisticSolution(
            pranayama=pranayama,
            asana=asana,
            wisdom=wisdom_text,
            activity=activity,
            personalized_intro=intro,
            tone=tone
        )

    @staticmethod
    def format_solution(solution: HolisticSolution, location: UserLocation) -> str:
        """
        Format the solution into a beautiful, readable text response.

        Returns formatted 4-part solution text.
        """

        location_key = location.value

        output = f"""{solution.personalized_intro}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌬️ **PART 1: PRANAYAMA (Breathing Practice)**

**{solution.pranayama.name}**

{solution.pranayama.description}

**Duration:** {solution.pranayama.duration}

**For your location ({location_key.replace('_', ' ')}):**
{solution.pranayama.location_adaptations.get(location_key, solution.pranayama.location_adaptations.get('home_indoor'))}

**Benefits:** {', '.join(solution.pranayama.benefits)}

{f"**Cautions:** {', '.join(solution.pranayama.cautions)}" if solution.pranayama.cautions else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧘 **PART 2: ASANA (Yoga Practice)**

**{solution.asana.name}**

{solution.asana.description}

**Duration:** {solution.asana.duration}

**For your location ({location_key.replace('_', ' ')}):**
{solution.asana.location_adaptations.get(location_key, solution.asana.location_adaptations.get('home_indoor'))}

**Benefits:** {', '.join(solution.asana.benefits)}

**Modifications:** {', '.join(solution.asana.modifications)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📿 **PART 3: WISDOM FROM GURUDEV**

{solution.wisdom}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ **PART 4: PRACTICE THIS WISDOM**

{solution.activity.content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Remember: You don't have to do everything at once. Start with what feels right to you. Even small steps create big shifts. 🙏
"""

        return output


# For testing
if __name__ == "__main__":
    print("Solution Generator Module - Ready to create holistic 4-part solutions")

    # Test generation
    test_solution = SolutionGenerator.generate(
        emotion=EmotionalState.FEAR,
        situation=LifeSituation.DECISION_MAKING,
        location=UserLocation.HOME_INDOOR,
        age=28,
        tone="warm",
        user_name="Sarah",
        wisdom_text="The cause of distress is set concepts in the mind that things should be a certain way. Train the mind to live in the present moment. Drop the stress that you are carrying for nothing. - Gurudev"
    )

    formatted = SolutionGenerator.format_solution(test_solution, UserLocation.HOME_INDOOR)
    print("\n" + "="*60)
    print("SAMPLE SOLUTION:")
    print("="*60)
    print(formatted)
