#!/usr/bin/env python3
"""Marathon Motivation Coach CLI.

Asks the user three personal questions and then generates personalized
motivational quotes tailored for sports/marathon training.
"""

from __future__ import annotations

import random


def ask_questions() -> dict[str, str]:
    """Collect three personal answers from the user."""
    print("🏃 Marathon Motivation Coach")
    print("Answer 3 quick questions to get personalized motivational quotes.\n")

    name = input("1) What's your first name? ").strip() or "Athlete"
    reason = (
        input(
            "2) Who or what are you running for today? (family, health, goal, etc.) "
        ).strip()
        or "your future self"
    )
    challenge = (
        input(
            "3) What's your biggest challenge right now? (fatigue, self-doubt, pace, etc.) "
        ).strip()
        or "staying consistent"
    )

    return {"name": name, "reason": reason, "challenge": challenge}


def generate_quotes(profile: dict[str, str], count: int = 5) -> list[str]:
    """Generate personalized sports-focused motivational quotes."""
    name = profile["name"]
    reason = profile["reason"]
    challenge = profile["challenge"]

    templates = [
        "Do it, {name}! Do it for {reason}. Every step is a promise kept.",
        "When {challenge} shows up, answer with action. One more stride, {name}.",
        "Run with purpose today: for {reason}, for your strength, for your finish line.",
        "{name}, pain is temporary—your pride and purpose for {reason} will last.",
        "Beat {challenge} with rhythm, breath, and belief. You are built for this.",
        "This marathon is your message: discipline over excuses, especially for {reason}.",
        "You're not just running miles, {name}—you're building a stronger life beyond {challenge}.",
        "Legs tired? Heart ready. Remember why: {reason}. Keep going.",
    ]

    selected = random.sample(templates, k=min(count, len(templates)))
    return [t.format(name=name, reason=reason, challenge=challenge) for t in selected]


def main() -> None:
    profile = ask_questions()
    print("\n🔥 Your Personalized Motivation:")
    for idx, quote in enumerate(generate_quotes(profile), start=1):
        print(f"{idx}. {quote}")


if __name__ == "__main__":
    main()
