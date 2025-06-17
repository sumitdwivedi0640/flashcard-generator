import json
import csv
import io
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd

from models import Flashcard, FlashcardSet, ExportFormat


class ExportUtils:
    """Utilities for exporting flashcards in various formats."""

    @staticmethod
    def export_to_csv(flashcard_set: FlashcardSet) -> str:
        """
        Export flashcards to CSV format.

        Args:
            flashcard_set: Flashcard set to export

        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Question', 'Answer', 'Difficulty', 'Topic', 'Subject', 'Language'
        ])

        # Write flashcards
        for card in flashcard_set.flashcards:
            writer.writerow([
                card.question,
                card.answer,
                card.difficulty,
                card.topic or '',
                card.subject or '',
                card.language
            ])

        return output.getvalue()

    @staticmethod
    def export_to_json(flashcard_set: FlashcardSet) -> str:
        """
        Export flashcards to JSON format.

        Args:
            flashcard_set: Flashcard set to export

        Returns:
            JSON string
        """
        # Convert to dictionary for JSON serialization
        data = {
            "title": flashcard_set.title,
            "description": flashcard_set.description,
            "subject": flashcard_set.subject,
            "language": flashcard_set.language,
            "created_at": flashcard_set.created_at or datetime.now().isoformat(),
            "flashcards": [
                {
                    "question": card.question,
                    "answer": card.answer,
                    "difficulty": card.difficulty,
                    "topic": card.topic,
                    "subject": card.subject,
                    "language": card.language
                }
                for card in flashcard_set.flashcards
            ]
        }

        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def export_to_anki(flashcard_set: FlashcardSet) -> str:
        """
        Export flashcards to Anki-compatible format.

        Args:
            flashcard_set: Flashcard set to export

        Returns:
            Anki-compatible CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output, delimiter='\t')

        # Write header (Anki format: Front,Back,Tags)
        writer.writerow(['Front', 'Back', 'Tags'])

        # Write flashcards
        for card in flashcard_set.flashcards:
            # Create tags from difficulty, topic, and subject
            tags = []
            if card.difficulty:
                tags.append(f"difficulty:{card.difficulty}")
            if card.topic:
                tags.append(f"topic:{card.topic}")
            if card.subject:
                tags.append(f"subject:{card.subject}")

            tags_str = ' '.join(tags) if tags else ''

            writer.writerow([
                card.question,
                card.answer,
                tags_str
            ])

        return output.getvalue()

    @staticmethod
    def export_to_quizlet(flashcard_set: FlashcardSet) -> str:
        """
        Export flashcards to Quizlet-compatible format.

        Args:
            flashcard_set: Flashcard set to export

        Returns:
            Quizlet-compatible CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header (Quizlet format: Term,Definition)
        writer.writerow(['Term', 'Definition'])

        # Write flashcards
        for card in flashcard_set.flashcards:
            writer.writerow([
                card.question,
                card.answer
            ])

        return output.getvalue()

    @staticmethod
    def export_to_pandas_dataframe(flashcard_set: FlashcardSet) -> pd.DataFrame:
        """
        Export flashcards to pandas DataFrame.

        Args:
            flashcard_set: Flashcard set to export

        Returns:
            Pandas DataFrame
        """
        data = []
        for card in flashcard_set.flashcards:
            data.append({
                'Question': card.question,
                'Answer': card.answer,
                'Difficulty': card.difficulty,
                'Topic': card.topic or '',
                'Subject': card.subject or '',
                'Language': card.language
            })

        return pd.DataFrame(data)

    @staticmethod
    def get_export_filename(flashcard_set: FlashcardSet, format_type: ExportFormat) -> str:
        """
        Generate a filename for export.

        Args:
            flashcard_set: Flashcard set to export
            format_type: Export format

        Returns:
            Generated filename
        """
        # Clean title for filename
        title = flashcard_set.title.replace(
            ' ', '_').replace('/', '_').replace('\\', '_')
        title = ''.join(c for c in title if c.isalnum() or c in '_-')

        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Add format extension
        extensions = {
            ExportFormat.CSV: '.csv',
            ExportFormat.JSON: '.json',
            ExportFormat.ANKI: '.csv',
            ExportFormat.QUIZLET: '.csv'
        }

        extension = extensions.get(format_type, '.txt')

        return f"{title}_{timestamp}{extension}"

    @staticmethod
    def export_flashcards(flashcard_set: FlashcardSet, format_type: ExportFormat) -> tuple[str, str]:
        """
        Export flashcards in the specified format.

        Args:
            flashcard_set: Flashcard set to export
            format_type: Export format

        Returns:
            Tuple of (content, filename)
        """
        exporters = {
            ExportFormat.CSV: ExportUtils.export_to_csv,
            ExportFormat.JSON: ExportUtils.export_to_json,
            ExportFormat.ANKI: ExportUtils.export_to_anki,
            ExportFormat.QUIZLET: ExportUtils.export_to_quizlet
        }

        exporter = exporters.get(format_type)
        if not exporter:
            raise ValueError(f"Unsupported export format: {format_type}")

        content = exporter(flashcard_set)
        filename = ExportUtils.get_export_filename(flashcard_set, format_type)

        return content, filename

    @staticmethod
    def create_summary_report(flashcard_set: FlashcardSet) -> str:
        """
        Create a summary report of the flashcard set.

        Args:
            flashcard_set: Flashcard set to analyze

        Returns:
            Summary report string
        """
        total_cards = len(flashcard_set.flashcards)

        # Count by difficulty
        difficulty_counts = {}
        for card in flashcard_set.flashcards:
            difficulty = card.difficulty
            difficulty_counts[difficulty] = difficulty_counts.get(
                difficulty, 0) + 1

        # Count by topic
        topic_counts = {}
        for card in flashcard_set.flashcards:
            topic = card.topic or 'Uncategorized'
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        # Generate report
        report = f"""
