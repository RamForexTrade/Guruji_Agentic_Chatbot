"""
Database Management Module for JAI GURU DEV AI Chatbot
Handles all SQLite operations for user profiles, conversations, and practice logs
"""

import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import json
import os


class Database:
    """SQLite database manager for the chatbot"""
    
    def __init__(self, db_path: str = "database/guruji_bot.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with Row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Create all required tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    life_aspect TEXT,
                    emotional_state TEXT,
                    guidance_type TEXT,
                    specific_situation TEXT,
                    experience_level TEXT DEFAULT 'beginner',
                    preferences TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    message_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Practice logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS practice_logs (
                    log_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    practice_name TEXT NOT NULL,
                    practice_type TEXT,
                    duration_minutes INTEGER,
                    completed BOOLEAN DEFAULT TRUE,
                    feedback TEXT,
                    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferred_time TEXT,
                    reminder_frequency TEXT,
                    communication_style TEXT,
                    notification_enabled BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Sessions table (for tracking user sessions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
                ON conversations(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
                ON conversations(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_practice_logs_user_id 
                ON practice_logs(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_practice_logs_timestamp 
                ON practice_logs(timestamp)
            """)
            
            conn.commit()
            print("✅ Database initialized successfully")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error initializing database: {e}")
            raise
        finally:
            conn.close()
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, user_data: Dict) -> str:
        """
        Create a new user profile
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            user_id: Generated UUID for the user
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            user_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO users (
                    user_id, name, age, life_aspect, emotional_state,
                    guidance_type, specific_situation, experience_level, preferences
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                user_data.get('name', 'User'),
                user_data.get('age'),
                user_data.get('life_aspect', ''),
                user_data.get('emotional_state', ''),
                user_data.get('guidance_type', ''),
                user_data.get('specific_situation', ''),
                user_data.get('experience_level', 'beginner'),
                json.dumps(user_data.get('preferences', {}))
            ))
            
            conn.commit()
            print(f"✅ User created: {user_id}")
            return user_id
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error creating user: {e}")
            raise
        finally:
            conn.close()
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Retrieve user profile by ID
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User data as dictionary or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM users WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            
            if row:
                user_data = dict(row)
                # Parse JSON preferences
                if user_data.get('preferences'):
                    user_data['preferences'] = json.loads(user_data['preferences'])
                return user_data
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving user: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (for admin purposes)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT user_id, name, created_at, last_active 
                FROM users 
                ORDER BY last_active DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ Error retrieving users: {e}")
            return []
        finally:
            conn.close()
    
    def update_user(self, user_id: str, user_data: Dict):
        """
        Update user profile
        
        Args:
            user_id: User's unique identifier
            user_data: Dictionary with fields to update
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Build dynamic UPDATE query based on provided fields
            update_fields = []
            values = []
            
            allowed_fields = [
                'name', 'age', 'life_aspect', 'emotional_state',
                'guidance_type', 'specific_situation', 'experience_level'
            ]
            
            for field in allowed_fields:
                if field in user_data:
                    update_fields.append(f"{field} = ?")
                    values.append(user_data[field])
            
            if 'preferences' in user_data:
                update_fields.append("preferences = ?")
                values.append(json.dumps(user_data['preferences']))
            
            # Always update updated_at
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            if update_fields:
                values.append(user_id)
                query = f"""
                    UPDATE users 
                    SET {', '.join(update_fields)}
                    WHERE user_id = ?
                """
                cursor.execute(query, values)
                conn.commit()
                print(f"✅ User updated: {user_id}")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error updating user: {e}")
            raise
        finally:
            conn.close()
    
    def update_last_active(self, user_id: str):
        """Update user's last active timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE users 
                SET last_active = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()
        except Exception as e:
            print(f"❌ Error updating last active: {e}")
        finally:
            conn.close()
    
    # ==================== CONVERSATION OPERATIONS ====================
    
    def save_message(
        self, 
        user_id: str, 
        role: str, 
        content: str, 
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save a conversation message
        
        Args:
            user_id: User's unique identifier
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata dictionary
            
        Returns:
            message_id: Generated UUID for the message
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            message_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO conversations (message_id, user_id, role, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                message_id,
                user_id,
                role,
                content,
                json.dumps(metadata) if metadata else None
            ))
            
            conn.commit()
            return message_id
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error saving message: {e}")
            raise
        finally:
            conn.close()
    
    def get_conversation_history(
        self, 
        user_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Retrieve conversation history for a user
        
        Args:
            user_id: User's unique identifier
            limit: Maximum number of messages to retrieve
            offset: Number of messages to skip
            
        Returns:
            List of message dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT message_id, user_id, role, content, timestamp, metadata
                FROM conversations
                WHERE user_id = ?
                ORDER BY timestamp ASC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            
            rows = cursor.fetchall()
            messages = []
            
            for row in rows:
                msg = dict(row)
                # Parse metadata if exists
                if msg.get('metadata'):
                    msg['metadata'] = json.loads(msg['metadata'])
                messages.append(msg)
            
            return messages
            
        except Exception as e:
            print(f"❌ Error retrieving conversation history: {e}")
            return []
        finally:
            conn.close()
    
    def get_recent_conversations(
        self, 
        user_id: str, 
        days: int = 7
    ) -> List[Dict]:
        """Get conversations from the last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            since_date = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                SELECT message_id, user_id, role, content, timestamp, metadata
                FROM conversations
                WHERE user_id = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            """, (user_id, since_date))
            
            rows = cursor.fetchall()
            messages = []
            
            for row in rows:
                msg = dict(row)
                if msg.get('metadata'):
                    msg['metadata'] = json.loads(msg['metadata'])
                messages.append(msg)
            
            return messages
            
        except Exception as e:
            print(f"❌ Error retrieving recent conversations: {e}")
            return []
        finally:
            conn.close()
    
    def clear_conversation_history(self, user_id: str):
        """Delete all conversation history for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM conversations WHERE user_id = ?
            """, (user_id,))
            conn.commit()
            print(f"✅ Conversation history cleared for user: {user_id}")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error clearing conversation history: {e}")
            raise
        finally:
            conn.close()
    
    def get_message_count(self, user_id: str) -> int:
        """Get total message count for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) as count FROM conversations WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            return result['count'] if result else 0
            
        except Exception as e:
            print(f"❌ Error getting message count: {e}")
            return 0
        finally:
            conn.close()
    
    # ==================== PRACTICE LOG OPERATIONS ====================
    
    def log_practice(self, practice_data: Dict) -> str:
        """
        Log a practice completion
        
        Args:
            practice_data: Dictionary containing practice information
            
        Returns:
            log_id: Generated UUID for the log entry
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            log_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO practice_logs (
                    log_id, user_id, practice_name, practice_type,
                    duration_minutes, completed, feedback, rating
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_id,
                practice_data['user_id'],
                practice_data['practice_name'],
                practice_data.get('practice_type', ''),
                practice_data.get('duration_minutes'),
                practice_data.get('completed', True),
                practice_data.get('feedback', ''),
                practice_data.get('rating')
            ))
            
            conn.commit()
            print(f"✅ Practice logged: {practice_data['practice_name']}")
            return log_id
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error logging practice: {e}")
            raise
        finally:
            conn.close()
    
    def get_practice_logs(
        self, 
        user_id: str, 
        days: int = 30,
        practice_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve practice logs for a user
        
        Args:
            user_id: User's unique identifier
            days: Number of days to look back
            practice_type: Optional filter by practice type
            
        Returns:
            List of practice log dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            since_date = datetime.now() - timedelta(days=days)
            
            if practice_type:
                cursor.execute("""
                    SELECT * FROM practice_logs
                    WHERE user_id = ? AND timestamp >= ? AND practice_type = ?
                    ORDER BY timestamp DESC
                """, (user_id, since_date, practice_type))
            else:
                cursor.execute("""
                    SELECT * FROM practice_logs
                    WHERE user_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                """, (user_id, since_date))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ Error retrieving practice logs: {e}")
            return []
        finally:
            conn.close()
    
    def get_practice_statistics(self, user_id: str, days: int = 30) -> Dict:
        """
        Get practice statistics for a user
        
        Args:
            user_id: User's unique identifier
            days: Number of days to analyze
            
        Returns:
            Dictionary with statistics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            since_date = datetime.now() - timedelta(days=days)
            
            # Total practices
            cursor.execute("""
                SELECT COUNT(*) as total_practices
                FROM practice_logs
                WHERE user_id = ? AND timestamp >= ?
            """, (user_id, since_date))
            total = cursor.fetchone()['total_practices']
            
            # Completed practices
            cursor.execute("""
                SELECT COUNT(*) as completed_practices
                FROM practice_logs
                WHERE user_id = ? AND timestamp >= ? AND completed = 1
            """, (user_id, since_date))
            completed = cursor.fetchone()['completed_practices']
            
            # Total duration
            cursor.execute("""
                SELECT SUM(duration_minutes) as total_duration
                FROM practice_logs
                WHERE user_id = ? AND timestamp >= ? AND completed = 1
            """, (user_id, since_date))
            duration_result = cursor.fetchone()
            total_duration = duration_result['total_duration'] or 0
            
            # Average rating
            cursor.execute("""
                SELECT AVG(rating) as avg_rating
                FROM practice_logs
                WHERE user_id = ? AND timestamp >= ? AND rating IS NOT NULL
            """, (user_id, since_date))
            rating_result = cursor.fetchone()
            avg_rating = rating_result['avg_rating'] or 0
            
            # Practice type breakdown
            cursor.execute("""
                SELECT practice_type, COUNT(*) as count
                FROM practice_logs
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY practice_type
            """, (user_id, since_date))
            type_breakdown = {row['practice_type']: row['count'] 
                            for row in cursor.fetchall()}
            
            # Calculate adherence rate
            adherence_rate = (completed / total * 100) if total > 0 else 0
            
            return {
                'total_practices': total,
                'completed_practices': completed,
                'adherence_rate': round(adherence_rate, 2),
                'total_duration_minutes': total_duration,
                'average_rating': round(avg_rating, 2),
                'practice_type_breakdown': type_breakdown,
                'period_days': days
            }
            
        except Exception as e:
            print(f"❌ Error calculating practice statistics: {e}")
            return {
                'total_practices': 0,
                'completed_practices': 0,
                'adherence_rate': 0,
                'total_duration_minutes': 0,
                'average_rating': 0,
                'practice_type_breakdown': {},
                'period_days': days
            }
        finally:
            conn.close()
    
    def get_streak_days(self, user_id: str) -> int:
        """Calculate current practice streak (consecutive days)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT DATE(timestamp) as practice_date
                FROM practice_logs
                WHERE user_id = ? AND completed = 1
                GROUP BY DATE(timestamp)
                ORDER BY practice_date DESC
            """, (user_id,))
            
            dates = [row['practice_date'] for row in cursor.fetchall()]
            
            if not dates:
                return 0
            
            # Calculate streak
            streak = 1
            current_date = datetime.strptime(dates[0], '%Y-%m-%d').date()
            
            for date_str in dates[1:]:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                diff = (current_date - date).days
                
                if diff == 1:
                    streak += 1
                    current_date = date
                else:
                    break
            
            return streak
            
        except Exception as e:
            print(f"❌ Error calculating streak: {e}")
            return 0
        finally:
            conn.close()
    
    # ==================== SESSION OPERATIONS ====================
    
    def create_session(self, user_id: str) -> str:
        """Create a new session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            session_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO sessions (session_id, user_id)
                VALUES (?, ?)
            """, (session_id, user_id))
            conn.commit()
            return session_id
        except Exception as e:
            conn.rollback()
            print(f"❌ Error creating session: {e}")
            raise
        finally:
            conn.close()
    
    def end_session(self, session_id: str, message_count: int):
        """End a session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE sessions
                SET end_time = CURRENT_TIMESTAMP, message_count = ?
                WHERE session_id = ?
            """, (message_count, session_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"❌ Error ending session: {e}")
        finally:
            conn.close()
    
    # ==================== UTILITY METHODS ====================
    
    def get_database_stats(self) -> Dict:
        """Get overall database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # User count
            cursor.execute("SELECT COUNT(*) as count FROM users")
            stats['total_users'] = cursor.fetchone()['count']
            
            # Message count
            cursor.execute("SELECT COUNT(*) as count FROM conversations")
            stats['total_messages'] = cursor.fetchone()['count']
            
            # Practice log count
            cursor.execute("SELECT COUNT(*) as count FROM practice_logs")
            stats['total_practice_logs'] = cursor.fetchone()['count']
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            return {}
        finally:
            conn.close()
    
    def cleanup_old_data(self, days: int = 90):
        """
        Clean up old data (optional maintenance)
        
        Args:
            days: Delete data older than this many days
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Delete old conversations
            cursor.execute("""
                DELETE FROM conversations 
                WHERE timestamp < ?
            """, (cutoff_date,))
            
            # Delete old practice logs
            cursor.execute("""
                DELETE FROM practice_logs 
                WHERE timestamp < ?
            """, (cutoff_date,))
            
            conn.commit()
            print(f"✅ Cleaned up data older than {days} days")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error cleaning up old data: {e}")
            raise
        finally:
            conn.close()
