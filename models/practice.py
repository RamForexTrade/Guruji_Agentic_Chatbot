"""
Practice Log Data Model
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class PracticeLog:
    """
    Practice log data model
    Tracks user's practice completions and feedback
    """
    log_id: str
    user_id: str
    practice_name: str
    practice_type: str  # pranayama, meditation, yoga, therapy, etc.
    duration_minutes: Optional[int] = None
    completed: bool = True
    feedback: Optional[str] = None
    rating: Optional[int] = None  # 1-5 scale
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Set default timestamp if not provided"""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # Validate rating
        if self.rating is not None and (self.rating < 1 or self.rating > 5):
            raise ValueError("Rating must be between 1 and 5")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert practice log to dictionary"""
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'practice_name': self.practice_name,
            'practice_type': self.practice_type,
            'duration_minutes': self.duration_minutes,
            'completed': self.completed,
            'feedback': self.feedback,
            'rating': self.rating,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PracticeLog':
        """Create PracticeLog from dictionary"""
        # Convert string timestamp back to datetime
        if data.get('timestamp') and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return cls(**data)
    
    def get_display_date(self) -> str:
        """Get formatted display date"""
        if not self.timestamp:
            return ""
        
        return self.timestamp.strftime("%B %d, %Y at %I:%M %p")
    
    def get_short_date(self) -> str:
        """Get short date format"""
        if not self.timestamp:
            return ""
        
        return self.timestamp.strftime("%m/%d/%Y")
    
    def get_rating_stars(self) -> str:
        """Get star representation of rating"""
        if not self.rating:
            return "No rating"
        
        full_stars = "⭐" * self.rating
        empty_stars = "☆" * (5 - self.rating)
        return full_stars + empty_stars
    
    def is_recent(self, hours: int = 24) -> bool:
        """Check if practice was done recently"""
        if not self.timestamp:
            return False
        
        age = datetime.now() - self.timestamp
        return age.total_seconds() < (hours * 3600)
    
    def __repr__(self) -> str:
        return f"PracticeLog(practice='{self.practice_name}', type='{self.practice_type}', completed={self.completed})"


@dataclass
class PracticeStatistics:
    """
    Practice statistics for a user
    """
    total_practices: int = 0
    completed_practices: int = 0
    adherence_rate: float = 0.0
    total_duration_minutes: int = 0
    average_rating: float = 0.0
    practice_type_breakdown: Dict[str, int] = None
    period_days: int = 30
    
    def __post_init__(self):
        if self.practice_type_breakdown is None:
            self.practice_type_breakdown = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary"""
        return {
            'total_practices': self.total_practices,
            'completed_practices': self.completed_practices,
            'adherence_rate': self.adherence_rate,
            'total_duration_minutes': self.total_duration_minutes,
            'total_duration_hours': round(self.total_duration_minutes / 60, 1),
            'average_rating': self.average_rating,
            'practice_type_breakdown': self.practice_type_breakdown,
            'period_days': self.period_days
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PracticeStatistics':
        """Create PracticeStatistics from dictionary"""
        # Remove computed fields
        data.pop('total_duration_hours', None)
        return cls(**data)
    
    def get_most_practiced_type(self) -> Optional[str]:
        """Get the most frequently practiced type"""
        if not self.practice_type_breakdown:
            return None
        
        return max(self.practice_type_breakdown, 
                  key=self.practice_type_breakdown.get)
    
    def get_adherence_level(self) -> str:
        """Get adherence level description"""
        if self.adherence_rate >= 80:
            return "Excellent 🏆"
        elif self.adherence_rate >= 60:
            return "Good 👍"
        elif self.adherence_rate >= 40:
            return "Fair 📊"
        else:
            return "Needs Improvement 💪"
    
    def get_summary_text(self) -> str:
        """Get human-readable summary"""
        parts = [
            f"Total Practices: {self.completed_practices}/{self.total_practices}",
            f"Adherence Rate: {self.adherence_rate}%",
            f"Total Time: {round(self.total_duration_minutes / 60, 1)} hours",
        ]
        
        if self.average_rating > 0:
            parts.append(f"Average Rating: {self.average_rating:.1f}/5.0")
        
        most_practiced = self.get_most_practiced_type()
        if most_practiced:
            parts.append(f"Most Practiced: {most_practiced}")
        
        return "\n".join(parts)
    
    def __repr__(self) -> str:
        return f"PracticeStatistics(total={self.total_practices}, adherence={self.adherence_rate}%)"
