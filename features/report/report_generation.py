import os
from dotenv import load_dotenv
from collections import Counter

import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_gigachat.chat_models import GigaChat

load_dotenv()


class ReportGeneration:
    def __init__(self):
        self._scv_path = os.path.join(os.path.dirname(__file__), "equipment.csv")
        self._model = GigaChat(
            credentials=os.environ["GIGACHAT_API_KEY"],
            verify_ssl_certs=False
        )
        self._report_chain = self._create_report_chain()

    def _create_report_chain(self):
        report_prompt = PromptTemplate(
            input_variables=["main_defect", "defect_count", "total_count", "processes_text"],
            template=(
                "Ты выступаешь в роли инженера по качеству.\n\n"
                "Дано:\n"
                "- Всего обнаружено дефектов: {total_count}\n"
                "- Наиболее часто встречающийся дефект: {main_defect}\n"
                "- Количество срабатываний этого дефекта: {defect_count}\n\n"
                "Ниже приведена информация о производственных процессах, "
                "которые связывают с этим дефектом (из справочника):\n"
                "{processes_text}\n\n"
                "Сформируй краткий структурированный отчет (3-4 предложения):\n"
                "1. Назови основной дефект и обоснуй, почему он считается основным.\n"
                "2. Перечисли возможные процессы, которые могли привести к этому дефекту, "
                "и кратко опиши механизм возникновения.\n"
                "3. При необходимости предложи направления для проверки/улучшения процессов.\n"
                "Отчет пиши по-русски, лаконично, по делу. Пиши единым текстом, без пропуска строк, без пунктов."
            )
        )
        report_chain = report_prompt | self._model
        return report_chain

    @staticmethod
    def load_defects_csv(path: str) -> pd.DataFrame:
        df = pd.read_csv(path, sep=";")

        required_cols = {"Defect", "Process", "Description"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"В CSV должны быть колонки: {required_cols}")
        return df

    @staticmethod
    def get_main_defect(defect_list):
        if not defect_list:
            raise ValueError("Список дефектов пуст!")

        counter = Counter(defect_list)
        main_defect, count = counter.most_common(1)[0]
        total = len(defect_list)

        return main_defect, count, total

    @staticmethod
    def get_process_info_for_defect(df: pd.DataFrame, defect_name: str):
        subset = df[df["Defect"] == defect_name]
        if subset.empty:
            return []

        subset = subset.drop_duplicates(["Process", "Description"])
        return subset.to_dict(orient="records")

    def generate_defect_report(self, defect_list) -> str:
        main_defect, count, total = self.get_main_defect(defect_list)

        df = self.load_defects_csv(self._scv_path)
        process_records = self.get_process_info_for_defect(df, main_defect)

        if process_records:
            processes_text = "\n".join(
                f"- Процесс: {r['Process']}. "
                f"Описание: {r['Description']}"
                for r in process_records
            )
        else:
            processes_text = (
                "Для данного дефекта в справочнике не найдено связанных процессов."
            )

        report = self._report_chain.invoke({
            "main_defect": main_defect,
            "defect_count": count,
            "total_count": total,
            "processes_text": processes_text,
        }
        )
        return report.content


if __name__ == "__main__":
    detected_defects = ["Окалины", "Окалины"]

    report = ReportGeneration()
    _report = report.generate_defect_report(detected_defects)
    print(_report)
