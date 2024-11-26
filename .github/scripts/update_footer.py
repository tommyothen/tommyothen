import re
from datetime import datetime, timezone
import yaml
import os
from pathlib import Path
from croniter import croniter

def get_next_cron_time(cron_expression):
    base = datetime.now(timezone.utc)
    iter = croniter(cron_expression, base)
    return iter.get_next(datetime)

def get_workflow_schedules():
    schedules = []
    workflow_dir = Path('.github/workflows')
    
    for workflow_file in workflow_dir.glob('*.yml'):
        with open(workflow_file, 'r') as f:
            try:
                workflow = yaml.safe_load(f)

                # Get schedule from the True key (which is actually 'on' in the YAML)
                if True in workflow and 'schedule' in workflow[True]:
                    crons = workflow[True]['schedule']
                    name = workflow.get('name', workflow_file.stem)
                    for cron in crons:
                        if 'cron' in cron:
                            schedules.append({
                                'name': name,
                                'cron': cron['cron'],
                                'next_run': get_next_cron_time(cron['cron'])
                            })
            except yaml.YAMLError as e:
                print(f"Error parsing {workflow_file}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error with {workflow_file}: {e}")
                continue
    
    print(f"Found schedules: {schedules}")  # Debug print
    return schedules

def update_readme_footer():
    with open('README.md', 'r', encoding='utf-8') as file:
        content = file.read()
    
    now = datetime.now(timezone.utc)
    schedules = get_workflow_schedules()
    
    if not schedules:
        print("No schedules found!")
        return
    
    # Sort schedules by next run time and take first two
    schedules.sort(key=lambda x: x['next_run'])
    next_updates = schedules[:2]
    
    # Create a cleaner scheduled actions list
    scheduled_actions = '\n'.join([
        f'<tr><td><code>{x["cron"]}</code></td><td>{x["name"]}</td><td><code>{x["next_run"].strftime("%Y-%m-%d %H:%M UTC")}</code></td></tr>'
        for x in schedules
    ])

    footer_text = f'''<!-- DYNAMIC_FOOTER:START -->
<div align="center">
  <i>This README is updated automatically through GitHub Actions</i>
  <br/>
  <i>Last refresh: {now.strftime('%H:%M UTC')} · Next update: {next_updates[0]['name']} @ {next_updates[0]['next_run'].strftime('%H:%M UTC')}</i>
</div>
<br/>
<div align="center">
  <details>
    <summary>🕒 Scheduled Actions</summary>
    <br/>
    <table>
      <tr>
        <th>Schedule</th>
        <th>Action</th>
        <th>Next Run</th>
      </tr>
      {scheduled_actions}
    </table>
  </details>
</div>
<!-- DYNAMIC_FOOTER:END -->'''

    # Replace existing footer or add new one
    footer_pattern = r'<!-- DYNAMIC_FOOTER:START -->.*?<!-- DYNAMIC_FOOTER:END -->'
    if re.search(footer_pattern, content, re.DOTALL):
        new_content = re.sub(footer_pattern, footer_text, content, flags=re.DOTALL)
    else:
        new_content = f'{content}\n\n---\n\n{footer_text}'
    
    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(new_content)

if __name__ == '__main__':
    update_readme_footer()