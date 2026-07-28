#!/usr/bin/env python3
"""Interactive CLI for AI-powered document processing."""

import os
import sys
import textwrap
from pathlib import Path
from typing import Callable, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))

from src.output_manager import OutputManager, OutputManagerError
from src.processors import ProcessorError, TextProcessor


class Colors:
    """ANSI styles used consistently throughout the interface."""

    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    CLEAR_LINE = "\033[2K"


class StageProgress:
    """Display one active workflow stage and retain completed stages."""

    def __init__(self, total: int):
        self.total = total
        self.current = 0
        self.active: Optional[str] = None

    def update(self, message: str) -> None:
        if self.active:
            self._complete_active()

        self.current += 1
        self.active = message
        print(
            f"{Colors.YELLOW}● [{self.current}/{self.total}] "
            f"{message}...{Colors.RESET}",
            end="",
            flush=True,
        )

    def finish(self) -> None:
        if self.active:
            self._complete_active()

    def fail(self) -> None:
        if not self.active:
            return

        print(
            f"\r{Colors.CLEAR_LINE}{Colors.RED}✗ [{self.current}/{self.total}] "
            f"{self.active} failed{Colors.RESET}"
        )
        self.active = None

    def _complete_active(self) -> None:
        print(
            f"\r{Colors.CLEAR_LINE}{Colors.GREEN}✓ [{self.current}/{self.total}] "
            f"{self.active}{Colors.RESET}"
        )
        self.active = None


