from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class DifficultyLevel(str, Enum):
    """Enumeration for flashcard difficulty levels."""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class Subject(str, Enum):
    """Enumeration for subject categories."""
    BIOLOGY = "Biology"
    CHEMISTRY = "Chemistry"
    PHYSICS = "Physics"
    MATHEMATICS = "Mathematics"
    COMPUTER_SCIENCE = "Computer Science"
    HISTORY = "History"
    LITERATURE = "Literature"
    GEOGRAPHY = "Geography"
    ECONOMICS = "Economics"
    PSYCHOLOGY = "Psychology"
    OTHER = "Other"


class Language(str, Enum):
    """Enumeration for supported languages."""
    ENGLISH = "English"
    SPANISH = "Spanish"
    FRENCH = "French"
    GERMAN = "German"
    CHINESE = "Chinese"
    JAPANESE = "Japanese"


class Flashcard(BaseModel):
    """Data model for individual flashcards."""
    question: str = Field(..., description="The flashcard question")
    answer: str = Field(..., description="The flashcard answer")
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIUM, description="Difficulty level")
    topic: Optional[str] = Field(
        default=None, description="Topic or section this card belongs to")
    subject: Optional[Subject] = Field(
        default=None, description="Subject category")
    language: Language = Field(
        default=Language.ENGLISH, description="Language of the flashcard")

    class Config:
        use_enum_values = True


class FlashcardSet(BaseModel):
    """Data model for a collection of flashcards."""
    title: str = Field(..., description="Title of the flashcard set")
    description: Optional[str] = Field(
        default=None, description="Description of the set")
    subject: Optional[Subject] = Field(
        default=None, description="Subject category")
    language: Language = Field(
        default=Language.ENGLISH, description="Language of the set")
    flashcards: List[Flashcard] = Field(
        default_factory=list, description="List of flashcards")
    created_at: Optional[str] = Field(
        default=None, description="Creation timestamp")

    class Config:
        use_enum_values = True


class GenerationRequest(BaseModel):
    """Data model for flashcard generation requests."""
    content: str = Field(...,
                         description="Input content for flashcard generation")
    subject: Optional[Subject] = Field(
        default=None, description="Subject category")
    language: Language = Field(
        default=Language.ENGLISH, description="Target language")
    num_cards: int = Field(default=15, ge=5, le=50,
                           description="Number of flashcards to generate")
    include_difficulty: bool = Field(
        default=True, description="Include difficulty levels")
    include_topics: bool = Field(
        default=True, description="Include topic grouping")

    class Config:
        use_enum_values = True


class GenerationResponse(BaseModel):
    """Data model for flashcard generation responses."""
    success: bool = Field(..., description="Whether generation was successful")
    flashcards: List[Flashcard] = Field(
        default_factory=list, description="Generated flashcards")
    topics: Dict[str, List[int]] = Field(
        default_factory=dict, description="Topic grouping with flashcard indices")
    error_message: Optional[str] = Field(
        default=None, description="Error message if generation failed")
    processing_time: Optional[float] = Field(
        default=None, description="Time taken for generation in seconds")

    class Config:
        use_enum_values = True


class ExportFormat(str, Enum):
    """Enumeration for export formats."""
    CSV = "csv"
    JSON = "json"
    ANKI = "anki"
    QUIZLET = "quizlet"


class ExportRequest(BaseModel):
    """Data model for export requests."""
    flashcard_set: FlashcardSet = Field(...,
                                        description="Flashcard set to export")
    format: ExportFormat = Field(..., description="Export format")
    filename: Optional[str] = Field(
        default=None, description="Custom filename")

    class Config:
        use_enum_values = True
