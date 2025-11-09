"""
Actionable Step Detection
=========================

Detects and extracts actionable spiritual practices from wisdom agent responses.

When the wisdom agent provides guidance with specific actionable steps
(like "Spend 10-15 minutes each morning in quiet breath-awareness"),
this module detects them and formats them as practice recommendations
so users can log and schedule them.
"""

import re
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class ActionableStepDetector:
    """
    Detects actionable practice steps in wisdom responses.
    
    Looks for patterns like:
    - "Spend X minutes doing Y"
    - "Practice Z each morning"
    - "Try this technique: ..."
    - Numbered/bulleted instructions
    """
    
    # Patterns that indicate actionable steps
    ACTIONABLE_PATTERNS = [
        r'spend\s+\d+-?\d*\s+minutes',
        r'practice\s+\w+\s+(each|every|daily)',
        r'try\s+(this|these)\s+(practice|technique|exercise)',
        r'actionable\s+step:',
        r'here\'s\s+what\s+to\s+do:',
        r'follow\s+these\s+steps:',
        r'simple\s+practice:',
    ]
    
    # Duration extraction patterns
    DURATION_PATTERNS = [
        r'(\d+)-(\d+)\s+minutes',  # "10-15 minutes"
        r'(\d+)\s+minutes',         # "15 minutes"
        r'(\d+)\s+min',             # "15 min"
    ]
    
    def __init__(self):
        """Initialize the detector"""
        pass
    
    def detect_actionable_step(self, wisdom_response: str) -> Optional[Dict[str, Any]]:
        """
        Detect if wisdom response contains an actionable practice step.
        
        Args:
            wisdom_response: Response text from wisdom agent
        
        Returns:
            Extracted practice data or None if no actionable step found
        """
        # Check for actionable patterns
        has_actionable = False
        for pattern in self.ACTIONABLE_PATTERNS:
            if re.search(pattern, wisdom_response, re.IGNORECASE):
                has_actionable = True
                break
        
        if not has_actionable:
            return None
        
        # Extract practice details
        practice_name = self._extract_practice_name(wisdom_response)
        duration = self._extract_duration(wisdom_response)
        instructions = self._extract_instructions(wisdom_response)
        
        if not practice_name or not instructions:
            return None
        
        # Build practice recommendation
        practice = {
            'practice_id': 'actionable_step',
            'name': practice_name,
            'practice_type': 'actionable_step',
            'description': self._extract_description(wisdom_response),
            'instructions': instructions,
            'duration_minutes': duration,
            'difficulty': 'beginner',
            'benefits': self._extract_benefits(wisdom_response),
            'source': 'wisdom_agent'
        }
        
        logger.info(f"Detected actionable step: {practice_name}")
        return practice
    
    def _extract_practice_name(self, text: str) -> Optional[str]:
        """Extract practice name from text"""
        # Look for common patterns
        patterns = [
            r'practice[:\s]+([^.!?\n]+)',
            r'try[:\s]+([^.!?\n]+)',
            r'technique[:\s]+([^.!?\n]+)',
            r'exercise[:\s]+([^.!?\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up
                name = re.sub(r'\s+', ' ', name)
                # Truncate if too long
                if len(name) > 100:
                    name = name[:97] + '...'
                return name
        
        # Fallback: extract from actionable step section
        actionable_match = re.search(
            r'actionable\s+step[:\s]+([^.!?\n]+)',
            text,
            re.IGNORECASE
        )
        if actionable_match:
            return actionable_match.group(1).strip()
        
        # Default name
        return "Guided Practice from Wisdom"
    
    def _extract_duration(self, text: str) -> int:
        """Extract practice duration in minutes"""
        for pattern in self.DURATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:  # Range like "10-15"
                    # Use the average
                    min_dur = int(match.group(1))
                    max_dur = int(match.group(2))
                    return (min_dur + max_dur) // 2
                else:  # Single value
                    return int(match.group(1))
        
        # Default duration
        return 15
    
    def _extract_description(self, text: str) -> str:
        """Extract practice description (first sentence or two)"""
        # Get first 200 characters up to a sentence end
        desc = text[:200]
        
        # Find last sentence end
        last_period = desc.rfind('.')
        if last_period > 50:
            desc = desc[:last_period + 1]
        
        return desc.strip()
    
    def _extract_instructions(self, text: str) -> str:
        """Extract detailed instructions"""
        # Look for instruction sections
        instruction_markers = [
            r'actionable\s+step[:\s]+(.*?)(?=\n\n|$)',
            r'here\'s\s+what\s+to\s+do[:\s]+(.*?)(?=\n\n|$)',
            r'practice[:\s]+(.*?)(?=\n\n|$)',
            r'steps?[:\s]+(.*?)(?=\n\n|$)',
        ]
        
        for marker in instruction_markers:
            match = re.search(marker, text, re.IGNORECASE | re.DOTALL)
            if match:
                instructions = match.group(1).strip()
                # Clean up
                instructions = re.sub(r'\s+', ' ', instructions)
                return instructions
        
        # Fallback: return full text
        return text
    
    def _extract_benefits(self, text: str) -> List[str]:
        """Extract mentioned benefits"""
        benefits = []
        
        # Look for benefit keywords
        benefit_keywords = [
            'calm', 'peace', 'clarity', 'focus', 'awareness',
            'relaxation', 'mindfulness', 'presence', 'wisdom',
            'insight', 'understanding', 'growth', 'healing'
        ]
        
        text_lower = text.lower()
        for keyword in benefit_keywords:
            if keyword in text_lower:
                benefits.append(f"Enhances {keyword}")
        
        # Limit to top 3
        return benefits[:3] if benefits else ["Spiritual growth"]


def create_practice_from_actionable_step(
    wisdom_response: str
) -> Optional[Dict[str, Any]]:
    """
    Convenience function to detect and create practice from wisdom response.
    
    Args:
        wisdom_response: Text from wisdom agent
    
    Returns:
        Practice recommendation dict or None
    """
    detector = ActionableStepDetector()
    return detector.detect_actionable_step(wisdom_response)


def format_actionable_step_for_logging(
    practice: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Format actionable step as a loggable practice recommendation.
    
    Args:
        practice: Detected actionable step
    
    Returns:
        Formatted as practice recommendation
    """
    return {
        'primary_practice': practice,
        'alternatives': [],
        'customized_instructions': practice.get('instructions', ''),
        'reasoning': 'This practice was recommended based on spiritual wisdom and guidance.',
        'expected_benefits': practice.get('benefits', []),
        'preparation_tips': [
            'Find a quiet space',
            'Set aside uninterrupted time',
            'Approach with an open heart'
        ],
        'contraindication_warnings': [],
        'confidence': 0.75
    }
