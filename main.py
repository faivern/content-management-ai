#!/usr/bin/env python3
"""
AI Content Management - CLI Application
Main entry point for text summarization, translation, and sentiment analysis.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.processors import TextProcessor, ProcessorError
from src.output_manager import OutputManager, OutputManagerError


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class CLI:
    """Command-line interface for AI Content Management."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.processor = None
    
    def print_welcome(self):
        """Display welcome message."""
        print("\n" + "=" * 60)
        print(f"{Colors.HEADER}{Colors.BOLD}  AI Content Management System{Colors.ENDC}")
        print("=" * 60)
        print(f"{Colors.BLUE}  Text Analysis powered by OpenAI GPT-5-Nano{Colors.ENDC}")
        print("=" * 60 + "\n")
    
    def print_menu(self):
        """Display main menu."""
        print(f"\n{Colors.BOLD}Available Actions:{Colors.ENDC}")
        print(f"  {Colors.GREEN}1.{Colors.ENDC} Summarize - Generate summary and key points")
        print(f"  {Colors.GREEN}2.{Colors.ENDC} Translate - Translate text to another language")
        print(f"  {Colors.GREEN}3.{Colors.ENDC} Sentiment - Analyze sentiment and tone")
        print(f"  {Colors.GREEN}4.{Colors.ENDC} Exit\n")
    
    def get_file_path(self) -> str:
        """
        Prompt user for file path and validate it.
        
        Returns:
            Validated file path
        """
        while True:
            print(f"{Colors.BOLD}Enter file path:{Colors.ENDC}")
            file_path = input(f"{Colors.BLUE}> {Colors.ENDC}").strip()
            
            if not file_path:
                print(f"{Colors.RED}Error: File path cannot be empty{Colors.ENDC}")
                continue
            
            # Expand user home directory if needed
            file_path = os.path.expanduser(file_path)
            
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"{Colors.RED}Error: File not found: {file_path}{Colors.ENDC}")
                retry = input(f"Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return None
                continue
            
            # Check if it's a file
            if not os.path.isfile(file_path):
                print(f"{Colors.RED}Error: Path is not a file: {file_path}{Colors.ENDC}")
                retry = input(f"Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return None
                continue
            
            # Check file extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in ['.txt', '.pdf']:
                print(f"{Colors.RED}Error: Unsupported file type: {ext}{Colors.ENDC}")
                print(f"{Colors.YELLOW}Supported types: .txt, .pdf{Colors.ENDC}")
                retry = input(f"Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return None
                continue
            
            return file_path
    
    def get_menu_choice(self) -> str:
        """
        Get user's menu choice.
        
        Returns:
            Menu choice (1-4)
        """
        while True:
            choice = input(f"{Colors.BOLD}Select option (1-4):{Colors.ENDC} ").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            print(f"{Colors.RED}Invalid choice. Please enter 1, 2, 3, or 4.{Colors.ENDC}")
    
    def show_progress(self, message: str):
        """Display progress message."""
        print(f"{Colors.YELLOW}⚙ {message}...{Colors.ENDC}")
    
    def show_success(self, message: str):
        """Display success message."""
        print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")
    
    def show_error(self, message: str):
        """Display error message."""
        print(f"{Colors.RED}✗ Error: {message}{Colors.ENDC}")
    
    def display_result(self, result: dict, use_case: str):
        """
        Display processing result in terminal.
        
        Args:
            result: Processing result dictionary
            use_case: Type of use case
        """
        print("\n" + "=" * 60)
        print(f"{Colors.HEADER}{Colors.BOLD}RESULTS{Colors.ENDC}")
        print("=" * 60 + "\n")
        
        if use_case == 'summarize':
            print(f"{Colors.BOLD}Summary:{Colors.ENDC}")
            print(result['summary'])
            print(f"\n{Colors.BOLD}Key Points:{Colors.ENDC}")
            for i, point in enumerate(result['key_points'], 1):
                print(f"  {i}. {point}")
        
        elif use_case == 'translate':
            print(f"{Colors.BOLD}Source Language:{Colors.ENDC} {result.get('source_language', 'N/A')}")
            print(f"{Colors.BOLD}Target Language:{Colors.ENDC} {result['target_language']}")
            print(f"\n{Colors.BOLD}Translation:{Colors.ENDC}")
            print(result['translated_text'])
        
        elif use_case == 'sentiment':
            sentiment = result['sentiment']
            confidence = result['confidence']
            
            # Color-code sentiment
            sentiment_color = Colors.GREEN if sentiment == 'positive' else \
                            Colors.RED if sentiment == 'negative' else Colors.YELLOW
            
            print(f"{Colors.BOLD}Sentiment:{Colors.ENDC} {sentiment_color}{sentiment.upper()}{Colors.ENDC}")
            print(f"{Colors.BOLD}Confidence:{Colors.ENDC} {confidence:.2%}")
            print(f"{Colors.BOLD}Explanation:{Colors.ENDC}")
            print(result['explanation'])
        
        print("\n" + "=" * 60 + "\n")
    
    def process_summarization(self, file_path: str):
        """Process summarization workflow."""
        try:
            self.show_progress("Reading file")
            self.show_progress("Detecting language")
            self.show_progress("Generating summary")
            
            result = self.processor.process_summarization(file_path)
            
            self.show_success("Processing complete")
            
            # Display result
            self.display_result(result['result'], 'summarize')
            
            # Save to file
            self.show_progress("Saving results")
            output_path = OutputManager.save_from_processor_result(result)
            self.show_success(f"Results saved to: {output_path}")
            
        except ProcessorError as e:
            self.show_error(str(e))
        except OutputManagerError as e:
            self.show_error(f"Failed to save output: {str(e)}")
        except Exception as e:
            self.show_error(f"Unexpected error: {str(e)}")
    
    def process_translation(self, file_path: str):
        """Process translation workflow."""
        # Get target language
        print(f"\n{Colors.BOLD}Enter target language (e.g., Spanish, French, German):{Colors.ENDC}")
        target_language = input(f"{Colors.BLUE}> {Colors.ENDC}").strip()
        
        if not target_language:
            self.show_error("Target language cannot be empty")
            return
        
        try:
            self.show_progress("Reading file")
            self.show_progress("Detecting source language")
            self.show_progress(f"Translating to {target_language}")
            
            result = self.processor.process_translation(file_path, target_language)
            
            self.show_success("Processing complete")
            
            # Display result
            self.display_result(result['result'], 'translate')
            
            # Save to file
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
        """Process sentiment analysis workflow."""
        try:
            self.show_progress("Reading file")
            self.show_progress("Detecting language")
            self.show_progress("Analyzing sentiment")
            
            result = self.processor.process_sentiment(file_path)
            
            self.show_success("Processing complete")
            
            # Display result
            self.display_result(result['result'], 'sentiment')
            
            # Save to file
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
        """Run the main CLI loop."""
        # Display welcome message
        self.print_welcome()
        
        # Initialize processor
        try:
            self.show_progress("Initializing AI client")
            self.processor = TextProcessor()
            self.show_success("Ready")
        except ProcessorError as e:
            self.show_error(str(e))
            print(f"\n{Colors.YELLOW}Please ensure your .env file is configured with a valid OPENAI_API_KEY{Colors.ENDC}")
            sys.exit(1)
        
        # Main loop
        while True:
            # Show menu
            self.print_menu()
            
            # Get choice
            choice = self.get_menu_choice()
            
            # Exit
            if choice == '4':
                print(f"\n{Colors.GREEN}Thank you for using AI Content Management!{Colors.ENDC}\n")
                sys.exit(0)
            
            # Get file path
            print()
            file_path = self.get_file_path()
            
            if file_path is None:
                continue
            
            print()
            
            # Process based on choice
            if choice == '1':
                self.process_summarization(file_path)
            elif choice == '2':
                self.process_translation(file_path)
            elif choice == '3':
                self.process_sentiment(file_path)
            
            # Ask if user wants to continue
            print()
            continue_choice = input(f"{Colors.BOLD}Process another file? (y/n):{Colors.ENDC} ").strip().lower()
            if continue_choice != 'y':
                print(f"\n{Colors.GREEN}Thank you for using AI Content Management!{Colors.ENDC}\n")
                break


def main():
    """Main entry point."""
    try:
        cli = CLI()
        cli.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Operation cancelled by user{Colors.ENDC}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {str(e)}{Colors.ENDC}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
