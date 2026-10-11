# Parts 2-4: Propositional Logic Answers

All answers below are worked by hand (truth tables and equivalence rules); no code is needed for Parts 2–4.

---

## Part 2 - Satisfiability (10%)

### a. Smoke ⇒ Fire - **neither** (satisfiable, but not valid)

| Smoke | Fire | Smoke ⇒ Fire |
|:-----:|:----:|:------------:|
| T | T | T |
| T | F | **F** |
| F | T | T |
| F | F | T |

True in some rows (so not unsatisfiable) and false in one row (so not valid).

### b. ((Smoke ∧ Heat) ⇒ Fire) ⇔ ((Smoke ⇒ Fire) ∨ (Heat ⇒ Fire)) — **valid**

Truth table (L = (Smoke ∧ Heat) ⇒ Fire, R = (Smoke ⇒ Fire) ∨ (Heat ⇒ Fire)):

| Smoke | Heat | Fire | L | R | L ⇔ R |
|:-----:|:----:|:----:|:-:|:-:|:-----:|
| T | T | T | T | T | T |
| T | T | F | **F** | **F** | T |
| T | F | T | T | T | T |
| T | F | F | T | T | T |
| F | T | T | T | T | T |
| F | T | F | T | T | T |
| F | F | T | T | T | T |
| F | F | F | T | T | T |

L ⇔ R is true in all 8 rows → valid.

Equivalence-rule check:

```
L = (S ∧ H) ⇒ F  ≡ ¬(S ∧ H) ∨ F          (implication elimination)
                 ≡ ¬S ∨ ¬H ∨ F            (De Morgan)
R = (S ⇒ F) ∨ (H ⇒ F) ≡ (¬S ∨ F) ∨ (¬H ∨ F)   (implication elimination)
                 ≡ ¬S ∨ ¬H ∨ F            (associativity / idempotence F∨F ≡ F)
```
L and R are the same sentence, so L ⇔ R is valid.

---

## Part 3 - Models (10%)

The vocabulary {A, B, C, D} has 2⁴ = 16 possible models.

### a. B ∨ C → **12 models**
B ∨ C is false only when B = F and C = F. A and D are then free (2 × 2 = 4 models). So 16 − 4 = **12** models make it true.

### b. (A ⇒ B) ∧ A ∧ ¬B ∧ C ∧ D → **0 models**
`A` is true and `A ⇒ B` is true, so modus ponens forces `B` to be true. But the sentence also contains `¬B`. This contradiction means no model satisfies it. The sentence is unsatisfiable, so there are **0** models.

---

## Part 4 – Resolution (20%)

S = [(Food ⇒ Party) ∨ (Drinks ⇒ Party)] ⇒ [(Food ∧ Drinks) ⇒ Party]

### a. Enumeration — **valid**

| Food | Drinks | Party | LHS = (F⇒P)∨(D⇒P) | RHS = (F∧D)⇒P | LHS ⇒ RHS |
|:----:|:------:|:-----:|:-----------------:|:-------------:|:---------:|
| T | T | T | T | T | T |
| T | T | F | F | F | T |
| T | F | T | T | T | T |
| T | F | F | T | T | T |
| F | T | T | T | T | T |
| F | T | F | T | T | T |
| F | F | T | T | T | T |
| F | F | F | T | T | T |

Every row is true → S is **valid**.

### b. CNF of each side

**Left-hand side** `(Food ⇒ Party) ∨ (Drinks ⇒ Party)`
1. Eliminate ⇒: `(¬Food ∨ Party) ∨ (¬Drinks ∨ Party)`
2. No negation needs moving inward (¬ only on atoms).
3. No ∨-over-∧ distribution needed (it is already a single disjunction).
4. Flatten and remove duplicate literal `Party`: **`¬Food ∨ ¬Drinks ∨ Party`** (one clause).

**Right-hand side** `(Food ∧ Drinks) ⇒ Party`
1. Eliminate ⇒: `¬(Food ∧ Drinks) ∨ Party`
2. De Morgan: `(¬Food ∨ ¬Drinks) ∨ Party`
3. No distribution needed.
4. Flatten: **`¬Food ∨ ¬Drinks ∨ Party`** (one clause).

**How this confirms (a):** both sides have the *identical* CNF, so LHS ≡ RHS. Then S has the form α ⇒ α ≡ ¬α ∨ α, which is a tautology. S is valid.

### c. Resolution proof that S is valid

To prove S valid we show that **¬S is unsatisfiable**. ¬(LHS ⇒ RHS) ≡ LHS ∧ ¬RHS.

* LHS in CNF: `¬Food ∨ ¬Drinks ∨ Party`
* ¬RHS = ¬(¬(Food ∧ Drinks) ∨ Party) ≡ (Food ∧ Drinks) ∧ ¬Party

Clause set:

| # | Clause | Source |
|---|--------|--------|
| 1 | ¬Food ∨ ¬Drinks ∨ Party | LHS |
| 2 | Food | ¬RHS |
| 3 | Drinks | ¬RHS |
| 4 | ¬Party | ¬RHS |

Resolution steps:

| Step | Resolve | Result |
|------|---------|--------|
| 5 | (1) with (2) on Food | ¬Drinks ∨ Party |
| 6 | (5) with (3) on Drinks | Party |
| 7 | (6) with (4) on Party | **□ (empty clause)** |

The empty clause is derived, so ¬S is unsatisfiable. Therefore **S is valid**, matching (a) and (b).
