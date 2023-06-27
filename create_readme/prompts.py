"""Default prompts for generating a readme file."""

from dataclasses import dataclass


@dataclass
class Question:
    """A question to ask the user."""

    question: str
    answer: str

    def to_string(self) -> str:
        """Return a string representation of the question and answer."""
        return f"**{self.question}**\n{self.answer}"

    def dict(self) -> dict:
        """Return a dictionary representation of the question and answer."""
        return {"question": self.question, "answer": self.answer}


def questions_prompt(project_name: str, questions: list[Question]) -> str:
    """Return a prompt for the user to answer questions about their project.

    Args:
        project_name: The name of the project.
        questions: A list of questions to ask the user.

    Returns:
        A prompt for the AI to generate another question.
    """
    project_name_question = Question(
        question="What is the name of your project?",
        answer=project_name,
    )
    q_and_a = "\n\n".join(x.to_string() for x in [project_name_question] + questions)
    prompt_head = (
        "I am writing a README for my project that I'm planning to publish on github. "
        "Here are some questions and answers that I think matter."
    )
    prompt_tail = (
        "Ask another question that you think is important for a README file. "
        "I will add it to the list."
    )
    return f"{prompt_head}\n\n{q_and_a}\n\n{prompt_tail}"


def readme_prompt(project_name: str, questions: list[Question]) -> str:
    return (
        "Here are some questions and answers about my project:\n\n"
        + "\n\n".join(
            x.to_string()
            for x in [
                Question(
                    question="What is the name of your project?", answer=project_name
                )
            ]
            + questions
        )
        + "\n\nWrite a readme for my project. Follow usual conventions for a readme file."
    )