Flashcard Set Summary
====================

Title: {flashcard_set.title}
Description: {flashcard_set.description or 'No description provided'}
Subject: {flashcard_set.subject or 'Not specified'}
Language: {flashcard_set.language}
Created: {flashcard_set.created_at or 'Unknown'}

Statistics:
- Total Cards: {total_cards}

Difficulty Distribution:
"""

        for difficulty, count in difficulty_counts.items():
            percentage = (count / total_cards) * 100
            report += f"- {difficulty}: {count} cards ({percentage:.1f}%)\n"

        report += "\nTopic Distribution:\n"
        for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_cards) * 100
            report += f"- {topic}: {count} cards ({percentage:.1f}%)\n"

        return report

    @staticmethod
    def validate_export_data(flashcard_set: FlashcardSet) -> tuple[bool, str]:
        """
        Validate flashcard set data before export.

        Args:
            flashcard_set: Flashcard set to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not flashcard_set.flashcards:
            return False, "No flashcards to export"

        for i, card in enumerate(flashcard_set.flashcards):
            if not card.question.strip():
                return False, f"Flashcard {i+1} has an empty question"
            if not card.answer.strip():
                return False, f"Flashcard {i+1} has an empty answer"

        return True, ""

    @staticmethod
    def get_export_preview(flashcard_set: FlashcardSet, format_type: ExportFormat, max_lines: int = 10) -> str:
        """
        Get a preview of the export content.

        Args:
            flashcard_set: Flashcard set to preview
            format_type: Export format
            max_lines: Maximum number of lines to show

        Returns:
            Preview string
        """
        try:
            content, _ = ExportUtils.export_flashcards(
                flashcard_set, format_type)
            lines = content.split('\n')

            if len(lines) <= max_lines:
                return content

            preview_lines = lines[:max_lines]
            preview_lines.append(
                f"... (showing {max_lines} of {len(lines)} lines)")

            return '\n'.join(preview_lines)

        except Exception as e:
            return f"Error generating preview: {str(e)}"
