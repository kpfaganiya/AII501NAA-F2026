"""
Spam Filter Email Agent
========================
AII501NAA - Activity 1, Question 1 (Part A)
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Callable, List


@dataclass
class EmailPercept:
    file_path: Path
    sender_domain: str
    body_text: str


# ---------------------------------------------------------------------------
# State: the interpreted percept - the only thing the rules look at.
# ---------------------------------------------------------------------------
@dataclass
class EmailState:
    sender_domain: str
    bad_word_count: int


@dataclass
class Rule:
    name: str
    condition: Callable[[EmailState], bool]
    action: str  # "spam" or "not_spam"


class SpamFilterAgent:
    """Simple reflex agent that classifies an email as spam / not spam."""

    # "If more than 5 words within the body are found on this list"
    BAD_WORD_THRESHOLD = 5

    def __init__(self, allow_list: set[str], restrict_list: set[str], bad_words: set[str]):
        self.allow_list = {d.strip().lower() for d in allow_list}
        self.restrict_list = {d.strip().lower() for d in restrict_list}
        self.bad_words = {w.strip().lower() for w in bad_words}

        # persistent: rules, a set of condition-action rules
        # Order encodes the priority given in the assignment spec:
        #   1. allow list wins regardless of content
        #   2. restrict list wins regardless of content
        #   3. otherwise, more than 5 bad words -> spam
        #   4. otherwise -> not spam
        self.rules: List[Rule] = [
            Rule(
                name="allow-list domain -> not spam (regardless of content)",
                condition=lambda s: s.sender_domain in self.allow_list,
                action="not_spam",
            ),
            Rule(
                name="restrict-list domain -> spam (regardless of content)",
                condition=lambda s: s.sender_domain in self.restrict_list,
                action="spam",
            ),
            Rule(
                name=f"more than {self.BAD_WORD_THRESHOLD} bad words -> spam",
                condition=lambda s: s.bad_word_count > self.BAD_WORD_THRESHOLD,
                action="spam",
            ),
            Rule(
                name="default -> not spam",
                condition=lambda s: True,
                action="not_spam",
            ),
        ]

    # -- Sensors -------------------------------------------------------
    def perceive(self, file_path: Path) -> EmailPercept:
        """Parse an .eml file's header (From domain) and readable body text.

        Assumption: only text-type parts (text/plain, text/html, etc.) are
        readable by the agent, per the assignment's note that "attachments
        of type text are readable by the agent." Non-text parts are ignored.
        """
        with open(file_path, "rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)

        sender = msg.get("From", "")
        domain = ""
        if "@" in sender:
            domain = sender.split("@")[-1].strip().rstrip(">").lower()

        body_parts = []
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_maintype() == "text":
                    try:
                        body_parts.append(part.get_content())
                    except Exception:
                        pass
        else:
            if msg.get_content_maintype() == "text":
                try:
                    body_parts.append(msg.get_content())
                except Exception:
                    pass

        return EmailPercept(
            file_path=file_path,
            sender_domain=domain,
            body_text=" ".join(body_parts),
        )

    # INTERPRET-INPUT -------------------------------------------------
    def interpret_input(self, percept: EmailPercept) -> EmailState:
        tokens = percept.body_text.lower().split()
        cleaned = [t.strip('.,!?;:"\'()[]') for t in tokens]
        count = sum(1 for t in cleaned if t in self.bad_words)
        return EmailState(sender_domain=percept.sender_domain, bad_word_count=count)

    # RULE-MATCH --------------------------------------------------------
    def rule_match(self, state: EmailState) -> Rule:
        for rule in self.rules:
            if rule.condition(state):
                return rule
        raise RuntimeError("unreachable: default rule always matches")

    # Agent program: SIMPLE-REFLEX-AGENT(percept) -----------------------
    def act(self, file_path: Path) -> str:
        percept = self.perceive(file_path)
        state = self.interpret_input(percept)
        rule = self.rule_match(state)
        return rule.action

    # Actuators -----------------------------------------------------------
    def file_email(self, file_path: Path, spam_dir: Path, email_dir: Path) -> str:
        """Actuator: move/copy the email into the spam or email directory."""
        action = self.act(file_path)
        target_dir = spam_dir if action == "spam" else email_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(file_path, target_dir / file_path.name)
        return action


def load_word_list(path: Path) -> set[str]:
    with open(path) as f:
        return {line.strip() for line in f if line.strip() and not line.startswith("#")}


def run(inbox_dir: Path, spam_dir: Path, email_dir: Path,
        allow_list_path: Path, restrict_list_path: Path, bad_words_path: Path) -> dict[str, str]:
    agent = SpamFilterAgent(
        allow_list=load_word_list(allow_list_path),
        restrict_list=load_word_list(restrict_list_path),
        bad_words=load_word_list(bad_words_path),
    )
    results: dict[str, str] = {}
    for eml_file in sorted(inbox_dir.glob("*.eml")):
        results[eml_file.name] = agent.file_email(eml_file, spam_dir, email_dir)
    return results


if __name__ == "__main__":
    import argparse

    

    results = run(
        Path(args.inbox), Path(args.spam_dir), Path(args.email_dir),
        Path(args.allow_list), Path(args.restrict_list), Path(args.bad_words),
    )
    for name, action in results.items():
        print(f"{name}: {action}")
