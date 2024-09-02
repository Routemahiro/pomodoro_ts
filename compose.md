classDiagram
    class MainWindow
    class TimerWidget
    class CharacterWidget
    class DashboardWidget
    class SlidePanel
    class TaskPanel
    class AIChatPanel
    class SettingsDialog
    class ReportWindow

    class Timer
    class SessionManager
    class TaskManager
    class AIInterface
    class CharacterState
    class NotificationManager

    class Database
    class DataAnalyzer
    class TaskData
    class AIConversation
    class SettingsManager

    class Config
    class Helpers
    class UIHelpers
    class Constants

    MainWindow --> TimerWidget
    MainWindow --> CharacterWidget
    MainWindow --> DashboardWidget
    MainWindow --> SlidePanel
    MainWindow --> SettingsDialog
    MainWindow --> ReportWindow

    SlidePanel --> TaskPanel
    SlidePanel --> AIChatPanel

    Timer --> NotificationManager
    SessionManager --> Database
    TaskManager --> Database
    AIInterface --> AIConversation

    DataAnalyzer --> Database
    SettingsManager --> Config

    MainWindow --> Timer
    MainWindow --> SessionManager
    MainWindow --> TaskManager
    MainWindow --> AIInterface
    MainWindow --> CharacterState

    TaskPanel --> TaskManager
    AIChatPanel --> AIInterface
    ReportWindow --> DataAnalyzer

    note for MainWindow "アプリケーションのメインウィンドウ"
    note for Timer "ポモドーロタイマーのコアロジック"
    note for Database "SQLiteデータベース操作"
    note for Config "アプリケーション全体の設定管理"