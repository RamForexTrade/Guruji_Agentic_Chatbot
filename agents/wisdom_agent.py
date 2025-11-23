"""
Wisdom Agent
============

Specialized agent for retrieving and contextualizing wisdom from Gurudev's teachings.

Responsibilities:
    - Perform semantic search on the knowledge base
    - Retrieve relevant wisdom based on user queries
    - Contextualize teachings to user's situation
    - Provide source attribution
    - Filter results by metadata (topics, emotions, situations)
    - Re-rank results for relevance

Architecture:
    User Query + Context → Wisdom Agent
                              ↓
                    RAG System (Vector Search)
                              ↓
                    Retrieve Teachings
                              ↓
                    Re-rank & Filter
                              ↓
                    Contextualize with LLM
                              ↓
                    Wisdom Response + Sources
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path

from langchain_core.messages import BaseMessage
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

from agents.base_agent import BaseAgent, AgentContext, AgentResponse
from agents.agent_types import AgentType
from rag_system import RAGSystem, UserContext

logger = logging.getLogger(__name__)


class WisdomAgent(BaseAgent):
    """
    Wisdom Agent for retrieving and contextualizing spiritual teachings.
    
    This agent wraps the existing RAG system to provide intelligent wisdom
    retrieval based on user queries, emotional states, and life situations.
    
    Features:
        - Semantic search across Gurudev's teachings
        - Metadata-based filtering (topics, emotions, situations)
        - Context-aware wisdom contextualization
        - Source attribution with teaching numbers
        - Confidence scoring based on retrieval quality
        - Re-ranking for relevance
    
    Integration with RAG System:
        The agent uses the existing RAGSystem class which includes:
        - ChromaDB vector store with embeddings
        - Custom retriever with metadata filtering
        - Teaching processor for markdown files
        - LLM chains for contextualization
    """
    
    def __init__(
        self,
        config_path: str = "config.yaml",
        knowledge_base_path: str = "Knowledge_Base",
        llm_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        top_k_results: int = 5,
        verbose: bool = False
    ):
        """
        Initialize the Wisdom Agent.
        
        Args:
            config_path: Path to config.yaml file
            knowledge_base_path: Path to Knowledge_Base directory
            llm_provider: LLM provider (groq, openai, anthropic)
            model_name: Model name
            temperature: LLM temperature for contextualizing wisdom
            top_k_results: Number of teachings to retrieve
            verbose: Enable verbose logging
        """
        super().__init__(
            agent_type=AgentType.WISDOM,
            name="wisdom",
            llm_provider=llm_provider,
            model_name=model_name,
            temperature=temperature,
            verbose=verbose
        )
        
        self.config_path = config_path
        self.knowledge_base_path = knowledge_base_path
        self.top_k_results = top_k_results
        
        # Initialize RAG system
        self.rag_system = None
        self._initialize_rag_system()
        
        # Context template for wisdom retrieval
        self.wisdom_prompt = self._create_wisdom_prompt()
        
        logger.info("Wisdom Agent initialized successfully")
    
    def _initialize_rag_system(self):
        """Initialize the RAG system with vector store and retriever"""
        try:
            logger.info("Initializing RAG system...")
            self.rag_system = RAGSystem(
                config_path=self.config_path,
                knowledge_base_path=self.knowledge_base_path
            )
            
            # Initialize the vector store if not already done
            if not self.rag_system.vectorstore:
                logger.info("Loading knowledge base into vector store...")
                self.rag_system.initialize_database()
            
            logger.info("RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            raise RuntimeError(f"Wisdom Agent cannot function without RAG system: {e}")
    
    def _create_wisdom_prompt(self) -> PromptTemplate:
        """
        Create the prompt template for contextualizing wisdom.
        
        This prompt helps the LLM provide relevant, compassionate wisdom
        that's tailored to the user's specific situation.
        
        Returns:
            PromptTemplate for wisdom contextualization
        """
        template = """You are a compassionate spiritual guide sharing wisdom from Gurudev Sri Sri Ravi Shankar's teachings.

User Context:
- Name: {user_name}
- Current State: {user_state}
- Life Situation: {life_situation}
- Age: {user_age}

User's Question/Concern:
{user_query}

Relevant Teachings Retrieved:
{retrieved_wisdom}

Source Information:
{sources}

