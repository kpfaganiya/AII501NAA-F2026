# Activity 1 - Question 1: Spam Filter Email Agent (Part A)

AII501NAA - F2026

## a) Task Environment — PEAS

| | |
|---|---|
| **Performance measure** | Correctly classifies each email as spam or not-spam; minimizes false positives (legitimate email marked spam) and false negatives (spam let through); correctly parses the header and readable (text-type) body/attachment content; correctly files each email into the right directory. |
| **Environment** | The stream of incoming `.eml` files (header + body, possibly with text-type attachments); the allow list; the restrict list; the bad word list; the file system the agent reads from and writes into (spam directory, email directory). |
| **Actuators** | Write/move the email into the **spam** directory; write/move the email into the **email** (not-spam) directory. |
| **Sensors** | Header parser (reads the `From` field / sender domain); body/text reader (reads and tokenizes the readable body and text-type attachment content); list lookup (checks sender domain against the allow/restrict lists and words against the bad word list). |

## b) Environment Properties

- **Fully observable** - everything needed to classify the email (header + readable body) is available in the file at once; nothing is hidden.
- **Deterministic** - the same email against the same lists always produces the same classification.
- **Episodic** - each email is classified independently; no memory of prior emails is needed or used.
- **Static** - the email content and the lists do not change while the agent is processing a given email.
- **Discrete** - a finite set of percepts (a fixed vocabulary/domain space) and a finite set of actions (file as spam / file as not-spam).
- **Single-agent** - only this agent acts in the environment.

## c) Agent Type

A **simple reflex agent** is the most appropriate design.

Justification: because the environment is episodic and fully observable (part b), the correct classification of any given email depends *only* on that email's own header and body - never on anything the agent has seen before. There is no need to track state across emails, plan ahead, or reason about future consequences. The entire decision reduces to a small set of condition-action rules (allow-list domain → not spam; restrict-list domain → spam; bad-word count over threshold → spam; otherwise → not spam), which is exactly the structure a simple reflex agent is built for (AIMA, Figure 2.8). A model-based, goal-based, or utility-based agent would add machinery (internal state, goal search, utility functions) that this problem has no use for.

## d) Implementation

Implemented in `spam_filter_agent.py` as a `SpamFilterAgent` class that mirrors the book's simple-reflex-agent pseudocode directly:

```
function SIMPLE-REFLEX-AGENT(percept) returns an action
    persistent: rules, a set of condition-action rules
    state  <- INTERPRET-INPUT(percept)
    rule   <- RULE-MATCH(state, rules)
    action <- rule.ACTION
    return action
```

| Book concept | Code |
|---|---|
| sensors | `perceive()` - parses the `.eml` file's `From` domain and readable (text-type) body |
| `INTERPRET-INPUT` | `interpret_input()` - reduces the percept to `(sender_domain, bad_word_count)` |
| persistent rules | `self.rules`, built once in `__init__` |
| `RULE-MATCH` | `rule_match()` - returns the first rule whose condition holds, in priority order |
| action / actuator | `act()` returns the classification; `file_email()` writes the file into the correct directory |

**Rule priority** (matches the assignment spec exactly):
1. Sender domain on the allow list → `not_spam`, regardless of content.
2. Else, sender domain on the restrict list → `spam`, regardless of content.
3. Else, more than 5 bad words in the body → `spam`.
4. Else → `not_spam`.

## Assumptions

- Only MIME parts with content-maintype `text` (e.g. `text/plain`, `text/html`) are read, per the assignment's note that text-type attachments are readable by the agent; non-text attachments are ignored/unreadable.
- Domain matching is case-insensitive and exact (e.g. `trusted.com` does not implicitly match `mail.trusted.com`); this can be widened to a suffix match if the instructor intends subdomains to count.
- "More than 5 words" (part A intro) is interpreted as a **strict** inequality — exactly 5 bad words is *not* spam; 6 or more is. This boundary is covered explicitly by a test case.
- Bad-word matching is case-insensitive and strips surrounding punctuation, but does not stem/lemmatize words (e.g. "clicking" would not match "click").

## Project Structure

```
Activity1_PartA/
├── README.md                  # this file
├── spam_filter_agent.py       # agent implementation
├── test_spam_filter.py        # pytest test suite
└── test_data/
    ├── allow_list.txt
    ├── restrict_list.txt
    ├── bad_words.txt
    └── inbox/
        ├── allow_list_override.eml     # allow list beats bad words  -> not_spam
        ├── restrict_list_override.eml  # restrict list beats clean content -> spam
        ├── bad_words_spam.eml          # 6 bad words, unknown domain -> spam
        ├── clean_email.eml             # 0 bad words, unknown domain -> not_spam
        ├── boundary_five_words.eml     # exactly 5 bad words -> not_spam (boundary)
        └── boundary_six_words.eml      # exactly 6 bad words -> spam (boundary)
```

## Setup

Requires Python 3.10+ and `pytest`.

```bash
pip install pytest
```

## Execution

Run the agent over the sample inbox (classifies every `.eml` file in `test_data/inbox` and copies each into `output/spam` or `output/email`):

```bash
python3 spam_filter_agent.py
```

Custom paths:

```bash
python3 spam_filter_agent.py --inbox path/to/inbox --spam-dir path/to/spam --email-dir path/to/email \
    --allow-list path/to/allow_list.txt --restrict-list path/to/restrict_list.txt --bad-words path/to/bad_words.txt
```

## Testing

```bash
pytest test_spam_filter.py -v
```

8 tests cover: allow-list override, restrict-list override, bad-word threshold spam case, clean email, the exactly-5/exactly-6 boundary around the threshold, correct file placement, and rule-priority ordering. All 8 currently pass.
