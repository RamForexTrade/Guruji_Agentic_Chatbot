"""
Google Calendar Integration for Practice Scheduling
===================================================

This module provides Google Calendar integration for scheduling and managing
spiritual practices with reminders.

Features:
- OAuth2 authentication flow
- Create calendar events for practices
- Set reminders (15 min, 1 hour, 1 day before)
- Recurring practice schedules
- View upcoming practices
- Update/cancel scheduled practices

Setup Instructions:
1. Enable Google Calendar API in Google Cloud Console
2. Create OAuth2 credentials
3. Download client_secrets.json
4. Place in project root
5. Add to .env: GOOGLE_CALENDAR_ENABLED=true
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleCalendarIntegration:
    """
    Google Calendar integration for practice scheduling.
    
    Handles authentication, event creation, and calendar management
    for scheduling spiritual practices.
    """
    
    # OAuth2 scopes needed
    SCOPES = ['https://www.googleapis.com/auth/calendar.events']
    
    def __init__(
        self,
        credentials_path: str = "token.pickle",
        client_secrets_path: str = "client_secrets.json"
    ):
        """
        Initialize Google Calendar integration.
        
        Args:
            credentials_path: Path to stored credentials
            client_secrets_path: Path to OAuth2 client secrets
        """
        self.credentials_path = credentials_path
        self.client_secrets_path = client_secrets_path
        self.service = None
        self.creds = None
        
    def authenticate(self, user_id: str) -> bool:
        """
        Authenticate with Google Calendar.
        
        Args:
            user_id: User identifier for storing credentials
        
        Returns:
            True if authenticated successfully
        """
        try:
            # User-specific credentials path
            user_creds_path = f"{self.credentials_path}_{user_id}"
            
            # Load existing credentials
            if os.path.exists(user_creds_path):
                with open(user_creds_path, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # Refresh if expired
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            
            # Initialize service
            if self.creds and self.creds.valid:
                self.service = build('calendar', 'v3', credentials=self.creds)
                logger.info(f"Google Calendar authenticated for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def get_auth_url(self, user_id: str) -> Optional[str]:
        """
        Get OAuth2 authorization URL for user.
        
        Args:
            user_id: User identifier
        
        Returns:
            Authorization URL or None if error
        """
        try:
            if not os.path.exists(self.client_secrets_path):
                logger.error("client_secrets.json not found")
                return None
            
            flow = Flow.from_client_secrets_file(
                self.client_secrets_path,
                scopes=self.SCOPES,
                redirect_uri='http://localhost:8501'  # Streamlit default
            )
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=user_id
            )
            
            return auth_url
            
        except Exception as e:
            logger.error(f"Error generating auth URL: {e}")
            return None
    
    def handle_oauth_callback(self, authorization_response: str, user_id: str) -> bool:
        """
        Handle OAuth2 callback and store credentials.
        
        Args:
            authorization_response: Full callback URL
            user_id: User identifier
        
        Returns:
            True if successful
        """
        try:
            logger.info(f"Starting OAuth callback for user {user_id}")
            logger.info(f"Authorization response URL: {authorization_response}")
            
            # Create flow with exact same redirect_uri
            flow = Flow.from_client_secrets_file(
                self.client_secrets_path,
                scopes=self.SCOPES,
                redirect_uri='http://localhost:8501'
            )
            
            logger.info("Fetching token from authorization response...")
            flow.fetch_token(authorization_response=authorization_response)
            self.creds = flow.credentials
            logger.info("Token fetched successfully")
            
            # Save credentials
            user_creds_path = f"{self.credentials_path}_{user_id}"
            with open(user_creds_path, 'wb') as token:
                pickle.dump(self.creds, token)
            logger.info(f"Credentials saved to {user_creds_path}")
            
            # Initialize service
            self.service = build('calendar', 'v3', credentials=self.creds)
            logger.info("Google Calendar service initialized")
            
            logger.info(f"OAuth completed for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"OAuth callback error: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def create_practice_event(
        self,
        practice_name: str,
        description: str,
        start_time: datetime,
        duration_minutes: int,
        reminders: List[int] = [15, 60, 1440],  # 15min, 1hr, 1day
        recurrence: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a calendar event for a practice.
        
        Args:
            practice_name: Name of the practice
            description: Practice description/instructions
            start_time: When to schedule the practice
            duration_minutes: Practice duration
            reminders: Reminder times in minutes before event
            recurrence: RFC5545 recurrence rule (e.g., "RRULE:FREQ=DAILY")
        
        Returns:
            Event ID if successful, None otherwise
        """
        if not self.service:
            logger.error("Not authenticated with Google Calendar")
            return None
        
        try:
            # Calculate end time
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Build event
            event = {
                'summary': f'🧘 {practice_name}',
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': m} for m in reminders
                    ],
                },
                'colorId': '9',  # Blue color for spiritual practices
            }
            
            # Add recurrence if specified
            if recurrence:
                event['recurrence'] = [recurrence]
            
            # Create event
            event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            logger.info(f"Created calendar event: {event['id']}")
            return event['id']
            
        except HttpError as e:
            logger.error(f"Calendar API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return None
    
    def get_upcoming_practices(
        self,
        days_ahead: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming practice events.
        
        Args:
            days_ahead: Number of days to look ahead
        
        Returns:
            List of practice events
        """
        if not self.service:
            logger.error("Not authenticated with Google Calendar")
            return []
        
        try:
            # Time range
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            # Get events
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
                q='🧘'  # Filter for practice events
            ).execute()
            
            events = events_result.get('items', [])
            
            # Format events
            practices = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                practices.append({
                    'id': event['id'],
                    'name': event['summary'].replace('🧘 ', ''),
                    'description': event.get('description', ''),
                    'start_time': start,
                    'link': event.get('htmlLink', '')
                })
            
            return practices
            
        except HttpError as e:
            logger.error(f"Calendar API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return []
    
    def update_practice_event(
        self,
        event_id: str,
        new_start_time: Optional[datetime] = None,
        new_duration: Optional[int] = None
    ) -> bool:
        """
        Update a scheduled practice event.
        
        Args:
            event_id: Google Calendar event ID
            new_start_time: New start time
            new_duration: New duration in minutes
        
        Returns:
            True if successful
        """
        if not self.service:
            logger.error("Not authenticated with Google Calendar")
            return False
        
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update start time
            if new_start_time:
                event['start']['dateTime'] = new_start_time.isoformat()
                
                # Update end time if duration provided
                if new_duration:
                    end_time = new_start_time + timedelta(minutes=new_duration)
                    event['end']['dateTime'] = end_time.isoformat()
            
            # Update event
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Updated calendar event: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Calendar API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return False
    
    def cancel_practice_event(self, event_id: str) -> bool:
        """
        Cancel a scheduled practice event.
        
        Args:
            event_id: Google Calendar event ID
        
        Returns:
            True if successful
        """
        if not self.service:
            logger.error("Not authenticated with Google Calendar")
            return False
        
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted calendar event: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Calendar API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        return self.service is not None


# Convenience functions for Streamlit app
def initialize_calendar(user_id: str) -> GoogleCalendarIntegration:
    """
    Initialize calendar integration for a user.
    
    Args:
        user_id: User identifier
    
    Returns:
        GoogleCalendarIntegration instance
    """
    calendar = GoogleCalendarIntegration()
    calendar.authenticate(user_id)
    return calendar


def format_practice_for_calendar(
    practice: Dict[str, Any],
    start_time: datetime
) -> Dict[str, Any]:
    """
    Format practice recommendation for calendar event.
    
    Args:
        practice: Practice data from PracticeAgent
        start_time: When to schedule
    
    Returns:
        Formatted event data
    """
    name = practice.get('name', 'Spiritual Practice')
    duration = practice.get('duration_minutes', 15)
    instructions = practice.get('instructions', '')
    benefits = practice.get('benefits', [])
    
    # Build description
    description = f"{instructions}\n\n"
    description += "Expected Benefits:\n"
    for benefit in benefits:
        description += f"• {benefit}\n"
    description += "\n🙏 From JAI GURU DEV AI Companion"
    
    return {
        'practice_name': name,
        'description': description,
        'start_time': start_time,
        'duration_minutes': duration
    }
