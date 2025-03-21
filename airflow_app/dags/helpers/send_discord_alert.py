import requests
import json
import pytz


DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1352506605580718101/TeYgUguawnPglngN5vtG0Vn_TJSoZsGuVNk9NM6PuZhR6isx_EUJv8yD6JB4ufTlZ8qz"  # 🔹 Replace with your webhook URL

def send_discord_alert(context, alert_type="failure"):

    dag_id = context.get('dag_run').dag_id
    task_id = context.get('task_instance').task_id
    execution_date = context.get('execution_date')
    exception = context.get('exception')

    jakarta_tz = pytz.timezone("Asia/Jakarta")
    execution_date_jakarta = execution_date.astimezone(jakarta_tz)
    execution_date_str = execution_date_jakarta.strftime("%Y-%m-%d %H:%M:%S")

    if alert_type == "failure":
        message = f"🚨 **Airflow Task Failed! Need actions immediately** \n" \
                  f" **DAG**: `{dag_id}`\n" \
                  f" **Task**: `{task_id}`\n" \
                  f" **Execution Date**: `{execution_date_str}`\n" \
                  f" **Error**: `{exception}`"
    elif alert_type == "retry":
        message = f"🔄 **Airflow Task Retrying!** \n" \
                  f" **DAG**: `{dag_id}`\n" \
                  f" **Task**: `{task_id}`\n" \
                  f" **Execution Date**: `{execution_date_str}`\n" \
                  f" **Retrying attempt**"
    elif alert_type == "success":
        message = f"✅ **Airflow Task Completed!** \n" \
                  f" **DAG**: `{dag_id}`\n" \
                  f" **Task**: `{task_id}`\n" \
                  f" **Execution Date**: `{execution_date_str}`\n" \
                  f" **Success**"

    payload = {"content": message}
    headers = {"Content-Type": "application/json"}

    response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    
    if response.status_code != 204:
        print(f"Failed to send Discord alert: {response.text}")
