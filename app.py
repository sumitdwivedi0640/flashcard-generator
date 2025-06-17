import streamlit as st
import os
from datetime import datetime
from typing import List, Dict, Optional

from models import (
    Flashcard, FlashcardSet, GenerationRequest, GenerationResponse,
    Subject, Language, DifficultyLevel, ExportFormat
)
from flashcard_generator import FlashcardGenerator
from file_processor import FileProcessor
from export_utils import ExportUtils

# Page configuration
st.set_page_config(
    page_title="LLM-Powered Flashcard Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .flashcard-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .difficulty-easy { color: #28a745; font-weight: bold; }
    .difficulty-medium { color: #ffc107; font-weight: bold; }
    .difficulty-hard { color: #dc3545; font-weight: bold; }
    .topic-badge {
        background-color: #e9ecef;
        color: #495057;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'flashcard_set' not in st.session_state:
    st.session_state.flashcard_set = None
if 'generator' not in st.session_state:
    st.session_state.generator = None
if 'current_flashcards' not in st.session_state:
    st.session_state.current_flashcards = []

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))


def initialize_generator():
    """Initialize the flashcard generator."""
    try:
        if st.session_state.generator is None:
            st.session_state.generator = FlashcardGenerator()
        return True
    except Exception as e:
        st.error(f"Failed to initialize generator: {str(e)}")
        return False


def main():
    """Main application function."""

    # Header
    st.markdown('<h1 class="main-header">🎓 LLM-Powered Flashcard Generator</h1>',
                unsafe_allow_html=True)
    st.markdown(
        "Transform educational content into effective flashcards using AI")

    # Sidebar for configuration
    with st.sidebar:
        st.markdown('<h3 class="sub-header">⚙️ Configuration</h3>',
                    unsafe_allow_html=True)

        # Subject selection
        subject = st.selectbox(
            "Subject (Optional)",
            ["Select a subject..."] + [s.value for s in Subject],
            help="Select a subject to improve flashcard relevance"
        )

        # Language selection
        language = st.selectbox(
            "Language",
            [lang.value for lang in Language],
            index=0,
            help="Language for generated flashcards"
        )

        # Number of cards
        num_cards = st.slider(
            "Number of Flashcards",
            min_value=5,
            max_value=50,
            value=15,
            help="Number of flashcards to generate"
        )

        # Advanced options
        with st.expander("Advanced Options"):
            include_difficulty = st.checkbox(
                "Include Difficulty Levels", value=True)
            include_topics = st.checkbox("Include Topic Grouping", value=True)
            model_temperature = st.slider(
                "Creativity Level", 0.1, 1.0, 0.7, 0.1)

    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📝 Input", "🎯 Generate", "✏️ Edit", "📤 Export"])

    with tab1:
        input_tab(subject, language, num_cards, include_difficulty,
                  include_topics, model_temperature)

    with tab2:
        generate_tab()

    with tab3:
        edit_tab()

    with tab4:
        export_tab()


def input_tab(subject, language, num_cards, include_difficulty, include_topics, model_temperature):
    """Input tab for content upload and text input."""

    st.markdown('<h2 class="sub-header">📝 Input Educational Content</h2>',
                unsafe_allow_html=True)

    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["📄 Upload File", "📝 Paste Text", "🧪 Sample Content"],
        horizontal=True
    )

    content = ""

    if input_method == "📄 Upload File":
        uploaded_file = st.file_uploader(
            "Upload your educational content",
            type=['txt', 'pdf'],
            help="Upload a text or PDF file containing educational content"
        )

        if uploaded_file:
            # Show file info
            file_info = FileProcessor.get_file_info(uploaded_file)
            if file_info:
                st.info(
                    f"📁 File: {file_info['name']} ({file_info['size_mb']} MB)")

            # Process file
            success, extracted_text, error = FileProcessor.process_uploaded_file(
                uploaded_file)

            if success:
                # Clean and validate text
                cleaned_text = FileProcessor.clean_text(extracted_text)
                is_valid, validation_error = FileProcessor.validate_text_content(
                    cleaned_text)

                if is_valid:
                    content = cleaned_text
                    st.success("✅ File processed successfully!")
                    st.text_area("Extracted Content Preview", cleaned_text[:500] + "..." if len(
                        cleaned_text) > 500 else cleaned_text, height=200, disabled=True)
                else:
                    st.error(f"❌ {validation_error}")
            else:
                st.error(f"❌ {error}")

    elif input_method == "📝 Paste Text":
        content = st.text_area(
            "Paste your educational content here",
            height=300,
            placeholder="Paste your textbook excerpt, lecture notes, or any educational content here..."
        )

        if content:
            # Validate content
            is_valid, validation_error = FileProcessor.validate_text_content(
                content)
            if not is_valid:
                st.error(f"❌ {validation_error}")

    elif input_method == "🧪 Sample Content":
        sample_content = FileProcessor.create_sample_content()
        content = st.text_area(
            "Sample Biology Content",
            sample_content,
            height=300,
            disabled=True
        )
        st.info(
            "This is sample content about cell biology. You can modify it or use it as-is for testing.")

    # Store content in session state
    if content:
        st.session_state.input_content = content
        st.session_state.input_subject = Subject(subject) if subject in [
            s.value for s in Subject] else None
        st.session_state.input_language = Language(language) if language in [
            l.value for l in Language] else Language.ENGLISH
        st.session_state.input_num_cards = num_cards
        st.session_state.input_include_difficulty = include_difficulty
        st.session_state.input_include_topics = include_topics
        st.session_state.input_temperature = model_temperature

        st.success(
            "✅ Content ready for generation! Switch to the 'Generate' tab to create flashcards.")


def generate_tab():
    """Generate tab for flashcard creation."""

    st.markdown('<h2 class="sub-header">🎯 Generate Flashcards</h2>',
                unsafe_allow_html=True)

    # Check if content is available
    if 'input_content' not in st.session_state:
        st.warning("⚠️ Please provide content in the 'Input' tab first.")
        return

    # Initialize generator
    if not initialize_generator():
        return

    # Display generation parameters
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Subject", get_enum_value(st.session_state.input_subject)
                  if st.session_state.input_subject else "Not specified")
    with col2:
        st.metric("Language", get_enum_value(st.session_state.input_language))
    with col3:
        st.metric("Target Cards", st.session_state.input_num_cards)

    # Generate button
    if st.button("🚀 Generate Flashcards", type="primary", use_container_width=True):
        with st.spinner("Generating flashcards..."):
            try:
                # Create generation request
                request = GenerationRequest(
                    content=st.session_state.input_content,
                    subject=st.session_state.input_subject,
                    language=st.session_state.input_language,
                    num_cards=st.session_state.input_num_cards,
                    include_difficulty=st.session_state.input_include_difficulty,
                    include_topics=st.session_state.input_include_topics
                )

                # Generate flashcards
                response = st.session_state.generator.generate_flashcards(
                    request)

                if response.success:
                    st.session_state.current_flashcards = response.flashcards

                    # Create flashcard set
                    flashcard_set = FlashcardSet(
                        title=f"Generated Flashcards - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        description=f"Generated from {get_enum_value(st.session_state.input_subject) if st.session_state.input_subject else 'general'} content",
                        subject=st.session_state.input_subject,
                        language=st.session_state.input_language,
                        flashcards=response.flashcards,
                        created_at=datetime.now().isoformat()
                    )

                    st.session_state.flashcard_set = flashcard_set

                    # Display success message
                    st.success(
                        f"✅ Successfully generated {len(response.flashcards)} flashcards in {response.processing_time:.2f} seconds!")

                    # Display flashcards
                    display_flashcards(response.flashcards, response.topics)

                else:
                    st.error(f"❌ Generation failed: {response.error_message}")

            except Exception as e:
                st.error(f"❌ Error during generation: {str(e)}")

    # Display existing flashcards if available
    elif st.session_state.current_flashcards:
        st.info("📋 Previously generated flashcards:")
        display_flashcards(st.session_state.current_flashcards)


