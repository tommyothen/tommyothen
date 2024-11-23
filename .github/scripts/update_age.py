import re
from datetime import datetime
import json
from zoneinfo import ZoneInfo

def calculate_age():
    birthday = datetime(2001, 8, 5)
    today = datetime.now(ZoneInfo("Europe/London"))
    age = today.year - birthday.year
    
    # If birthday hasn't occurred this year, subtract 1
    if today.month < birthday.month or (today.month == birthday.month and today.day < birthday.day):
        age -= 1
    
    return age

def update_readme():
    with open('README.md', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Look for the JSON block between stats tags
    stats_pattern = r'(<!-- STATS:START -->\n```json\n)((.|\n)*)(\n```\n<!-- STATS:END -->)'
    stats_match = re.search(stats_pattern, content)
    
    if not stats_match:
        print("Stats section not found in README")
        return
    
    # Parse the existing JSON
    json_str = stats_match.group(2)

    # Find the `"age": \d+` pattern in the JSON
    age_pattern = r'("age": )(\d+)'

    # Find the age in the JSON and replace it with the new number
    new_json = re.sub(age_pattern, f'"age": {calculate_age()}', json_str)

    # Replace the old JSON with the new one, maintaining the ```json format
    new_content = content.replace(stats_match.group(0),
                                f'<!-- STATS:START -->\n```json\n{new_json}\n```\n<!-- STATS:END -->')
    
    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(new_content)

if __name__ == '__main__':
    update_readme()