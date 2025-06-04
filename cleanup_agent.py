#!/usr/bin/env python3

import sys
import os
import openai

def main():
    if len(sys.argv) < 3:
        print("Usage: cleanup_agent.py <file> <flag>")
        sys.exit(1)

    file = sys.argv[1]
    flag = sys.argv[2]

    # Read the file content
    with open(file, "r") as f:
        code = f.read()

    # Compose the prompt
    prompt = (
        f"You are an expert software engineer. "
        f"Rewrite the following code to completely remove the use of the feature flag '{flag}', "
        f"preserving the rest of the logic where possible. "
        f"Do not leave any references to the flag or dead code. "
        f"Maintain the code's original formatting and comments.\n\n"
        f"---\n"
        f"{code}\n"
        f"---\n"
        f"Return only the cleaned-up code."
    )

    # Call OpenAI API
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)

    openai.api_key = api_key

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # You can use "gpt-4", "gpt-3.5-turbo", etc.
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        cleaned_code = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        sys.exit(1)

    # Write the cleaned code back to the file
    with open(file, "w") as f:
        f.write(cleaned_code)

if __name__ == "__main__":
    main()