Instructions:
1. Provide wisdom that directly addresses the user's question or concern
2. Be warm, empathetic, and encouraging
3. Use simple, accessible language
4. Connect the teachings to their current situation
5. DO NOT cite teaching numbers inline in your response - sources will be listed separately at the end
6. Write the wisdom in a flowing, narrative style without interrupting with citations
7. Keep the response focused and not too lengthy (3-5 paragraphs)
8. End with an actionable insight or reflection point
9. Maintain the authentic voice and essence of Gurudev's teachings

IMPORTANT: Write clean, flowing wisdom text WITHOUT any inline citations or teaching numbers. The sources will be appended automatically after your response.

Response:"""
        
        return PromptTemplate(
            template=template,
            input_variables=[
                "user_name",
                "user_state", 
                "life_situation",
                "user_age",
                "user_query",
                "retrieved_wisdom",
                "sources"
            ]
        )
    
    def define_tools(self) -> List:
        """
        Define tools for the wisdom agent.
        
        Tools:
            - retrieve_wisdom: Search knowledge base for relevant teachings
            - filter_by_metadata: Filter teachings by topics/emotions/situations
            - rerank_results: Re-rank retrieved teachings for relevance
        
        Returns:
            List of Tool objects
        """
        # Wisdom agent primarily uses the RAG system
        # Tools are implicitly the RAG retrieval methods
        return []
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the wisdom agent.
        
        Returns:
            System prompt string
        """
        return """You are the Wisdom Agent for the JAI GURU DEV AI Companion chatbot.

Your sacred responsibility is to retrieve and share wisdom from Gurudev Sri Sri Ravi Shankar's teachings.

## Your Capabilities:

1. **Semantic Search**: Find teachings relevant to the user's query
2. **Context-Aware Retrieval**: Consider user's emotional state and life situation
3. **Metadata Filtering**: Filter by topics, emotional states, problem categories
4. **Source Attribution**: Always cite teaching numbers and dates
5. **Wisdom Contextualization**: Adapt teachings to user's specific situation

## Guidelines:

**Retrieval Quality**:
- Prioritize teachings most relevant to the user's query
- Consider both semantic similarity and metadata matches
- Retrieve multiple teachings for comprehensive guidance
- Validate relevance before presenting

**Presentation Style**:
- Be compassionate and warm
- Speak in accessible language
- Maintain the authentic voice of the teachings
- Avoid jargon unless necessary
- Be concise yet comprehensive

**Source Attribution**:
- Always cite teaching numbers (e.g., "Teaching #123")
- Include date if relevant
- Mention location if it adds context
- Allow users to reference original teachings

**Context Awareness**:
- Adapt wisdom to user's age and life stage
- Consider their emotional state
- Address their specific situation
- Provide actionable insights

## When Retrieving Wisdom:

1. Analyze the user's query for key themes
2. Consider their emotional state and life situation
3. Retrieve relevant teachings (top 3-5)
4. Re-rank by relevance to specific query
5. Synthesize into coherent, contextual response
6. Cite sources clearly

## Quality Indicators:

- High relevance to user's query
- Multiple teachings support the guidance
- Clear source attribution
- Actionable insights provided
- Compassionate and encouraging tone

Your goal is to make Gurudev's wisdom accessible, relevant, and transformative for each user."""
    
    def process(
        self,
        input_text: str,
        context: AgentContext,
        chat_history: Optional[List[BaseMessage]] = None
    ) -> AgentResponse:
        """
        Process wisdom retrieval request.
        
        This is the main method that:
        1. Extracts user context and query
        2. Performs semantic search with RAG system
        3. Filters and re-ranks results
        4. Contextualizes wisdom with LLM
        5. Returns formatted response with sources
        
        Args:
            input_text: User's query or concern
            context: User context (profile, state, history)
            chat_history: Conversation history
        
        Returns:
            AgentResponse with wisdom and source citations
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Wisdom Agent processing: '{input_text[:50]}...'")
            
            # Step 1: Prepare user context for retrieval
            user_context = self._prepare_user_context(context)
            
            # Step 2: Enhance query with user context
            enhanced_query = self._enhance_query_with_context(
                input_text,
                user_context
            )
            
            # Step 3: Retrieve relevant teachings
            retrieved_docs = self._retrieve_teachings(
                enhanced_query,
                user_context
            )
            
            if not retrieved_docs:
                logger.warning("No relevant teachings found")
                return self._create_fallback_response(context, start_time)
            
            # Step 4: Calculate confidence based on retrieval quality
            confidence = self._calculate_retrieval_confidence(retrieved_docs)
            
            # Step 5: Extract and format teachings
            wisdom_content, sources = self._extract_wisdom_and_sources(retrieved_docs)
            
            # Step 6: Contextualize wisdom with LLM
            final_wisdom = self._contextualize_wisdom(
                user_query=input_text,
                retrieved_wisdom=wisdom_content,
                sources=sources,
                user_context=context
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create response
            response = AgentResponse(
                agent_name=self.name,
                content=final_wisdom,
                confidence=confidence,
                metadata={
                    'teachings_retrieved': len(retrieved_docs),
                    'sources': sources,
                    'enhanced_query': enhanced_query,
                    'retrieval_method': 'semantic_search_with_metadata'
                },
                tools_used=['semantic_search', 'metadata_filtering', 'llm_contextualization'],
                processing_time=processing_time,
                success=True
            )
            
            logger.info(f"Wisdom Agent completed in {processing_time:.2f}s with confidence {confidence:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"Wisdom Agent error: {e}", exc_info=True)
            return self.handle_error(e, context)
    
    def _prepare_user_context(self, context: AgentContext) -> UserContext:
        """
        Prepare user context for RAG retrieval.
        
        Extracts relevant information from AgentContext and formats it
        for the RAG system's UserContext.
        
        Args:
            context: AgentContext from orchestrator
        
        Returns:
            UserContext for RAG system
        """
        profile = context.user_profile
        
        # Extract relevant fields
        emotional_state = profile.get('emotional_state', '')
        life_situation = profile.get('life_situation', '')
        
        # Create UserContext for RAG system
        user_context = UserContext(
            emotional_state=emotional_state,
            life_aspect=life_situation,
            guidance_type='wisdom',  # Default to wisdom guidance
            specific_situation=context.metadata.get('specific_situation', '')
        )
        
        return user_context
    
    def _enhance_query_with_context(
        self,
        query: str,
        user_context: UserContext
    ) -> str:
        """
        Enhance the user's query with contextual information.
        
        This helps improve retrieval by adding relevant context
        about the user's state and situation.
        
        Args:
            query: Original user query
            user_context: User's context information
        
        Returns:
            Enhanced query string
        """
        # Build enhanced query
        context_parts = [query]
        
        if user_context.emotional_state:
            context_parts.append(f"emotional state: {user_context.emotional_state}")
        
        if user_context.life_aspect:
            context_parts.append(f"life situation: {user_context.life_aspect}")
        
        enhanced_query = " | ".join(context_parts)
        
        logger.debug(f"Enhanced query: {enhanced_query}")
        return enhanced_query
    
    def _retrieve_teachings(
        self,
        query: str,
        user_context: UserContext
    ) -> List[Document]:
        """
        Retrieve relevant teachings using the RAG system.
        
        Uses the CustomRetriever which combines:
        - Semantic similarity search
        - Metadata filtering (topics, emotions, situations)
        - Teaching number tracking
        
        Args:
            query: Search query (possibly enhanced)
            user_context: User context for filtering
        
        Returns:
            List of relevant Document objects
        """
        try:
            # Use RAG system's retriever
            if self.rag_system.retriever:
                docs = self.rag_system.retriever.get_relevant_documents(query)
            else:
                # Fallback to direct vectorstore search
                docs = self.rag_system.vectorstore.similarity_search(
                    query,
                    k=self.top_k_results
                )
            
            logger.info(f"Retrieved {len(docs)} teachings")
            return docs
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []
    
    def _calculate_retrieval_confidence(self, docs: List[Document]) -> float:
        """
        Calculate confidence score based on retrieval quality.
        
        Factors considered:
        - Number of documents retrieved
        - Presence of metadata
        - Relevance indicators
        
        Args:
            docs: Retrieved documents
        
        Returns:
            Confidence score (0.0 - 1.0)
        """
        if not docs:
            return 0.0
        
        # Base confidence on number of results
        base_confidence = min(len(docs) / self.top_k_results, 1.0)
        
        # Boost confidence if documents have rich metadata
        metadata_quality = 0.0
        for doc in docs:
            if doc.metadata:
                # Check for key metadata fields
                has_number = 'number' in doc.metadata
                has_topics = 'topics' in doc.metadata
                has_emotions = 'emotional_states' in doc.metadata
                
                metadata_quality += (has_number + has_topics + has_emotions) / 3.0
        
        metadata_quality /= len(docs)
        
        # Final confidence is weighted average
        confidence = 0.6 * base_confidence + 0.4 * metadata_quality
        
        return confidence
    
    def _extract_wisdom_and_sources(
        self,
        docs: List[Document]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Extract wisdom content and source information from documents.

        Args:
            docs: Retrieved documents

        Returns:
            Tuple of (wisdom_content, sources_list)
        """
        wisdom_parts = []
        sources = []

        for idx, doc in enumerate(docs):
            # Extract content
            content = doc.page_content
            wisdom_parts.append(f"Teaching {idx + 1}:\n{content}\n")

            # Extract source information
            metadata = doc.metadata
            source_info = {
                'teaching_number': metadata.get('number', 'Unknown'),
                'title': metadata.get('title', 'Untitled'),
                'date': metadata.get('date', ''),
                'location': metadata.get('location', ''),
                'topics': metadata.get('topics', ''),
                'relevance_rank': idx + 1,
                'content': content  # Store actual teaching content for sources section
            }
            sources.append(source_info)

        wisdom_content = "\n---\n".join(wisdom_parts)
        return wisdom_content, sources
    
    def _contextualize_wisdom(
        self,
        user_query: str,
        retrieved_wisdom: str,
        sources: List[Dict[str, Any]],
        user_context: AgentContext
    ) -> str:
        """
        Contextualize retrieved wisdom for the user's specific situation.

        Uses LLM to synthesize retrieved teachings into a coherent,
        personalized response that addresses the user's query.

        Args:
            user_query: Original user query
            retrieved_wisdom: Raw wisdom from retrieved teachings
            sources: Source information for citations
            user_context: User's context

        Returns:
            Contextualized wisdom response with sources appended
        """
        try:
            # Format sources for citation
            sources_text = self._format_sources(sources)

            # Extract user information
            profile = user_context.user_profile
            user_name = profile.get('name', 'friend')
            user_state = profile.get('emotional_state', 'seeking guidance')
            life_situation = profile.get('life_situation', '')
            user_age = profile.get('age', '')

            # Generate contextualized response
            prompt_input = {
                'user_name': user_name,
                'user_state': user_state,
                'life_situation': life_situation,
                'user_age': user_age,
                'user_query': user_query,
                'retrieved_wisdom': retrieved_wisdom,
                'sources': sources_text
            }

            # Invoke LLM
            formatted_prompt = self.wisdom_prompt.format(**prompt_input)
            response = self.llm.invoke(formatted_prompt)

            # Get clean wisdom text
            wisdom_text = response.content.strip()

            # Generate Part 4: Practice section based on the wisdom
            practice_section = self._generate_practice_section(
                wisdom_text=wisdom_text,
                retrieved_wisdom=retrieved_wisdom,
                user_context=user_context
            )

            # Combine wisdom + practice
            full_wisdom = wisdom_text + "\n\n" + practice_section

            # Append sources section at the end
            wisdom_with_sources = self._append_sources_section(full_wisdom, sources, retrieved_wisdom)

            return wisdom_with_sources

        except Exception as e:
            logger.error(f"Wisdom contextualization failed: {e}")
            # Fallback: return retrieved wisdom with basic formatting
            return self._format_fallback_wisdom(retrieved_wisdom, sources, user_context)
    
    def _format_sources(self, sources: List[Dict[str, Any]]) -> str:
        """Format sources for citation in the response"""
        sources_text = []

        for source in sources:
            source_line = f"- Teaching #{source['teaching_number']}"
            if source.get('title'):
                source_line += f": {source['title']}"
            if source.get('date'):
                source_line += f" ({source['date']})"
            sources_text.append(source_line)

        return "\n".join(sources_text)

    def _generate_practice_section(
        self,
        wisdom_text: str,
        retrieved_wisdom: str,
        user_context: AgentContext
    ) -> str:
        """
        Generate Part 4: Practice This Wisdom section.

        Creates contextual micro-games, nudges, or actionable practices
        based on the wisdom teachings retrieved in Part 3.

        Args:
            wisdom_text: The contextualized wisdom from Part 3
            retrieved_wisdom: Original retrieved teachings
            user_context: User's context (age, emotional state, etc.)

        Returns:
            Formatted Part 4 practice section
        """
        try:
            # Extract user information
            profile = user_context.user_profile
            user_name = profile.get('name', 'friend')
            user_age = profile.get('age', '')
            user_state = profile.get('emotional_state', '')
            life_situation = profile.get('life_situation', '')

            # Determine if humor is appropriate
            sensitive_states = ['grief', 'grieving', 'loss', 'trauma', 'traumatic']
            use_humor = not any(state in user_state.lower() for state in sensitive_states)

            practice_prompt = f"""Based on the wisdom shared above, create a PART 4: PRACTICE THIS WISDOM section.

User Context:
- Name: {user_name}
- Age: {user_age}
- Emotional State: {user_state}
- Life Situation: {life_situation}
- Humor Appropriate: {'Yes' if use_humor else 'No (grief/trauma context)'}

Wisdom Shared (Part 3):
{wisdom_text}

Original Teachings:
{retrieved_wisdom}

Instructions:
Create a brief, actionable "PART 4: PRACTICE THIS WISDOM" section that:

1. **Is directly connected to the teachings above** - Not generic, but specific to what was shared
2. **Tiny actions (15 seconds to 2 minutes)** - Must be quick and doable right now
3. **Age-appropriate** - Match the user's age and situation
4. **Contextual to their emotion** - If anxious, calming. If sad, uplifting. If overwhelmed, grounding.
5. **Choose ONE format** from:
   - **Micro-game**: "Right now: Close your eyes, take 3 breaths, and on each exhale silently say 'I release what I cannot control.'"
   - **Nudge**: "Text yourself one word that describes how you want to feel by tomorrow."
   - **Emoji check-in**: "Send yourself this emoji that matches where you are emotionally: 😌 calm, 😰 anxious, 😔 heavy, or 🙂 okay."
   - **Gratitude prompt**: "Name one tiny thing (even just a breath) you're grateful for right now."
   - **Reflection**: "Write down: What's one belief about this situation I can let go of?"
   - **Humor-light** (ONLY if appropriate): "Challenge: Find one thing in your space right now that makes you smile, even slightly. Stare at it for 10 seconds."

Format:
✨ **PART 4: PRACTICE THIS WISDOM**

[One clear, specific action directly tied to the wisdom teachings above. Keep it to 1-2 sentences max. Make it doable RIGHT NOW.]

IMPORTANT:
- This must be SPECIFIC to the wisdom teachings, not generic
- Must reference or build on what was shared in Part 3
- Keep it SHORT (1-2 sentences)
- Make it immediately actionable

Your response (just the Part 4 section):"""

            # Invoke LLM
            response = self.llm.invoke(practice_prompt)
            practice_text = response.content.strip()

            # Ensure it has the Part 4 heading if LLM didn't include it
            if "PART 4" not in practice_text:
                practice_text = "✨ **PART 4: PRACTICE THIS WISDOM**\n\n" + practice_text

            return practice_text

        except Exception as e:
            logger.error(f"Practice section generation failed: {e}")
            # Fallback to simple actionable reflection
            return "✨ **PART 4: PRACTICE THIS WISDOM**\n\nTake a moment today to reflect on one insight from above that resonates with you. Let it settle gently in your awareness."

    def _append_sources_section(
        self,
        wisdom_text: str,
        sources: List[Dict[str, Any]],
        retrieved_wisdom: str
    ) -> str:
        """
        Append a formatted sources section at the end of the wisdom response.

        Args:
            wisdom_text: The clean wisdom text without inline citations
            sources: List of source information dicts
            retrieved_wisdom: Original retrieved wisdom text

        Returns:
            Wisdom text with sources section appended
        """
        if not sources:
            return wisdom_text

        # Build sources section
        sources_section = "\n\n---\n\n**📚 Teachings Referenced:**\n\n"

        for idx, source in enumerate(sources, 1):
            teaching_num = source.get('teaching_number', 'Unknown')
            title = source.get('title', 'Untitled')
            date = source.get('date', '')
            location = source.get('location', '')
            content = source.get('content', '')

            # Format each source
            source_entry = f"**Teaching #{teaching_num}**"
            if title and title != 'Untitled':
                source_entry += f": {title}"

            # Add metadata if available
            metadata_parts = []
            if date:
                metadata_parts.append(date)
            if location:
                metadata_parts.append(location)
            if metadata_parts:
                source_entry += f" ({', '.join(metadata_parts)})"

            source_entry += "\n"

            # Add teaching content (truncate if too long)
            if content:
                # Limit content to first 500 characters to keep it readable
                content_preview = content[:500] + "..." if len(content) > 500 else content
                source_entry += f"\n{content_preview}\n"

            sources_section += source_entry + "\n"

        # Combine wisdom text with sources
        return wisdom_text + sources_section

    def _format_fallback_wisdom(
        self,
        wisdom: str,
        sources: List[Dict[str, Any]],
        user_context: AgentContext
    ) -> str:
        """
        Format wisdom as fallback when LLM contextualization fails.

        Provides basic formatting with Part 4 practice and source citations.

        Args:
            wisdom: Retrieved wisdom content
            sources: Source information
            user_context: User's context

        Returns:
            Formatted wisdom string with Part 4 and sources section
        """
        fallback = f"""Here is wisdom from Gurudev's teachings:

{wisdom}

May this wisdom bring you clarity and peace. 🙏"""

        # Generate Part 4 even in fallback
        try:
            practice_section = self._generate_practice_section(
                wisdom_text=fallback,
                retrieved_wisdom=wisdom,
                user_context=user_context
            )
            fallback = fallback + "\n\n" + practice_section
        except Exception as e:
            logger.warning(f"Could not generate practice section in fallback: {e}")

        # Append sources section using the same method
        return self._append_sources_section(fallback, sources, wisdom)
    
    def _create_fallback_response(
        self,
        context: AgentContext,
        start_time: datetime
    ) -> AgentResponse:
        """
        Create fallback response when no teachings are found.
        
        Args:
            context: User context
            start_time: Processing start time
        
        Returns:
            AgentResponse with fallback message
        """
        user_name = context.user_profile.get('name', 'friend')
        
        fallback_message = f"""Dear {user_name},

I couldn't find specific teachings directly addressing your query in the knowledge base.

However, I'm here to support you. Could you perhaps:
- Rephrase your question differently
- Provide more context about what you're experiencing
- Ask about a related topic

Remember, every question is a step on the spiritual journey. 🙏"""
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            agent_name=self.name,
            content=fallback_message,
            confidence=0.3,
            metadata={
                'fallback': True,
                'reason': 'no_teachings_found'
            },
            processing_time=processing_time,
            success=True
        )
    
    def search_by_metadata(
        self,
        topic: Optional[str] = None,
        emotional_state: Optional[str] = None,
        life_situation: Optional[str] = None,
        problem_category: Optional[str] = None,
        top_k: int = 5
    ) -> List[Document]:
        """
        Search teachings by specific metadata filters.
        
        This method allows direct metadata-based search without
        semantic similarity, useful for browsing specific categories.
        
        Args:
            topic: Topic filter (e.g., "meditation", "anxiety")
            emotional_state: Emotional state filter (e.g., "anxious", "calm")
            life_situation: Life situation filter (e.g., "relationship", "work")
            problem_category: Problem category filter
            top_k: Number of results to return
        
        Returns:
            List of filtered documents
        """
        # Build metadata filter
        where_filter = {}
        
        if topic:
            where_filter['topics'] = {"$contains": topic}
        if emotional_state:
            where_filter['emotional_states'] = {"$contains": emotional_state}
        if life_situation:
            where_filter['life_situations'] = {"$contains": life_situation}
        if problem_category:
            where_filter['problem_categories'] = {"$contains": problem_category}
        
        # Search with filter
        try:
            results = self.rag_system.vectorstore.similarity_search(
                "",  # Empty query for metadata-only search
                k=top_k,
                filter=where_filter if where_filter else None
            )
            return results
        except Exception as e:
            logger.error(f"Metadata search failed: {e}")
            return []


