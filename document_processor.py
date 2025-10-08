import re
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Teaching:
    """Structure to hold teaching data"""
    number: str
    title: str
    date: str
    location: str
    topics: List[str]
    keywords: List[str]
    problem_categories: List[str]
    emotional_states: List[str]
    life_situations: List[str]
    content: str
    source_file: str = ""  # Track which file this came from
    
    def get_full_text(self) -> str:
        """Get full searchable text including metadata"""
        metadata_text = f"""
        Teaching #{self.number}: {self.title}
        Date: {self.date}
        Location: {self.location}
        Topics: {', '.join(self.topics)}
        Keywords: {', '.join(self.keywords)}
        Problem Categories: {', '.join(self.problem_categories)}
        Emotional States: {', '.join(self.emotional_states)}
        Life Situations: {', '.join(self.life_situations)}
        """
        return f"{metadata_text}\n\nContent:\n{self.content}"

class DocumentProcessor:
    """Process markdown files containing Sri Sri Ravi Shankar's teachings"""
    
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = Path(knowledge_base_path)
        
    def load_all_teachings(self) -> List[Teaching]:
        """
        Load all teachings from markdown files in ALL batch folders.
        
        This method now scans:
        - Root directory: Knowledge_Base/*.md
        - Batch folders: Knowledge_Base/batch_*/*.md
        
        Returns: List of all teachings sorted by teaching number
        """
        all_teachings = []
        file_count = 0
        
        print("📚 Scanning for teachings...")
        print(f"   Knowledge Base: {self.knowledge_base_path}")
        
        # Pattern 1: Scan root directory for any .md files
        root_files = list(self.knowledge_base_path.glob("*.md"))
        if root_files:
            print(f"   📄 Found {len(root_files)} files in root directory")
            for md_file in root_files:
                teachings = self.parse_markdown_file(md_file)
                all_teachings.extend(teachings)
                file_count += len(teachings)
        
        # Pattern 2: Scan ALL batch_* subdirectories
        batch_folders = sorted(self.knowledge_base_path.glob("batch_*"))
        
        if batch_folders:
            print(f"   📁 Found {len(batch_folders)} batch folders:")
            for batch_folder in batch_folders:
                if batch_folder.is_dir():
                    batch_files = list(batch_folder.glob("*.md"))
                    # Filter out README files
                    batch_files = [f for f in batch_files if f.name.lower() != 'readme.md']
                    
                    if batch_files:
                        print(f"      • {batch_folder.name}: {len(batch_files)} teaching files")
                        for md_file in batch_files:
                            teachings = self.parse_markdown_file(md_file)
                            all_teachings.extend(teachings)
                            file_count += 1
                    else:
                        print(f"      • {batch_folder.name}: No teaching files (empty or only README)")
        else:
            print("   ⚠️  No batch folders found")
        
        # Sort teachings by number for better organization
        all_teachings = sorted(all_teachings, key=lambda x: self._parse_teaching_number(x.number))
        
        print(f"\n✅ Total: Loaded {len(all_teachings)} teachings from {file_count} files")
        
        # Display teaching range for verification
        if all_teachings:
            numbers = [self._parse_teaching_number(t.number) for t in all_teachings]
            min_num = min(numbers)
            max_num = max(numbers)
            print(f"   Teaching range: #{min_num:03d} - #{max_num:03d}")
        
        return all_teachings
    
    def _parse_teaching_number(self, number_str: str) -> int:
        """Extract numeric value from teaching number string"""
        try:
            # Extract digits from string like "001" or "1" or "Teaching 1"
            match = re.search(r'\d+', str(number_str))
            if match:
                return int(match.group())
            return 0
        except:
            return 0
    
    def parse_markdown_file(self, file_path: Path) -> List[Teaching]:
        """Parse a single markdown file and extract teachings"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip README files
            if file_path.name.lower() == 'readme.md':
                return []
            
            teachings = []
            
            # Check if this is an individual teaching file (teaching_XXX.md format)
            if file_path.name.startswith('teaching_') and file_path.name.endswith('.md'):
                # Parse as single teaching file
                teaching = self.parse_individual_teaching_file(content, file_path)
                if teaching:
                    teachings.append(teaching)
            else:
                # Parse as combined file with multiple teachings
                # Split by teaching sections
                teaching_sections = re.split(r'\n## Teaching #', content)
                
                for i, section in enumerate(teaching_sections):
                    if i == 0:  # Skip the header section
                        continue
                    
                    # Add back the "## Teaching #" prefix
                    section = "## Teaching #" + section
                    teaching = self.parse_teaching_section(section, file_path)
                    if teaching:
                        teachings.append(teaching)
            
            return teachings
            
        except Exception as e:
            print(f"⚠️  Error parsing {file_path.name}: {e}")
            return []
    
    def parse_individual_teaching_file(self, content: str, file_path: Path) -> Teaching:
        """Parse a single teaching from an individual file (teaching_XXX.md)"""
        try:
            # Look for the teaching header pattern
            # Could be: # Sri Sri Ravishankar Teaching #XXX followed by ## Teaching #XXX
            # Or just: ## Teaching #XXX
            
            # Find the ## Teaching # section
            match = re.search(r'## Teaching #(.+)', content)
            if match:
                # Extract from ## Teaching # onwards
                teaching_start = content.find('## Teaching #')
                teaching_content = content[teaching_start:]
                return self.parse_teaching_section(teaching_content, file_path)
            
            # If no ## Teaching # found, treat entire file as teaching
            # This handles files that might just have the content
            return self.parse_teaching_section(content, file_path)
            
        except Exception as e:
            print(f"⚠️  Error parsing individual file {file_path.name}: {e}")
            return None
    
    def parse_teaching_section(self, section: str, source_file: Path = None) -> Teaching:
        """Parse a single teaching section"""
        try:
            lines = section.strip().split('\n')
            
            # Extract teaching number and title
            title_line = lines[0].replace('## Teaching #', '').strip()
            if ':' in title_line:
                number, title = title_line.split(':', 1)
                number = number.strip()
                title = title.strip()
            else:
                number = title_line.strip()
                title = "Untitled"
            
            # Initialize variables
            date = "Not specified"
            location = "Not specified"
            topics = []
            keywords = []
            problem_categories = []
            emotional_states = []
            life_situations = []
            content = ""
            
            content_started = False
            
            for line in lines[1:]:
                line = line.strip()
                
                if line.startswith('**Date:**'):
                    date = line.replace('**Date:**', '').strip()
                elif line.startswith('**Location:**'):
                    location = line.replace('**Location:**', '').strip()
                elif line.startswith('**Topics:**'):
                    topics_str = line.replace('**Topics:**', '').strip()
                    topics = [t.strip() for t in topics_str.split(',') if t.strip()]
                elif line.startswith('**Keywords:**'):
                    keywords_str = line.replace('**Keywords:**', '').strip()
                    keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
                elif line.startswith('**Problem Categories:**'):
                    prob_str = line.replace('**Problem Categories:**', '').strip()
                    problem_categories = [p.strip() for p in prob_str.split(',') if p.strip()]
                elif line.startswith('**Emotional States:**'):
                    emot_str = line.replace('**Emotional States:**', '').strip()
                    emotional_states = [e.strip() for e in emot_str.split(',') if e.strip()]
                elif line.startswith('**Life Situations:**'):
                    life_str = line.replace('**Life Situations:**', '').strip()
                    life_situations = [l.strip() for l in life_str.split(',') if l.strip()]
                elif line.startswith('### Content:'):
                    content_started = True
                elif content_started and line and line != '---':
                    if content:
                        content += "\n" + line
                    else:
                        content = line
            
            return Teaching(
                number=number,
                title=title,
                date=date,
                location=location,
                topics=topics,
                keywords=keywords,
                problem_categories=problem_categories,
                emotional_states=emotional_states,
                life_situations=life_situations,
                content=content.strip(),
                source_file=str(source_file.name) if source_file else "unknown"
            )
            
        except Exception as e:
            print(f"⚠️  Error parsing teaching section: {e}")
            return None
    
    @staticmethod
    def search_teachings_by_metadata(teachings: List[Teaching], 
                                     query_topics: List[str] = None,
                                     query_emotions: List[str] = None,
                                     query_situations: List[str] = None,
                                     query_problems: List[str] = None) -> List[Teaching]:
        """Search teachings based on metadata fields"""
        results = []
        
        for teaching in teachings:
            score = 0
            
            # Check topics
            if query_topics:
                for topic in query_topics:
                    if any(topic.lower() in t.lower() for t in teaching.topics):
                        score += 2
            
            # Check emotional states
            if query_emotions:
                for emotion in query_emotions:
                    if any(emotion.lower() in e.lower() for e in teaching.emotional_states):
                        score += 3
            
            # Check life situations
            if query_situations:
                for situation in query_situations:
                    if any(situation.lower() in s.lower() for s in teaching.life_situations):
                        score += 2
            
            # Check problem categories
            if query_problems:
                for problem in query_problems:
                    if any(problem.lower() in p.lower() for p in teaching.problem_categories):
                        score += 3
            
            if score > 0:
                results.append((teaching, score))
        
        # Sort by score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return [teaching for teaching, score in results]
