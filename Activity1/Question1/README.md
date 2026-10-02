# Activity 1 - Question 1: Spam Filter Email Agent (Part A)

AII501NAA - F2026

## a) Task environment (PEAS)

**Performance measure:** how accurately the agent classifies emails as spam or not spam. Specifically it should minimize false positives (good email marked as spam) and false negatives (spam that gets through), and it needs to correctly parse the header and any readable (text) body/attachments, then file each email in the right place.

**Environment:** the incoming emails themselves (.eml files, header + body, sometimes with text attachments), the allow list, the restrict list, the bad word list, and the file system it reads from / writes into.

**Actuators:** moving/writing the email into the spam directory, or moving/writing it into the not-spam (email) directory. That's really the only two things the agent can "do."

**Sensors:** reading the From header to get the sender's domain, reading the body (and any text attachments) to pull out words, and checking those against the three lists.

## b) Environment properties

Going through the standard set of properties from the book:

It's fully observable - everything the agent needs (header + body) is right there in the file, nothing hidden. It's deterministic - same email, same lists, same result every time, no randomness involved. It's episodic, since each email gets judged on its own; the agent doesn't need to remember anything about emails it classified earlier. It's static, because nothing about the email or the lists changes while the agent is in the middle of deciding. It's discrete - there's a finite set of possible words/domains and only two possible actions. And it's single-agent, since nothing else is acting in this environment alongside it.

## c) Agent type

I went with a simple reflex agent here. The reasoning is basically that the environment properties in (b) already tell you this is the right call - since it's episodic and fully observable, the correct answer for any email depends only on that email, not on anything that happened before it. There's no reason to carry state between emails, plan ahead, or weigh outcomes - the whole decision is just a handful of condition-action rules (domain on allow list → not spam, domain on restrict list → spam, too many bad words → spam, otherwise not spam). That's exactly the shape of problem a simple reflex agent is meant for. Anything more complex (model-based, goal-based, utility-based) would just be adding machinery this problem doesn't need.

## d) Implementation

`spam_filter_agent.py` implements this as a `SpamFilterAgent` class, following the simple reflex agent structure from the book (Figure 2.8):

```
function SIMPLE-REFLEX-AGENT(percept) returns an action
    persistent: rules, a set of condition-action rules
    state  <- INTERPRET-INPUT(percept)
    rule   <- RULE-MATCH(state, rules)
    action <- rule.ACTION
    return action
```

Roughly, the pieces map like this: `perceive()` is the sensors, pulling the sender's domain and readable body text out of the .eml file. `interpret_input()` is `INTERPRET-INPUT` - it reduces all of that down to just `(sender_domain, bad_word_count)`, which is all the rules actually need to look at. The rules themselves are set up once in `__init__` (the "persistent" part), and `rule_match()` walks through them in order and returns the first one that applies. `act()` ties it together and returns the classification, and `file_email()` is the actuator - it actually copies the file into the right folder.

The rules are checked in this order, which matches how the assignment describes them:
1. sender on the allow list → not spam, no matter what's in the body
2. otherwise, sender on the restrict list → spam, no matter what's in the body
3. otherwise, more than 5 bad words in the body → spam
4. otherwise → not spam

## Assumptions

A few things I had to decide on since they weren't spelled out exactly in the assignment:

Only text-type parts of the email (text/plain, text/html, etc.) get read - this matches the assignment's note that text attachments are readable, so anything else is just skipped. Domain matching is exact and case-insensitive, so `trusted.com` won't match `mail.trusted.com` unless you widen it to a subdomain match. "More than 5 words" is read as a strict greater-than - exactly 5 bad words is still not spam, you need 6+ - and there's a test that checks this boundary specifically since it's an easy thing to get backwards. Bad word matching strips punctuation and ignores case but doesn't do any stemming, so "click" won't catch "clicking."

## Project structure

```
Activity1_PartA/
├── README.md
├── spam_filter_agent.py
├── test_spam_filter.py
└── test_data/
    ├── allow_list.txt
    ├── restrict_list.txt
    ├── bad_words.txt
    └── inbox/
        ├── allow_list_override.eml
        ├── restrict_list_override.eml
        ├── bad_words_spam.eml
        ├── clean_email.eml
        ├── boundary_five_words.eml
        └── boundary_six_words.eml
```

## Setup

Needs Python 3.10+ and pytest.

```bash
pip install pytest
```

## Running it

```bash
python3 spam_filter_agent.py
```

This runs every .eml file in `test_data/inbox` through the agent and copies each one into `output/spam` or `output/email` depending on the result. You can point it at different folders/lists with `--inbox`, `--spam-dir`, `--email-dir`, `--allow-list`, `--restrict-list`, `--bad-words`.

## Testing

```bash
pytest test_spam_filter.py -v
```

8 tests, covering the allow-list override, the restrict-list override, the bad-word threshold case, a clean email, the exactly-5/exactly-6 boundary, that files actually land in the right folder, and that the rules get checked in the right priority order. All 8 pass.