def display_flashcards(flashcards: List[Flashcard], topics: Dict[str, List[int]] = None):
    """Display flashcards in an organized manner."""

    if not flashcards:
        st.warning("No flashcards to display.")
        return

    # Group by topic if available
    if topics and len(topics) > 1:
        for topic, indices in topics.items():
            if indices:  # Only show topics with cards
                st.markdown(f"### 📚 {topic}")
                for idx in indices:
                    if idx < len(flashcards):
                        display_single_flashcard(flashcards[idx], idx + 1)
                st.divider()
    else:
        # Display all flashcards
        for i, flashcard in enumerate(flashcards):
            display_single_flashcard(flashcard, i + 1)


def display_single_flashcard(flashcard: Flashcard, card_number: int):
    """Display a single flashcard."""

    # Difficulty color class
    difficulty_class = f"difficulty-{flashcard.difficulty.lower()}"

    st.markdown(f"""
    <div class="flashcard-box" style="color: #000;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: bold; color: #6c757d;">Card #{card_number}</span>
            <span class="{difficulty_class}">{flashcard.difficulty}</span>
        </div>
        <div style="margin-bottom: 0.5rem; color: #000;">
            <strong>Q:</strong> {flashcard.question}
        </div>
        <div style="margin-bottom: 0.5rem; color: #000;">
            <strong>A:</strong> {flashcard.answer}
        </div>
        <div style="display: flex; align-items: center;">
            <span class="topic-badge">📂 {flashcard.topic or 'General'}</span>
            <span class="topic-badge">🌐 {flashcard.language}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def edit_tab():
    """Edit tab for modifying flashcards."""

    st.markdown('<h2 class="sub-header">✏️ Edit Flashcards</h2>',
                unsafe_allow_html=True)

    if not st.session_state.current_flashcards:
        st.warning(
            "⚠️ No flashcards available for editing. Generate some flashcards first.")
        return

    # Edit options
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔧 Improve All Flashcards", use_container_width=True):
            with st.spinner("Improving flashcards..."):
                try:
                    improved_flashcards = st.session_state.generator.improve_flashcards(
                        st.session_state.current_flashcards)
                    st.session_state.current_flashcards = improved_flashcards
                    st.session_state.flashcard_set.flashcards = improved_flashcards
                    st.success("✅ Flashcards improved successfully!")
                except Exception as e:
                    st.error(f"❌ Error improving flashcards: {str(e)}")

    with col2:
        target_language = st.selectbox(
            "Translate to:",
            [lang.value for lang in Language],
            index=0,
            key="translate_language"
        )

        if st.button("🌐 Translate Flashcards", use_container_width=True):
            with st.spinner("Translating flashcards..."):
                try:
                    translated_flashcards = st.session_state.generator.translate_flashcards(
                        st.session_state.current_flashcards,
                        Language(target_language)
                    )
                    st.session_state.current_flashcards = translated_flashcards
                    st.session_state.flashcard_set.flashcards = translated_flashcards
                    st.success(
                        f"✅ Flashcards translated to {target_language}!")
                except Exception as e:
                    st.error(f"❌ Error translating flashcards: {str(e)}")

    # Individual flashcard editing
    st.markdown("### 📝 Edit Individual Flashcards")

    for i, flashcard in enumerate(st.session_state.current_flashcards):
        with st.expander(f"Card #{i+1}: {flashcard.question[:50]}..."):
            col1, col2 = st.columns(2)

            with col1:
                new_question = st.text_area(
                    "Question", flashcard.question, key=f"q_{i}")
                new_difficulty = st.selectbox(
                    "Difficulty",
                    [d.value for d in DifficultyLevel],
                    index=[d.value for d in DifficultyLevel].index(
                        flashcard.difficulty),
                    key=f"d_{i}"
                )

            with col2:
                new_answer = st.text_area(
                    "Answer", flashcard.answer, key=f"a_{i}")
                new_topic = st.text_input(
                    "Topic", flashcard.topic or "", key=f"t_{i}")

            # Update flashcard
            if st.button(f"💾 Save Card #{i+1}", key=f"save_{i}"):
                flashcard.question = new_question
                flashcard.answer = new_answer
                flashcard.difficulty = DifficultyLevel(new_difficulty)
                flashcard.topic = new_topic if new_topic else None
                st.success(f"✅ Card #{i+1} updated!")


def export_tab():
    """Export tab for downloading flashcards."""

    st.markdown('<h2 class="sub-header">📤 Export Flashcards</h2>',
                unsafe_allow_html=True)

    if not st.session_state.flashcard_set:
        st.warning(
            "⚠️ No flashcards available for export. Generate some flashcards first.")
        return

    # Display summary
    st.markdown("### 📊 Flashcard Set Summary")
    summary = ExportUtils.create_summary_report(st.session_state.flashcard_set)
    st.text(summary)

    # Export options
    st.markdown("### 📤 Export Options")

    col1, col2 = st.columns(2)

    with col1:
        export_format = st.selectbox(
            "Export Format",
            [format.value for format in ExportFormat],
            help="Choose the format for your exported flashcards"
        )

        # Validate export data
        is_valid, error_msg = ExportUtils.validate_export_data(
            st.session_state.flashcard_set)

        if not is_valid:
            st.error(f"❌ {error_msg}")
            return

        # Export button
        if st.button("📥 Export Flashcards", type="primary", use_container_width=True):
            try:
                content, filename = ExportUtils.export_flashcards(
                    st.session_state.flashcard_set,
                    ExportFormat(export_format)
                )

                # Create download button
                st.download_button(
                    label=f"💾 Download {filename}",
                    data=content,
                    file_name=filename,
                    mime="text/plain" if export_format == "json" else "text/csv",
                    use_container_width=True
                )

                st.success(f"✅ Export ready! Click the download button above.")

            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")

    with col2:
        # Preview
        st.markdown("### 👀 Export Preview")
        preview = ExportUtils.get_export_preview(
            st.session_state.flashcard_set,
            ExportFormat(export_format),
            max_lines=15
        )
        st.code(preview, language="text")


def get_enum_value(val):
    return val.value if hasattr(val, 'value') else val


if __name__ == "__main__":
    main()
