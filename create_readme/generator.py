"""Generate READMEs."""
import contextlib
import json
import os

import openai

from .multiline_input import multiline_input
from .prompts import Question, questions_prompt, readme_prompt


class Generator:
    """README generator."""

    def __init__(
        self,
        project_name: str,
        config_path: str | None = None,
        model: str = "gpt-3.5-turbo-0613",
    ):
        """Initialize the generator.

        Args:
            project_name: The name of the project.
        """
        self.project_name = project_name
        self.questions: list[Question] = []
        self.config_path = config_path
        self.model = model

    @property
    def config_file_path(self) -> str | None:
        """Get the path to the configuration file.

        Returns:
            The path to the configuration file.
        """
        if not self.config_path:
            return None
        return self.config_path + f"/{self.project_name}.json"

    def load_config(self):
        """Load the configuration."""
        if not self.config_file_path:
            return
        with contextlib.suppress(FileNotFoundError):
            with open(self.config_file_path, "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
            self.questions = [
                Question(question=question["question"], answer=question["answer"])
                for question in config["questions"]
            ]

    def save_config(self):
        """Save the configuration."""
        if not self.config_file_path:
            return
        with open(self.config_file_path, "w", encoding="utf-8") as config_file:
            json.dump(
                {"questions": [question.dict() for question in self.questions]},
                config_file,
            )

    def ask_load(self):
        """Ask the user if they want to load the configuration."""
        if not self.config_file_path:
            return
        if not os.path.exists(self.config_file_path):
            return
        load = input(
            "Would you like to load the configuration from a previous session? [Y/n] "
        )
        if load.lower() == "y":
            self.load_config()

    def generate_next_question(self) -> str:
        """Generate the next question for the user to answer.

        Returns:
            A prompt for the user to answer.
        """
        prompt = questions_prompt(self.project_name, self.questions)
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a README generator. "
                        "You are helping a user write a README for "
                        "their project. Your task is to ask the user "
                        "questions about their project to help them "
                        "write a comprehensive README. As a reminder, "
                        "a README should not prioritize the technical "
                        "details of my project. Instead, it should focus on "
                        "the motivation for the project, the problem it "
                        "solves, and how to use it."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            functions=[
                {
                    "name": "ask_next_question",
                    "description": "Ask the user the next question.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "The question to ask the user, "
                                "for example, 'What is your project called?'",
                            }
                        },
                        "required": ["question"],
                    },
                }
            ],
            function_call={"name": "ask_next_question"},
        )
        return json.loads(
            response["choices"][0]["message"]["function_call"]["arguments"]
        )["question"]

    def ask_next_question(self) -> Question | None:
        """Ask the user the next question.

        Returns:
            The question and answer.
        """
        question = self.generate_next_question()
        answer = multiline_input(
            question + " Leave empty to generate the README"
        ).strip()
        if not answer:
            return None
        return Question(question=question, answer=answer)

    def generate_readme(self) -> str:
        """Generate the README.

        Returns:
            The README.
        """
        prompt = readme_prompt(self.project_name, self.questions)
        return openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a README generator. "
                        "You are helping a user write a comprehensive "
                        "README for their project. You shouldn't output "
                        "any text other than the README itself, in Markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )["choices"][0]["message"]["content"]

    def run(self) -> str:
        """Run the generator."""
        self.ask_load()
        while True:
            question = self.ask_next_question()
            if not question:
                break
            self.questions.append(question)
            self.save_config()
        return self.generate_readme()
