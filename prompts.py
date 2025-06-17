from typing import Optional
from models import Subject, Language, DifficultyLevel


class PromptTemplates:
    """Collection of prompt templates for different flashcard generation scenarios."""

    @staticmethod
    def get_base_prompt(subject: Optional[Subject] = None, language: Language = Language.ENGLISH) -> str:
        """Get the base prompt template for flashcard generation."""

        subject_context = ""
        if subject and subject != Subject.OTHER:
            subject_context = f"Focus on {subject.value} concepts and terminology. "

        language_instruction = ""
        if language != Language.ENGLISH:
            language_instruction = f"Generate all flashcards in {language.value}. "

        return f"""You are an expert educational content creator specializing in creating high-quality flashcards for learning. {subject_context}{language_instruction}

Your task is to analyze the provided educational content and create effective flashcards that follow these guidelines:

1. **Question Quality**: 
   - Questions should be clear, concise, and test understanding
   - Avoid yes/no questions unless testing critical concepts
   - Use various question types: definition, application, analysis, synthesis

2. **Answer Quality**:
   - Answers should be comprehensive yet concise
   - Include key details and context
   - Be self-contained and accurate

3. **Difficulty Distribution**:
   - Easy: Basic recall and understanding
   - Medium: Application and analysis
   - Hard: Synthesis, evaluation, and complex concepts

4. **Topic Organization**:
   - Group related concepts together
   - Identify main themes and subtopics
   - Maintain logical flow

5. **Educational Value**:
   - Focus on important concepts and key learning objectives
   - Include both factual and conceptual knowledge
   - Ensure progressive difficulty within topics

Please generate flashcards in the following JSON format:
{{
    "flashcards": [
        {{
            "question": "Clear, specific question",
            "answer": "Comprehensive, accurate answer",
            "difficulty": "Easy/Medium/Hard",
            "topic": "Topic or section name"
        }}
    ],
    "topics": {{
        "Topic Name": [0, 1, 2]  // Indices of flashcards in this topic
    }}
}}

Content to analyze:
"""

    @staticmethod
    def get_subject_specific_prompt(subject: Subject, language: Language = Language.ENGLISH) -> str:
        """Get subject-specific prompt enhancements."""

        subject_prompts = {
            Subject.BIOLOGY: """
Additional Biology-specific guidelines:
- Focus on cellular processes, systems, and biological concepts
- Include scientific terminology and definitions
- Emphasize cause-and-effect relationships
- Cover both microscopic and macroscopic levels
- Include examples from different organisms when relevant
""",
            Subject.CHEMISTRY: """
Additional Chemistry-specific guidelines:
- Focus on chemical reactions, bonding, and molecular structures
- Include chemical formulas and equations
- Emphasize periodic trends and chemical properties
- Cover both organic and inorganic chemistry concepts
- Include practical applications and laboratory procedures
""",
            Subject.PHYSICS: """
Additional Physics-specific guidelines:
- Focus on physical laws, principles, and mathematical relationships
- Include formulas and units of measurement
- Emphasize problem-solving and conceptual understanding
- Cover mechanics, thermodynamics, electromagnetism, and modern physics
- Include real-world applications and phenomena
""",
            Subject.MATHEMATICS: """
Additional Mathematics-specific guidelines:
- Focus on mathematical concepts, theorems, and problem-solving strategies
- Include formulas, proofs, and mathematical notation
- Emphasize logical reasoning and mathematical thinking
- Cover algebra, calculus, geometry, and statistics
- Include step-by-step problem-solving approaches
""",
            Subject.COMPUTER_SCIENCE: """
Additional Computer Science-specific guidelines:
- Focus on programming concepts, algorithms, and data structures
- Include code examples and pseudocode
- Emphasize computational thinking and problem-solving
- Cover software engineering, databases, and computer architecture
- Include practical programming scenarios
""",
            Subject.HISTORY: """
Additional History-specific guidelines:
- Focus on historical events, figures, and their significance
- Include dates, locations, and causal relationships
- Emphasize historical context and impact
- Cover political, social, economic, and cultural aspects
- Include primary and secondary source analysis
""",
            Subject.LITERATURE: """
Additional Literature-specific guidelines:
- Focus on literary devices, themes, and author techniques
- Include character analysis and plot elements
- Emphasize critical reading and interpretation
- Cover different genres and literary periods
- Include textual evidence and close reading skills
""",
            Subject.GEOGRAPHY: """
Additional Geography-specific guidelines:
- Focus on physical and human geography concepts
- Include maps, spatial relationships, and environmental factors
- Emphasize regional characteristics and global patterns
- Cover climate, landforms, population, and cultural geography
- Include current events and environmental issues
""",
            Subject.ECONOMICS: """
Additional Economics-specific guidelines:
- Focus on economic principles, theories, and models
- Include supply and demand, market structures, and policy
- Emphasize economic reasoning and decision-making
- Cover microeconomics, macroeconomics, and international trade
- Include real-world economic scenarios and data analysis
""",
            Subject.PSYCHOLOGY: """
Additional Psychology-specific guidelines:
- Focus on psychological theories, research methods, and mental processes
- Include cognitive, behavioral, and social psychology concepts
- Emphasize scientific methodology and evidence-based approaches
- Cover developmental, clinical, and experimental psychology
- Include case studies and research findings
"""
        }

        base_prompt = PromptTemplates.get_base_prompt(subject, language)
        subject_enhancement = subject_prompts.get(subject, "")

        return base_prompt + subject_enhancement

    @staticmethod
    def get_translation_prompt(target_language: Language) -> str:
        """Get prompt for translating existing flashcards."""

        return f"""You are a professional translator specializing in educational content. 

Your task is to translate the provided flashcards from English to {target_language.value} while maintaining:
1. Educational accuracy and clarity
2. Appropriate terminology for the target language
3. Cultural and linguistic appropriateness
4. Consistent difficulty levels
5. Preserved topic organization

Translate each flashcard maintaining the same structure and educational value. Ensure that:
- Questions remain clear and test the same concepts
- Answers are comprehensive and accurate in the target language
- Technical terms are properly translated or explained
- The difficulty level remains appropriate for the target language

Please provide the translated flashcards in the same JSON format as the original.
"""

    @staticmethod
    def get_editing_prompt() -> str:
        """Get prompt for editing and improving existing flashcards."""

        return """You are an expert educational content reviewer and editor.

Your task is to review and improve the provided flashcards to ensure they meet high educational standards:

1. **Clarity**: Make questions and answers clearer and more precise
2. **Accuracy**: Verify factual correctness and update if needed
3. **Educational Value**: Ensure each card tests meaningful understanding
4. **Difficulty**: Adjust difficulty levels if they don't match the content
5. **Consistency**: Maintain consistent style and format across all cards

Guidelines for improvements:
- Reword unclear or ambiguous questions
- Expand incomplete or vague answers
- Correct any factual errors
- Adjust difficulty levels appropriately
- Maintain the same topic organization
- Preserve the educational intent

Please provide the improved flashcards in the same JSON format, making only necessary changes.
"""

    @staticmethod
    def get_topic_detection_prompt() -> str:
        """Get prompt for detecting and organizing topics in content."""

        return """You are an expert content analyst specializing in educational material organization.

Your task is to analyze the provided educational content and identify:
1. **Main Topics**: Primary subject areas or themes
2. **Subtopics**: Specific concepts within each main topic
3. **Logical Grouping**: How concepts relate to each other
4. **Hierarchical Structure**: Main topics and their subdivisions

Please provide a structured analysis in JSON format:
{
    "topics": {
        "Main Topic 1": {
            "description": "Brief description of the topic",
            "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3"],
            "key_concepts": ["Concept 1", "Concept 2", "Concept 3"]
        },
        "Main Topic 2": {
            "description": "Brief description of the topic",
            "subtopics": ["Subtopic 1", "Subtopic 2"],
            "key_concepts": ["Concept 1", "Concept 2"]
        }
    },
    "content_summary": "Brief overview of the entire content"
}

This analysis will be used to organize flashcards into logical groups and ensure comprehensive coverage of the material.
"""
