import os

import asana
import openai
from dotenv import load_dotenv

load_dotenv()


# ChatGPT Settings
chatgpt_api_key = os.getenv("CHATGPT_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Asana Settings
ASANA_API_KEY = os.getenv("ASANA_API_KEY")
ASANA_PROJECT_ID = "1204111094296891"
client = asana.Client.access_token(ASANA_API_KEY)
client.LOG_ASANA_CHANGE_WARNINGS = False


def create_asana_task(task_name: str, notes: str = ""):
    """Asanaのタスクを作成する"""
    result = client.tasks.create_task(
        {"name": task_name, "notes": notes, "projects": ASANA_PROJECT_ID},
        opt_pretty=True,
    )
    return result


def ask_to_chatgpt(prompt: str, sys_setting: str = "") -> tuple[str, int]:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": sys_setting},
                {"role": "user", "content": prompt},
            ],
        )
        message = response["choices"][0]["message"]["content"]
        token = int(response["usage"]["total_tokens"])
        return (message, token)
    except Exception as e:
        raise Exception(e)


def main():
    # ユーザーからの入力を受け取る
    user_input = input("実行したいことを入力してください: ")

    # ChatGPT APIを呼び出してタスクを取得
    prompt = f"""
        {user_input}を実行するためのタスクを教えて。以下のフォーマットで出力して。
        1,タスク名, 詳しい手順(1行で書く)
        2,タスク名, 詳しい手順(1行で書く)
        続く
        """
    answer, _ = ask_to_chatgpt(prompt)

    tasks = answer.split("\n")
    # 空行を削除
    tasks = [x for x in tasks if x.strip()]

    # 取得したタスクを標準出力に出力し、Asanaに登録するか尋ねる
    for t in tasks:
        print(t)
    register = input("このタスクをAsanaに登録しますか？(y/n): ")

    # ユーザーが登録を希望する場合、Asana APIを呼び出してタスクを作成する
    if register.lower() == "y":
        # 最初のタスクをAsana上で一番上に表示するために、[::-1]で末尾から登録する
        for task in tasks[::-1]:
            task = task.split(",")
            create_asana_task(task[1], task[2])
        print("タスクを登録しました。")


if __name__ == "__main__":
    main()
