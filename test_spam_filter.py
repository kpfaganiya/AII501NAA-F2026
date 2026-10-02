"""
Test cases for the Spam Filter Email Agent.
AII501NAA - Activity 1, Question 1, Part A(d)

Run with:  pytest test_spam_filter.py -v
"""

from pathlib import Path

import pytest

from spam_filter_agent import SpamFilterAgent, load_word_list

DATA_DIR = Path(__file__).parent / "test_data"
INBOX = DATA_DIR / "inbox"


@pytest.fixture
def agent() -> SpamFilterAgent:
    return SpamFilterAgent(
        allow_list=load_word_list(DATA_DIR / "allow_list.txt"),
        restrict_list=load_word_list(DATA_DIR / "restrict_list.txt"),
        bad_words=load_word_list(DATA_DIR / "bad_words.txt"),
    )


def test_allow_list_overrides_bad_word_content(agent):
    """An email from an allow-listed domain is never spam, even with many
    bad words in the body."""
    result = agent.act(INBOX / "allow_list_override.eml")
    assert result == "not_spam"


def test_restrict_list_overrides_clean_content(agent):
    """An email from a restrict-listed domain is always spam, even with a
    perfectly clean body."""
    result = agent.act(INBOX / "restrict_list_override.eml")
    assert result == "spam"


def test_more_than_five_bad_words_is_spam(agent):
    """Six bad words, from a domain on neither list, is spam."""
    result = agent.act(INBOX / "bad_words_spam.eml")
    assert result == "spam"


def test_clean_email_is_not_spam(agent):
    """No bad words, from a domain on neither list, is not spam."""
    result = agent.act(INBOX / "clean_email.eml")
    assert result == "not_spam"


def test_boundary_exactly_five_bad_words_is_not_spam(agent):
    """Spec says 'more than 5' -> exactly 5 must NOT be spam. Boundary case."""
    result = agent.act(INBOX / "boundary_five_words.eml")
    assert result == "not_spam"


def test_boundary_six_bad_words_is_spam(agent):
    """One more than the boundary (6) must be spam."""
    result = agent.act(INBOX / "boundary_six_words.eml")
    assert result == "spam"


def test_file_email_writes_to_correct_directory(agent, tmp_path):
    spam_dir = tmp_path / "spam"
    email_dir = tmp_path / "email"

    action = agent.file_email(INBOX / "bad_words_spam.eml", spam_dir, email_dir)

    assert action == "spam"
    assert (spam_dir / "bad_words_spam.eml").exists()
    assert not (email_dir / "bad_words_spam.eml").exists()


def test_rule_match_returns_first_matching_rule_in_priority_order(agent):
    """Directly exercises RULE-MATCH to confirm allow-list priority beats
    the restrict-list rule if (hypothetically) a domain were on both."""
    from spam_filter_agent import EmailState

    state = EmailState(sender_domain="trusted.com", bad_word_count=100)
    rule = agent.rule_match(state)
    assert rule.action == "not_spam"
    assert "allow-list" in rule.name
