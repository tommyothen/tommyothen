import re
from datetime import datetime
from zoneinfo import ZoneInfo

STATS_BLOCK = re.compile(
    r'<!-- STATS:START -->\s*```json\s*(.*?)\s*```\s*<!-- STATS:END -->',
    re.S
)

def calculate_age() -> int:
    tz = ZoneInfo("Europe/London")
    birthday = datetime(2001, 8, 5, tzinfo=tz)
    today = datetime.now(tz)
    age = today.year - birthday.year
    
    # Adjust age if birthday hasn't occurred yet this year
    if (today.month, today.day) < (birthday.month, birthday.day):
        age -= 1
    
    return age

def update_readme(path: str = "README.md") -> None:
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Look for the JSON block between stats tags
    match = STATS_BLOCK.search(content)
    if not match:
        print(f"Stats section not found in {path}")
        return

    json_payload = match.group(1)

    new_payload, n = re.subn(
        r'("age"\s*:\s*)\d+',
        rf'\g<1>{calculate_age()}',
        json_payload,
        count=1
    )

    if n == 0:
        print("No age field found to update.")
        return

    new_block = (
        "<!-- STATS:START -->\n"
        "```json\n"
        f"{new_payload}\n"
        "```\n"
        "<!-- STATS:END -->"
    )

    new_content = content[:match.start()] + new_block + content[match.end():]

    if new_content != content:
        with open(path, "w", encoding="utf-8") as file:
            file.write(new_content)
        print(f"Updated age in {path}")
    else:
        print(f"{path} is already up to date.")


if __name__ == '__main__':
    update_readme()