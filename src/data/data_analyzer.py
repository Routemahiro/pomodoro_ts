"""
データ分析とレポート生成

役割:
- 記録されたデータの分析
- 生産性レポートの生成

主な機能:
- 作業パターンの分析（時間帯別、曜日別など）
- タスク完了率の計算
- 集中時間の統計

使用するクラス/モジュール:
- data.database.Database
- pandas (データ処理用)
- matplotlib (グラフ生成用)

注意点:
- 大量のデータを扱う場合のパフォーマンスに注意
- ユーザーにとって意味のある指標を選択し、分かりやすい形で提示すること
"""

import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any
from src.data.database import Database

class DataAnalyzer:
    def __init__(self, database: Database):
        self.database = database

    def analyze_work_patterns(self) -> Dict[str, Any]:
        query = "SELECT start_time, duration FROM sessions"
        data = self.database.execute_query(query)
        df = pd.DataFrame(data)
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['hour'] = df['start_time'].dt.hour
        df['day_of_week'] = df['start_time'].dt.dayofweek

        hourly_pattern = df.groupby('hour')['duration'].mean()
        daily_pattern = df.groupby('day_of_week')['duration'].mean()

        return {
            'hourly_pattern': hourly_pattern.to_dict(),
            'daily_pattern': daily_pattern.to_dict()
        }

    def calculate_task_completion_rate(self) -> float:
        query = "SELECT status FROM tasks"
        data = self.database.execute_query(query)
        df = pd.DataFrame(data)
        total_tasks = len(df)
        completed_tasks = len(df[df['status'] == '完了'])
        return completed_tasks / total_tasks if total_tasks > 0 else 0

    def generate_focus_time_statistics(self) -> Dict[str, Any]:
        query = "SELECT duration FROM sessions"
        data = self.database.execute_query(query)
        df = pd.DataFrame(data)
        
        total_focus_time = df['duration'].sum()
        avg_focus_time = df['duration'].mean()
        max_focus_time = df['duration'].max()

        return {
            'total_focus_time': total_focus_time,
            'avg_focus_time': avg_focus_time,
            'max_focus_time': max_focus_time
        }

    def generate_productivity_report(self) -> Dict[str, Any]:
        work_patterns = self.analyze_work_patterns()
        task_completion_rate = self.calculate_task_completion_rate()
        focus_time_stats = self.generate_focus_time_statistics()

        return {
            'work_patterns': work_patterns,
            'task_completion_rate': task_completion_rate,
            'focus_time_stats': focus_time_stats
        }

    def plot_work_patterns(self):
        patterns = self.analyze_work_patterns()
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

        ax1.bar(patterns['hourly_pattern'].keys(), patterns['hourly_pattern'].values())
        ax1.set_title('Hourly Work Pattern')
        ax1.set_xlabel('Hour of the Day')
        ax1.set_ylabel('Average Duration (seconds)')

        ax2.bar(patterns['daily_pattern'].keys(), patterns['daily_pattern'].values())
        ax2.set_title('Daily Work Pattern')
        ax2.set_xlabel('Day of the Week')
        ax2.set_ylabel('Average Duration (seconds)')

        plt.tight_layout()
        plt.show()
