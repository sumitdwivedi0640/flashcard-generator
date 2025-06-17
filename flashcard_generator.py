import os
import json
import time
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks import get_openai_callback
import cohere

from models import (
    Flashcard, FlashcardSet, GenerationRequest, GenerationResponse,
    Subject, Language, DifficultyLevel
)
from prompts import PromptTemplates

# Load environment variables
load_dotenv()


class CohereFlashcardGenerator:
    def __init__(self, api_key: str):
        self.co = cohere.Client(api_key)

    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        response = self.co.generate(
            model='command',
            prompt=prompt,
            max_tokens=max_tokens
        )
        return response.generations[0].text


class FlashcardGenerator:
    """Core flashcard generation engine using LLM integration."""

    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize the flashcard generator.

        Args:
            model_name: OpenAI model to use
            temperature: Model temperature for creativity control
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self.use_cohere = False
        self.cohere_gen = None
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the language model."""
        api_key = os.getenv("OPENAI_API_KEY")
        cohere_key = os.getenv("COHERE_API_KEY")
        if api_key:
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                openai_api_key=api_key
            )
            self.use_cohere = False
        elif cohere_key:
            self.cohere_gen = CohereFlashcardGenerator(cohere_key)
            self.use_cohere = True
        else:
            raise ValueError(
                "OPENAI_API_KEY or COHERE_API_KEY environment variable is required")

    def generate_flashcards(self, request: GenerationRequest) -> GenerationResponse:
        """
        Generate flashcards from educational content.

        Args:
            request: Generation request containing content and parameters

        Returns:
            Generation response with flashcards and metadata
        """
        start_time = time.time()

        try:
            # Validate input
            if not request.content.strip():
                return GenerationResponse(
                    success=False,
                    error_message="No content provided for flashcard generation."
                )

            if self.use_cohere:
                # Use a simple, explicit prompt for Cohere
                full_prompt = (
                    f"Generate {request.num_cards} flashcards in Q&A format about the following content:\n"
                    f"{request.content}\n"
                    "Each flashcard should be formatted as:\nQ: [question]\nA: [answer]\n"
                    "Only output the flashcards, nothing else."
                )
            else:
                if request.subject and request.subject != Subject.OTHER:
                    prompt = PromptTemplates.get_subject_specific_prompt(
                        request.subject, request.language
                    )
                else:
                    prompt = PromptTemplates.get_base_prompt(
                        request.subject, request.language
                    )
                full_prompt = prompt + request.content

            # Generate flashcards using LLM
            if not self.use_cohere:
                with get_openai_callback() as cb:
                    response = self.llm.invoke([
                        SystemMessage(
                            content="You are an expert educational content creator."),
                        HumanMessage(content=full_prompt)
                    ])

                    # Parse the response
                    flashcards, topics = self._parse_llm_response(
                        response.content)
            else:
                response_text = self.cohere_gen.generate(
                    full_prompt, max_tokens=1000)
                print("Cohere response:", response_text)
                flashcards, topics = self._parse_text_response(response_text)

            # Validate and process flashcards
            if not flashcards:
                return GenerationResponse(
                    success=False,
                    error_message="No valid flashcards were generated. Please try again."
                )

            # Limit to requested number of cards
            if len(flashcards) > request.num_cards:
                flashcards = flashcards[:request.num_cards]

            # Update topics mapping for limited cards
            topics = self._update_topics_mapping(topics, len(flashcards))

            processing_time = time.time() - start_time

            return GenerationResponse(
                success=True,
                flashcards=flashcards,
                topics=topics,
                processing_time=processing_time
            )

        except Exception as e:
            return GenerationResponse(
                success=False,
                error_message=f"Error generating flashcards: {str(e)}"
            )

    def _parse_llm_response(self, response_text: str) -> Tuple[List[Flashcard], Dict[str, List[int]]]:
        """
        Parse the LLM response to extract flashcards and topics.

        Args:
            response_text: Raw response from the LLM

        Returns:
            Tuple of (flashcards, topics)
        """
        try:
            # Try to extract JSON from the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)

            # Extract flashcards
            flashcards = []
            for card_data in data.get('flashcards', []):
                try:
                    flashcard = Flashcard(
                        question=card_data.get('question', '').strip(),
                        answer=card_data.get('answer', '').strip(),
                        difficulty=card_data.get('difficulty', 'Medium'),
                        topic=card_data.get('topic', 'General'),
                        language=Language.ENGLISH  # Will be updated based on request
                    )
                    flashcards.append(flashcard)
                except Exception as e:
                    print(f"Error parsing flashcard: {e}")
                    continue

            # Extract topics
            topics = data.get('topics', {})

            return flashcards, topics

        except json.JSONDecodeError as e:
            # Fallback: try to extract flashcards from text format
            return self._parse_text_response(response_text)
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return [], {}

    def _parse_text_response(self, response_text: str) -> Tuple[List[Flashcard], Dict[str, List[int]]]:
        """
        Fallback parser for text-based responses.

        Args:
            response_text: Raw response text

        Returns:
            Tuple of (flashcards, topics)
        """
        from models import DifficultyLevel, Language, Subject
        flashcards = []
        topics = {"General": []}
        current_topic = "General"

        lines = response_text.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Look for topic headers
            if line.upper().endswith(':') and len(line) < 50:
                current_topic = line[:-1].strip()
                if current_topic not in topics:
                    topics[current_topic] = []
                i += 1
                continue

            # Look for question-answer pairs
            if line.startswith('Q:') or line.startswith('Question:'):
                question = line.replace('Q:', '').replace(
                    'Question:', '').strip()
                i += 1

                # Look for answer
                answer = ""
                while i < len(lines) and not lines[i].strip().startswith('Q:') and not lines[i].strip().startswith('Question:'):
                    answer_line = lines[i].strip()
                    if answer_line:
                        answer += answer_line + " "
                    i += 1

                if question and answer.strip():
                    try:
                        flashcard = Flashcard(
                            question=question,
                            answer=answer.strip(),
                            difficulty=DifficultyLevel.MEDIUM,
                            topic=current_topic,
                            subject=None,
                            language=Language.ENGLISH
                        )
                        flashcards.append(flashcard)
                        topics[current_topic].append(len(flashcards) - 1)
                    except Exception as e:
                        print(f"Error creating flashcard: {e}")
                        continue
            else:
                i += 1

        return flashcards, topics

    def _update_topics_mapping(self, topics: Dict[str, List[int]], num_cards: int) -> Dict[str, List[int]]:
        """
        Update topics mapping after limiting the number of flashcards.

        Args:
            topics: Original topics mapping
            num_cards: Number of cards after limiting

        Returns:
            Updated topics mapping
        """
        updated_topics = {}

        for topic, indices in topics.items():
            # Filter indices that are within the valid range
            valid_indices = [idx for idx in indices if idx < num_cards]
            if valid_indices:
                updated_topics[topic] = valid_indices

        return updated_topics

    def translate_flashcards(self, flashcards: List[Flashcard], target_language: Language) -> List[Flashcard]:
        """
        Translate flashcards to a different language.

        Args:
            flashcards: List of flashcards to translate
            target_language: Target language for translation

        Returns:
            List of translated flashcards
        """
        if target_language == Language.ENGLISH:
            return flashcards

        try:
            # Prepare flashcards for translation
            flashcard_data = []
            for card in flashcards:
                flashcard_data.append({
                    "question": card.question,
                    "answer": card.answer,
                    "difficulty": card.difficulty,
                    "topic": card.topic
                })

            # Create translation prompt
            prompt = PromptTemplates.get_translation_prompt(target_language)
            prompt += f"\n\nFlashcards to translate:\n{json.dumps(flashcard_data, indent=2)}"

            # Generate translation
            response = self.llm.invoke([
                SystemMessage(content="You are a professional translator."),
                HumanMessage(content=prompt)
            ])

            # Parse translated flashcards
            translated_flashcards, _ = self._parse_llm_response(
                response.content)

            # Update language for all translated cards
            for card in translated_flashcards:
                card.language = target_language

            return translated_flashcards

        except Exception as e:
            print(f"Error translating flashcards: {e}")
            return flashcards

    def improve_flashcards(self, flashcards: List[Flashcard]) -> List[Flashcard]:
        """
        Improve existing flashcards using LLM.

        Args:
            flashcards: List of flashcards to improve

        Returns:
            List of improved flashcards
        """
        try:
            # Prepare flashcards for improvement
            flashcard_data = []
            for card in flashcards:
                flashcard_data.append({
                    "question": card.question,
                    "answer": card.answer,
                    "difficulty": card.difficulty,
                    "topic": card.topic
                })

            # Create improvement prompt
            prompt = PromptTemplates.get_editing_prompt()
            prompt += f"\n\nFlashcards to improve:\n{json.dumps(flashcard_data, indent=2)}"

            # Generate improvements
            response = self.llm.invoke([
                SystemMessage(
                    content="You are an expert educational content editor."),
                HumanMessage(content=prompt)
            ])

            # Parse improved flashcards
            improved_flashcards, _ = self._parse_llm_response(response.content)

            return improved_flashcards

        except Exception as e:
            print(f"Error improving flashcards: {e}")
            return flashcards

    def detect_topics(self, content: str) -> Dict[str, Dict]:
        """
        Detect topics and structure in educational content.

        Args:
            content: Educational content to analyze

        Returns:
            Dictionary containing topic analysis
        """
        try:
            prompt = PromptTemplates.get_topic_detection_prompt()
            prompt += f"\n\nContent to analyze:\n{content}"

            response = self.llm.invoke([
                SystemMessage(content="You are an expert content analyst."),
                HumanMessage(content=prompt)
            ])

            # Try to parse the response as JSON
            json_start = response.content.find('{')
            json_end = response.content.rfind('}') + 1

            if json_start != -1 and json_end > 0:
                json_str = response.content[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"topics": {}, "content_summary": "Topic detection failed"}

        except Exception as e:
            print(f"Error detecting topics: {e}")
            return {"topics": {}, "content_summary": f"Error: {str(e)}"}