class CLI:
    """Demo-friendly command-line interface."""

    WIDTH = 76
    ACTIONS: Dict[str, Dict[str, str]] = {
        "1": {
            "key": "summarize",
            "name": "Summarize",
            "description": "Create a concise summary and key points",
        },
        "2": {
            "key": "translate",
            "name": "Translate",
            "description": "Translate content while preserving meaning and tone",
        },
        "3": {
            "key": "sentiment",
            "name": "Sentiment analysis",
            "description": "Identify sentiment, confidence, and reasoning",
        },
    }

    def __init__(self):
        self.processor: Optional[TextProcessor] = None

    def print_welcome(self) -> None:
        line = "═" * (self.WIDTH - 2)
        print(f"\n{Colors.MAGENTA}╔{line}╗")
        print(
            f"║{Colors.BOLD}{Colors.WHITE}"
            f"{'AI CONTENT MANAGEMENT':^{self.WIDTH - 2}}"
            f"{Colors.RESET}{Colors.MAGENTA}║"
        )
        print(f"╚{line}╝{Colors.RESET}")
        print(
            f"{Colors.DIM}{'Turn documents into actionable insights':^{self.WIDTH}}"
            f"{Colors.RESET}\n"
        )

    def print_menu(self) -> None:
        self._section("CHOOSE A WORKFLOW", "INPUT")
        for number, action in self.ACTIONS.items():
            print(
                f"  {Colors.CYAN}{Colors.BOLD}[{number}] {action['name']:<20}"
                f"{Colors.RESET}{Colors.DIM}{action['description']}{Colors.RESET}"
            )
        print(
            f"  {Colors.CYAN}{Colors.BOLD}[4] Exit{Colors.RESET}"
            f"{Colors.DIM}{'':<17}Close the application{Colors.RESET}\n"
        )

    def get_menu_choice(self) -> str:
        while True:
            choice = input(
                f"{Colors.BOLD}  Select an option "
                f"{Colors.CYAN}[1-4]{Colors.RESET}{Colors.BOLD}: {Colors.RESET}"
            ).strip()
            if choice in {"1", "2", "3", "4"}:
                return choice
            self.show_error("Enter 1, 2, 3, or 4.")

    def get_file_path(self) -> Optional[str]:
        while True:
            value = input(
                f"{Colors.BOLD}  Source file "
                f"{Colors.CYAN}[.txt or .pdf]{Colors.RESET}{Colors.BOLD}: "
                f"{Colors.RESET}"
            ).strip()

            if not value:
                self.show_error("A file path is required.")
                continue

            path = Path(value).expanduser()
            if not path.exists():
                self.show_error(f"File not found: {path}")
            elif not path.is_file():
                self.show_error(f"Path is not a file: {path}")
            elif path.suffix.lower() not in {".txt", ".pdf"}:
                self.show_error(
                    f"Unsupported format '{path.suffix or 'none'}'; use .txt or .pdf."
                )
            else:
                return str(path)

            retry = input(
                f"{Colors.DIM}  Try another path? [Y/n]: {Colors.RESET}"
            ).strip().lower()
            if retry == "n":
                return None

    def get_target_language(self) -> Optional[str]:
        language = input(
            f"{Colors.BOLD}  Target language "
            f"{Colors.CYAN}[e.g. Spanish]{Colors.RESET}{Colors.BOLD}: "
            f"{Colors.RESET}"
        ).strip()
        if not language:
            self.show_error("A target language is required.")
            return None
        return language

    def display_input(
        self,
        action: Dict[str, str],
        file_path: str,
        target_language: Optional[str] = None,
    ) -> None:
        path = Path(file_path)
        self._section("REQUEST", "INPUT")
        self._field("Workflow", action["name"])
        self._field("Source", self._display_path(path))
        self._field("Format", path.suffix[1:].upper())
        self._field("File size", self._format_size(path.stat().st_size))
        if target_language:
            self._field("Target", target_language)
        print()

    def display_result(self, result: dict, output_path: str) -> None:
        use_case = result["use_case"]
        output = result["result"]

        self._section("RESULT", "OUTPUT")
        self._field("Source", result["filename"])
        self._field("Language", result["language_detected"])
        self._field("Words processed", f"{result['word_count']:,}")
        self._field("Saved to", output_path)
        print()

        if use_case == "summarize":
            self._subheading("SUMMARY")
            self._wrapped(output["summary"])
            print()
            self._subheading("KEY POINTS")
            for index, point in enumerate(output["key_points"], 1):
                self._wrapped(str(point), prefix=f"  {index}. ")

        elif use_case == "translate":
            self._field("Translation", f"{output.get('source_language', 'N/A')} → "
                        f"{output['target_language']}")
            print()
            self._subheading("TRANSLATED TEXT")
            self._wrapped(output["translated_text"])

        elif use_case == "sentiment":
            sentiment = str(output["sentiment"]).lower()
            sentiment_color = {
                "positive": Colors.GREEN,
                "negative": Colors.RED,
                "neutral": Colors.YELLOW,
            }.get(sentiment, Colors.WHITE)
            self._field(
                "Sentiment",
                f"{sentiment_color}{Colors.BOLD}{sentiment.upper()}{Colors.RESET}",
            )
            self._field("Confidence", f"{float(output['confidence']):.1%}")
            print()
            self._subheading("ANALYSIS")
            self._wrapped(output["explanation"])

        print(f"\n{Colors.GREEN}{'─' * self.WIDTH}{Colors.RESET}")
        print(
            f"{Colors.GREEN}{Colors.BOLD}✓ COMPLETE{Colors.RESET}  "
            f"The result is ready and the JSON output has been saved.\n"
        )

    def execute_workflow(
        self,
        file_path: str,
        operation: Callable[[Callable[[str], None]], dict],
    ) -> None:
        progress = StageProgress(total=4)
        self._section("PROCESSING", "LIVE")

        try:
            result = operation(progress.update)
            progress.update("Saving structured JSON output")
            output_path = OutputManager.save_from_processor_result(result)
            progress.finish()
            self.display_result(result, output_path)
        except ProcessorError as exc:
            progress.fail()
            self.show_error(str(exc))
        except OutputManagerError as exc:
            progress.fail()
            self.show_error(f"Could not save output: {exc}")
        except Exception as exc:
            progress.fail()
            self.show_error(f"Unexpected error: {exc}")

    def run(self) -> int:
        self.print_welcome()

        startup = StageProgress(total=1)
        try:
            startup.update("Loading secure AI configuration")
            self.processor = TextProcessor()
            startup.finish()
            print(
                f"{Colors.GREEN}{Colors.BOLD}  STATUS: READY{Colors.RESET}"
                f"{Colors.DIM}  Secure configuration loaded{Colors.RESET}\n"
            )
        except ProcessorError as exc:
            startup.fail()
            self.show_error(str(exc))
            print(
                f"{Colors.YELLOW}  Add a valid OPENAI_API_KEY to .env, "
                f"then restart the application.{Colors.RESET}\n"
            )
            return 1

        while True:
            self.print_menu()
            choice = self.get_menu_choice()
            if choice == "4":
                self._goodbye()
                return 0

            action = self.ACTIONS[choice]
            print()
            file_path = self.get_file_path()
            if file_path is None:
                continue

            target_language = None
            if action["key"] == "translate":
                target_language = self.get_target_language()
                if target_language is None:
                    continue

            self.display_input(action, file_path, target_language)

            if action["key"] == "summarize":
                self.execute_workflow(
                    file_path,
                    lambda callback: self.processor.process_summarization(
                        file_path, callback
                    ),
                )
            elif action["key"] == "translate":
                self.execute_workflow(
                    file_path,
                    lambda callback: self.processor.process_translation(
                        file_path, target_language, callback
                    ),
                )
            else:
                self.execute_workflow(
                    file_path,
                    lambda callback: self.processor.process_sentiment(
                        file_path, callback
                    ),
                )

            again = input(
                f"{Colors.BOLD}  Process another file? "
                f"{Colors.CYAN}[Y/n]{Colors.RESET}{Colors.BOLD}: {Colors.RESET}"
            ).strip().lower()
            if again == "n":
                self._goodbye()
                return 0
            print()

    def show_error(self, message: str) -> None:
        print(f"\n{Colors.RED}{Colors.BOLD}  ✗ ERROR{Colors.RESET}  {message}\n")

    def _section(self, title: str, badge: str) -> None:
        print(f"{Colors.BLUE}{'─' * self.WIDTH}{Colors.RESET}")
        print(
            f"{Colors.BLUE}{Colors.BOLD}{title}{Colors.RESET}  "
            f"{Colors.DIM}[{badge}]{Colors.RESET}"
        )
        print(f"{Colors.BLUE}{'─' * self.WIDTH}{Colors.RESET}")

    def _subheading(self, title: str) -> None:
        print(f"{Colors.CYAN}{Colors.BOLD}{title}{Colors.RESET}")

    def _field(self, label: str, value: str) -> None:
        print(
            f"  {Colors.DIM}{label:<16}{Colors.RESET}"
            f"{Colors.WHITE}{value}{Colors.RESET}"
        )

    def _wrapped(self, value: str, prefix: str = "  ") -> None:
        available_width = self.WIDTH - len(prefix)
        paragraphs = str(value).splitlines() or [""]
        for paragraph in paragraphs:
            print(
                textwrap.fill(
                    paragraph,
                    width=available_width,
                    initial_indent=prefix,
                    subsequent_indent=" " * len(prefix),
                )
            )

    @staticmethod
    def _format_size(size: int) -> str:
        if size < 1024:
            return f"{size} B"
        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size / (1024 * 1024):.1f} MB"

    @staticmethod
    def _display_path(path: Path) -> str:
        resolved = path.resolve()
        try:
            return str(resolved.relative_to(Path.cwd()))
        except ValueError:
            return str(resolved)

    def _goodbye(self) -> None:
        print(
            f"\n{Colors.MAGENTA}{Colors.BOLD}"
            f"{'Session complete — thank you for using AI Content Management':^{self.WIDTH}}"
            f"{Colors.RESET}\n"
        )


def main() -> None:
    try:
        raise SystemExit(CLI().run())
    except KeyboardInterrupt:
        print(
            f"\n\n{Colors.YELLOW}Operation cancelled. No further work was "
            f"performed.{Colors.RESET}\n"
        )
        raise SystemExit(0)
    except Exception as exc:
        print(f"\n{Colors.RED}Fatal error: {exc}{Colors.RESET}\n")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