# Example usage and testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    import uuid
    
    load_dotenv()
    
    print("=" * 60)
    print("Wisdom Agent Test")
    print("=" * 60)
    
    try:
        # Create wisdom agent
        wisdom_agent = WisdomAgent(
            config_path="config.yaml",
            knowledge_base_path="Knowledge_Base",
            top_k_results=3,
            verbose=True
        )
        
        # Create test context
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={
                'name': 'Alice',
                'age': 28,
                'emotional_state': 'anxious',
                'life_situation': 'work stress'
            }
        )
        
        # Test queries
        test_queries = [
            "I'm feeling very anxious about work. What should I do?",
            "Why do we meditate?",
            "How can I find inner peace?",
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"User Query: {query}")
            print("-" * 60)
            
            response = wisdom_agent.process(query, context)
            
            print(f"Confidence: {response.confidence:.2f}")
            print(f"Teachings Retrieved: {response.metadata.get('teachings_retrieved', 0)}")
            print(f"Processing Time: {response.processing_time:.2f}s")
            print(f"\nWisdom Response:\n{response.content}")
            
            if 'sources' in response.metadata:
                print(f"\nSources:")
                for source in response.metadata['sources']:
                    print(f"  - Teaching #{source['teaching_number']}: {source['title']}")
        
        print("\n" + "=" * 60)
        print("✅ Wisdom Agent Test Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
