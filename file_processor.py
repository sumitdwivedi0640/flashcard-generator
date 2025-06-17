import PyPDF2
import io
from typing import Optional, Tuple
import streamlit as st


class FileProcessor:
    """Handles file upload and text extraction from various file formats."""

    @staticmethod
    def extract_text_from_pdf(pdf_file) -> Tuple[bool, str, Optional[str]]:
        """
        Extract text from a PDF file.

        Args:
            pdf_file: Uploaded PDF file object

        Returns:
            Tuple of (success: bool, text: str, error_message: Optional[str])
        """
        try:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Extract text from all pages
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"

            if not text.strip():
                return False, "", "No text could be extracted from the PDF. The file might be scanned or image-based."

            return True, text.strip(), None

        except Exception as e:
            return False, "", f"Error processing PDF file: {str(e)}"

    @staticmethod
    def extract_text_from_txt(txt_file) -> Tuple[bool, str, Optional[str]]:
        """
        Extract text from a TXT file.

        Args:
            txt_file: Uploaded TXT file object

        Returns:
            Tuple of (success: bool, text: str, error_message: Optional[str])
        """
        try:
            # Read the text content
            text = txt_file.read().decode('utf-8')

            if not text.strip():
                return False, "", "The text file appears to be empty."

            return True, text.strip(), None

        except UnicodeDecodeError:
            try:
                # Try with a different encoding
                txt_file.seek(0)  # Reset file pointer
                text = txt_file.read().decode('latin-1')
                return True, text.strip(), None
            except Exception as e:
                return False, "", f"Error reading text file with different encoding: {str(e)}"
        except Exception as e:
            return False, "", f"Error processing text file: {str(e)}"

    @staticmethod
    def process_uploaded_file(uploaded_file) -> Tuple[bool, str, Optional[str]]:
        """
        Process an uploaded file and extract text content.

        Args:
            uploaded_file: Streamlit uploaded file object

        Returns:
            Tuple of (success: bool, text: str, error_message: Optional[str])
        """
        if uploaded_file is None:
            return False, "", "No file was uploaded."

        file_type = uploaded_file.type.lower()

        if file_type == "application/pdf":
            return FileProcessor.extract_text_from_pdf(uploaded_file)
        elif file_type == "text/plain":
            return FileProcessor.extract_text_from_txt(uploaded_file)
        else:
            return False, "", f"Unsupported file type: {file_type}. Please upload a PDF or TXT file."

    @staticmethod
    def validate_text_content(text: str, min_length: int = 100) -> Tuple[bool, Optional[str]]:
        """
        Validate the extracted text content.

        Args:
            text: Extracted text content
            min_length: Minimum required text length

        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        if not text or not text.strip():
            return False, "No text content found."

        if len(text.strip()) < min_length:
            return False, f"Text content is too short. Please provide at least {min_length} characters."

        # Check if text contains meaningful content (not just whitespace or special characters)
        meaningful_chars = sum(1 for char in text if char.isalnum())
        if meaningful_chars < min_length * 0.5:
            return False, "Text content appears to contain mostly non-alphanumeric characters."

        return True, None

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and preprocess extracted text.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # Remove leading/trailing whitespace
            line = line.strip()
            if line:  # Keep non-empty lines
                cleaned_lines.append(line)

        # Join lines with single newlines
        cleaned_text = '\n'.join(cleaned_lines)

        # Remove excessive spaces between words
        import re
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

        return cleaned_text.strip()

    @staticmethod
    def get_file_info(uploaded_file) -> dict:
        """
        Get information about the uploaded file.

        Args:
            uploaded_file: Streamlit uploaded file object

        Returns:
            Dictionary containing file information
        """
        if uploaded_file is None:
            return {}

        return {
            "name": uploaded_file.name,
            "type": uploaded_file.type,
            "size": uploaded_file.size,
            "size_mb": round(uploaded_file.size / (1024 * 1024), 2)
        }

    @staticmethod
    def create_sample_content() -> str:
        """
        Create sample educational content for testing purposes.

        Returns:
            Sample educational text
        """
        return """Cell Biology: The Foundation of Life

Cells are the basic units of life, and understanding their structure and function is fundamental to biology. All living organisms are composed of cells, which can be either prokaryotic or eukaryotic.

Prokaryotic cells, found in bacteria and archaea, are simpler in structure. They lack a true nucleus and membrane-bound organelles. Their genetic material is contained in a nucleoid region, and they have a cell wall, cell membrane, and cytoplasm. Some prokaryotes also have flagella for movement and pili for attachment.

Eukaryotic cells, found in plants, animals, fungi, and protists, are more complex. They have a true nucleus that contains the cell's DNA, surrounded by a nuclear envelope. Eukaryotic cells also contain various membrane-bound organelles, each with specific functions.

The nucleus is the control center of the cell, containing the genetic material (DNA) that directs all cellular activities. The nuclear envelope is a double membrane that separates the nucleus from the cytoplasm and contains nuclear pores for the exchange of materials.

Mitochondria are often called the "powerhouses" of the cell because they produce energy through cellular respiration. They have their own DNA and can replicate independently. The process of cellular respiration converts glucose and oxygen into ATP (adenosine triphosphate), the cell's energy currency.

The endoplasmic reticulum (ER) is a network of membranes that extends throughout the cell. Rough ER has ribosomes attached to its surface and is involved in protein synthesis. Smooth ER lacks ribosomes and is involved in lipid synthesis, detoxification, and calcium storage.

The Golgi apparatus is responsible for processing, packaging, and distributing proteins and lipids. It receives materials from the ER, modifies them, and packages them into vesicles for transport to their final destinations.

Lysosomes are membrane-bound organelles that contain digestive enzymes. They break down cellular waste, foreign materials, and worn-out organelles through a process called autophagy.

The cell membrane, also called the plasma membrane, is a selectively permeable barrier that surrounds the cell. It controls what enters and leaves the cell and is composed of a phospholipid bilayer with embedded proteins.

In plant cells, the cell wall provides structural support and protection. It is composed primarily of cellulose and is located outside the cell membrane. Plant cells also contain chloroplasts, which are responsible for photosynthesis and contain the green pigment chlorophyll.

The cytoskeleton is a network of protein filaments that provides structural support, enables cell movement, and helps organize cellular components. It consists of microtubules, microfilaments, and intermediate filaments.

Cell division is essential for growth, repair, and reproduction. In eukaryotic cells, this process occurs through mitosis (for somatic cells) or meiosis (for gametes). Mitosis results in two identical daughter cells, while meiosis produces four genetically diverse gametes.

Understanding cell biology is crucial for many fields, including medicine, genetics, biotechnology, and ecology. It provides the foundation for understanding how organisms function, how diseases develop, and how life evolves."""
