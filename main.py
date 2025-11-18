#!/usr/bin/env python3
"""
AI Content Management - CLI Application

This is the main entry point for the command-line interface.
Users interact with this file to perform text analysis tasks:
- Summarization (summary + key points extraction)
- Translation (to any language, preserving tone)
- Sentiment Analysis (positive/neutral/negative with confidence)

The CLI provides:
- Colored terminal output for better UX
- Input validation for file paths
- Progress indicators during processing
- Clear display of results
- Automatic saving to timestamped JSON files
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
# This allows us to import from src/ without installing the package
sys.path.insert(0, str(Path(__file__).parent))

from src.processors import TextProcessor, ProcessorError
from src.output_manager import OutputManager, OutputManagerError


class Colors:
    """
    ANSI color codes for terminal output.
    
    These codes work on most Unix/Linux/Mac terminals. On Windows,
    they work in Windows Terminal and newer command prompts.
    
    Usage:
        print(f"{Colors.RED}Error message{Colors.ENDC}")
    """
    HEADER = '\033[95m'  # Purple/magenta
    BLUE = '\033[94m'    # Blue
    GREEN = '\033[92m'   # Green
    YELLOW = '\033[93m'  # Yellow
    RED = '\033[91m'     # Red
    ENDC = '\033[0m'     # Reset to default color
    BOLD = '\033[1m'     # Bold text


class CLI:
    """
    Command-line interface for AI Content Management.
    
    This class handles all user interaction:
    - Displaying menus and prompts
    - Validating user input
    - Showing progress and results
    - Error handling and recovery
    
    The CLI uses colored output to make the interface more user-friendly
    and guide users through each workflow.
    """
    
    def __init__(self):
        """
        Initialize the CLI.
        
        The processor is initialized lazily (on first use) to avoid
        failing early if the API key is missing. This allows us to
        show a better error message when the user actually tries to
        perform an operation.
        """
        self.processor = None
    
    def print_welcome(self):
        """
        Display welcome banner when application starts.
        
        This provides branding and shows users what the application does.
        """
        print("\n" + "=" * 60)
        print(f"{Colors.HEADER}{Colors.BOLD}  AI Content Management System{Colors.ENDC}")
        print("=" * 60)
        print(f"{Colors.BLUE}  Text Analysis powered by OpenAI GPT-5-Nano{Colors.ENDC}")
        print("=" * 60 + "\n")
    
    def print_menu(self):
        """
        Display the main menu with available actions.
        
        Uses numbered options for easy selection and color-coding
        to make the menu visually clear.
        """
        print(f"\n{Colors.BOLD}Available Actions:{Colors.ENDC}")
        print(f"  {Colors.GREEN}1.{Colors.ENDC} Summarize - Generate summary and key points")
        print(f"  {Colors.GREEN}2.{Colors.ENDC} Translate - Translate text to another language")
        print(f"  {Colors.GREEN}3.{Colors.ENDC} Sentiment - Analyze sentiment and tone")
        print(f"  {Colors.GREEN}4.{Colors.ENDC} Exit\n")
    
    def get_file_path(self) -> str:
        """
        Prompt user for file path and thoroughly validate it.
        
        This provides a user-friendly validation loop that:
        - Checks if file exists
        - Verifies it's a file (not a directory)
        - Validates file extension (.txt or .pdf only)
        - Allows retry on errors
        - Expands ~/ to user's home directory
        
        Returns:
            Validated file path string, or None if user cancels
            
        User Experience:
            - Clear error messages for each validation failure
            - Opportunity to retry after each error
            - Graceful exit option if they want to cancel
        """
        while True:
            print(f"{Colors.BOLD}Enter file path:{Colors.ENDC}")
            file_path = input(f"{Colors.BLUE}> {Colors.ENDC}").strip()
            
            # Validation 1: Not empty
            if not file_path:
                print(f"{Colors.RED}Error: File path cannot be empty{Colors.ENDC}")
                continue
            
            # Expand ~ to user's home directory (e.g., ~/file.txt -> /home/user/file.txt)
            # This makes it easier for users to reference files in their home directory
            file_path = os.path.expanduser(file_path)
            
            # Validation 2: File exists
            if not os.path.exists(file_path):
                print(f"{Colors.RED}Error: File not found: {file_path}{Colors.ENDC}")
                retry = input(f"Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return None  # User cancelled
                continue
            
            # Validation 3: Is a file (not a directory)
            if not os.path.isfile(file_path):
                print(f"{Colors.RED}Error: Path is not a file: {file_path}{Colors.ENDC}")
                retry = input(f"Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return None
                continue
            
            # Validation 4: Supported file type
            # Extract extension (e.g., "article.txt" -> ".txt")
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in ['.txt', '.pdf']:
                print(f"{Colors.RED}Error: Unsupported file type: {ext}{Colors.ENDC}")
                print(f"{Colors.YELLOW}Supported types: .txt, .pdf{Colors.ENDC}")
                retry = input(f"Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return None
                continue
            
            # All validations passed!
            return file_path
    
    def get_menu_choice(self) -> str:
        """
        Get and validate user's menu choice.
        
        Loops until valid input (1-4) is provided. This prevents crashes
        from invalid input and guides users to valid options.
        
        Returns:
            String "1", "2", "3", or "4" (validated choice)
        """
        while True:
            choice = input(f"{Colors.BOLD}Select option (1-4):{Colors.ENDC} ").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            # Invalid input - show error and loop again
            print(f"{Colors.RED}Invalid choice. Please enter 1, 2, 3, or 4.{Colors.ENDC}")
    
    def show_progress(self, message: str):
        """
        Display a progress/working indicator.
        
        Args:
            message: What operation is currently happening
            
        Visual: "⚙ Reading file..."
        """
        print(f"{Colors.YELLOW}⚙ {message}...{Colors.ENDC}")
    
    def show_success(self, message: str):
        """
        Display a success message with checkmark.
        
        Args:
            message: What succeeded
            
        Visual: "✓ Processing complete"
        """
        print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")
    
    def show_error(self, message: str):
        """
        Display an error message with X mark.
        
        Args:
            message: Error description
            
        Visual: "✗ Error: File not found"
        """
        print(f"{Colors.RED}✗ Error: {message}{Colors.ENDC}")
    
    def display_result(self, result: dict, use_case: str):
        """
        Display processing results in the terminal with nice formatting.
        
        This formats results differently based on the use case:
        - Summarize: Shows summary paragraph + numbered key points
        - Translate: Shows source→target languages + translated text
        - Sentiment: Shows color-coded sentiment + confidence percentage + explanation
        
        Args:
            result: The result dictionary from the processor (varies by use case)
            use_case: Type of operation ('summarize', 'translate', or 'sentiment')
            
        Example output for sentiment:
            ==============================================================
            RESULTS
            ==============================================================
            
            Sentiment: POSITIVE
            Confidence: 92.50%
            Explanation:
            The text uses strong positive language like "excellent" and "love"
            
            ==============================================================
        """
        print("\n" + "=" * 60)
        print(f"{Colors.HEADER}{Colors.BOLD}RESULTS{Colors.ENDC}")
        print("=" * 60 + "\n")
        
        if use_case == 'summarize':
            # Display summary paragraph
            print(f"{Colors.BOLD}Summary:{Colors.ENDC}")
            print(result['summary'])
            
            # Display key points as numbered list
            print(f"\n{Colors.BOLD}Key Points:{Colors.ENDC}")
            for i, point in enumerate(result['key_points'], 1):
                print(f"  {i}. {point}")
        
        elif use_case == 'translate':
            # Show translation metadata
            print(f"{Colors.BOLD}Source Language:{Colors.ENDC} {result.get('source_language', 'N/A')}")
            print(f"{Colors.BOLD}Target Language:{Colors.ENDC} {result['target_language']}")
            
            # Show the translated text
            print(f"\n{Colors.BOLD}Translation:{Colors.ENDC}")
            print(result['translated_text'])
        
        elif use_case == 'sentiment':
            sentiment = result['sentiment']
            confidence = result['confidence']
            
            # Color-code the sentiment for visual impact
            # Green = positive, Red = negative, Yellow = neutral
            sentiment_color = Colors.GREEN if sentiment == 'positive' else \
                            Colors.RED if sentiment == 'negative' else Colors.YELLOW
            
            print(f"{Colors.BOLD}Sentiment:{Colors.ENDC} {sentiment_color}{sentiment.upper()}{Colors.ENDC}")
            print(f"{Colors.BOLD}Confidence:{Colors.ENDC} {confidence:.2%}")  # Format as percentage (0.95 -> 95.00%)
            print(f"{Colors.BOLD}Explanation:{Colors.ENDC}")
            print(result['explanation'])
        
        print("\n" + "=" * 60 + "\n")
    
    def process_summarization(self, file_path: str):
        """
        Execute the complete summarization workflow with user feedback.
        
        Workflow:
        1. Show progress indicators for each step
        2. Call the processor to do the actual work
        3. Display results in the terminal
        4. Save results to JSON file
        5. Handle any errors gracefully
        
        Args:
            file_path: Path to the file to summarize
            
        User sees:
            ⚙ Reading file...
            ⚙ Detecting language...
            ⚙ Generating summary...
            ✓ Processing complete
            [RESULTS DISPLAYED]
            ⚙ Saving results...
            ✓ Results saved to: output/file_summarize_2024-01-15_14-30-00.json
        """
        try:
            # Progress feedback: Let user know what's happening
            self.show_progress("Reading file")
            self.show_progress("Detecting language")
            self.show_progress("Generating summary")
            
            # Do the actual processing (this takes time - API calls involved)
            result = self.processor.process_summarization(file_path)
            
            self.show_success("Processing complete")
            
            # Display the results in a formatted way
            self.display_result(result['result'], 'summarize')
            
            # Save to JSON file for later reference
            self.show_progress("Saving results")
            output_path = OutputManager.save_from_processor_result(result)
            self.show_success(f"Results saved to: {output_path}")
            
        except ProcessorError as e:
            # Processing failed (file reading, API call, etc.)
            self.show_error(str(e))
        except OutputManagerError as e:
            # Processing succeeded but saving failed
            self.show_error(f"Failed to save output: {str(e)}")
        except Exception as e:
            # Unexpected error - catch-all for safety
            self.show_error(f"Unexpected error: {str(e)}")
    
    def process_translation(self, file_path: str):
        """
        Execute the complete translation workflow with user feedback.
        
        Unlike summarization, this requires an additional user input:
        the target language. We collect that first, validate it,
        then proceed with the workflow.
        
        Args:
            file_path: Path to the file to translate
            
        User experience:
            1. Prompted for target language
            2. Progress feedback during processing
            3. Results displayed showing source→target
            4. Results saved to JSON
        """
        # Get target language from user
        print(f"\n{Colors.BOLD}Enter target language (e.g., Spanish, French, German):{Colors.ENDC}")
        target_language = input(f"{Colors.BLUE}> {Colors.ENDC}").strip()
        
        # Validate input
        if not target_language:
            self.show_error("Target language cannot be empty")
            return  # Abort this operation
        
        try:
            # Progress feedback
            self.show_progress("Reading file")
            self.show_progress("Detecting source language")
            self.show_progress(f"Translating to {target_language}")
            
            # Do the actual processing
            result = self.processor.process_translation(file_path, target_language)
            
            self.show_success("Processing complete")
            
            # Display the translation
            self.display_result(result['result'], 'translate')
            
            # Save to JSON file
            self.show_progress("Saving results")
            output_path = OutputManager.save_from_processor_result(result)
            self.show_success(f"Results saved to: {output_path}")
            
        except ProcessorError as e:
            self.show_error(str(e))
        except OutputManagerError as e:
            self.show_error(f"Failed to save output: {str(e)}")
        except Exception as e:
            self.show_error(f"Unexpected error: {str(e)}")
    
    def process_sentiment(self, file_path: str):
        """
        Execute the complete sentiment analysis workflow with user feedback.
        
        Workflow is similar to summarization but analyzes emotional tone
        instead of creating a summary.
        
        Args:
            file_path: Path to the file to analyze
            
        User sees:
            ⚙ Reading file...
            ⚙ Detecting language...
            ⚙ Analyzing sentiment...
            ✓ Processing complete
            [SENTIMENT RESULTS WITH COLOR-CODED OUTPUT]
            ⚙ Saving results...
            ✓ Results saved to: output/file_sentiment_2024-01-15_14-30-00.json
        """
        try:
            # Progress feedback
            self.show_progress("Reading file")
            self.show_progress("Detecting language")
            self.show_progress("Analyzing sentiment")
            
            # Do the actual processing
            result = self.processor.process_sentiment(file_path)
            
            self.show_success("Processing complete")
            
            # Display the sentiment analysis
            self.display_result(result['result'], 'sentiment')
            
            # Save to JSON file
            self.show_progress("Saving results")
            output_path = OutputManager.save_from_processor_result(result)
            self.show_success(f"Results saved to: {output_path}")
            
        except ProcessorError as e:
            self.show_error(str(e))
        except OutputManagerError as e:
            self.show_error(f"Failed to save output: {str(e)}")
        except Exception as e:
            self.show_error(f"Unexpected error: {str(e)}")
    
    def run(self):
        """
        Main application loop - orchestrates the entire CLI experience.
        
        Flow:
        1. Display welcome message
        2. Initialize the AI processor (validates API key early)
        3. Loop: Show menu → Get choice → Process file → Ask to continue
        4. Exit gracefully when user chooses to quit
        
        This is the heart of the application that ties everything together.
        """
        # Display welcome banner
        self.print_welcome()
        
        # Initialize processor (this validates API key)
        # We do this early to fail fast if the API key is missing/invalid
        try:
            self.show_progress("Initializing AI client")
            self.processor = TextProcessor()
            self.show_success("Ready")
        except ProcessorError as e:
            # API key missing or invalid - show helpful error
            self.show_error(str(e))
            print(f"\n{Colors.YELLOW}Please ensure your .env file is configured with a valid OPENAI_API_KEY{Colors.ENDC}")
            sys.exit(1)
        
        # Main application loop
        # Continues until user chooses to exit (option 4) or says 'n' to continue
        while True:
            # Show the menu of available operations
            self.print_menu()
            
            # Get and validate user's menu choice (1-4)
            choice = self.get_menu_choice()
            
            # Handle exit option
            if choice == '4':
                print(f"\n{Colors.GREEN}Thank you for using AI Content Management!{Colors.ENDC}\n")
                sys.exit(0)
            
            # Get file path from user (with validation)
            print()
            file_path = self.get_file_path()
            
            # User cancelled file selection - go back to menu
            if file_path is None:
                continue
            
            print()
            
            # Route to appropriate processing workflow based on choice
            if choice == '1':
                self.process_summarization(file_path)
            elif choice == '2':
                self.process_translation(file_path)
            elif choice == '3':
                self.process_sentiment(file_path)
            
            # Ask if user wants to process another file
            print()
            continue_choice = input(f"{Colors.BOLD}Process another file? (y/n):{Colors.ENDC} ").strip().lower()
            if continue_choice != 'y':
                print(f"\n{Colors.GREEN}Thank you for using AI Content Management!{Colors.ENDC}\n")
                break  # Exit the loop


def main():
    """
    Application entry point with top-level error handling.
    
    Handles:
    - Normal operation (create and run CLI)
    - Keyboard interrupt (Ctrl+C) - exit gracefully
    - Unexpected fatal errors - show error message
    
    This is what gets called when you run: python main.py
    """
    try:
        # Create CLI instance and start the main loop
        cli = CLI()
        cli.run()
    except KeyboardInterrupt:
        # User pressed Ctrl+C - exit cleanly without stack trace
        print(f"\n\n{Colors.YELLOW}Operation cancelled by user{Colors.ENDC}\n")
        sys.exit(0)
    except Exception as e:
        # Unexpected error - show it and exit with error code
        print(f"\n{Colors.RED}Fatal error: {str(e)}{Colors.ENDC}\n")
        sys.exit(1)


# Standard Python idiom: only run main() when script is executed directly
# (not when imported as a module)
if __name__ == '__main__':
    main()
