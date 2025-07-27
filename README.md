# 🚀 AML Orchestrator - Multi-Agent Anti-Money Laundering Analysis Platform

Платформа для анализа отмывания денег с использованием многоагентной системы на базе ИИ.

## 🎯 Возможности

- **Многоагентная архитектура**: 6 специализированных агентов для разных задач
- **Анализ транзакций**: Обнаружение подозрительных паттернов
- **Соответствие требованиям**: Проверка соответствия регулятивным требованиям
- **Верификация**: Многоагентный консенсус для повышения точности
- **Интерактивный dashboard**: Веб-интерфейс для мониторинга и управления

## 🏗️ Архитектура

### Агенты

1. **Planner Agent** - Планирование задач и создание графа выполнения
2. **Retriever Agent** - Извлечение релевантных данных
3. **Analysis Agent** - Анализ транзакций и обнаружение аномалий
4. **Compliance Agent** - Проверка соответствия регулятивным требованиям
5. **Verifier Agent** - Верификация результатов через консенсус
6. **Synthesizer Agent** - Синтез финального отчета

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Клонирование репозитория
git clone <repository-url>
cd Orchectra

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка конфигурации

```bash
# Копирование файла конфигурации
copy env.example .env

# Редактирование .env файла
# Добавьте ваш OpenAI API ключ:
# OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Запуск демонстрации

```bash
# Упрощенная демонстрация (работает без API ключа)
python run_demo.py
```

### 4. Запуск полной системы

```bash
# Запуск основного оркестратора
python -m orchestrator.main

# Запуск веб-дашборда
streamlit run dashboard/app.py
```

## 📊 Демонстрация

### Упрощенная демонстрация

Запустите `python run_demo.py` для просмотра базовой функциональности:

- Загрузка данных транзакций
- Анализ статистики
- Обнаружение паттернов
- Генерация отчета

### Веб-дашборд

Откройте `http://localhost:8501` для доступа к интерактивному дашборду:

- **Overview**: Общий обзор системы
- **Agents**: Статус и метрики агентов
- **Reports**: Управление отчетами
- **Patterns**: Анализ обнаруженных паттернов
- **Settings**: Настройки системы

## 📁 Структура проекта

```
Orchectra/
├── orchestrator/           # Основная логика
│   ├── agents/            # Агенты системы
│   ├── config/            # Конфигурация
│   ├── models/            # Модели данных
│   └── utils/             # Утилиты
├── dashboard/             # Веб-интерфейс
├── data/                  # Данные транзакций
├── tests/                 # Тесты
├── run_demo.py           # Демонстрационный скрипт
├── example.py            # Примеры использования
└── requirements.txt      # Зависимости
```

## 🔧 Конфигурация

### Основные настройки (.env)

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=2000

# Agent Configuration
PLANNER_MAX_TASKS=10
RETRIEVER_TOP_K=5
RETRIEVER_SIMILARITY_THRESHOLD=0.7
ANALYSIS_ANOMALY_THRESHOLD=0.05
VERIFIER_CONSENSUS_THRESHOLD=0.8

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/orchestrator.log

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## 📈 Примеры использования

### Базовый анализ

```python
from orchestrator.main import Orchestrator

async def analyze_transactions():
    orchestrator = Orchestrator()
    await orchestrator.start()
    
    query = "Analyze transactions for suspicious patterns in the last 30 days"
    report = await orchestrator.process_query(query)
    
    print(f"Generated report: {report.title}")
    await orchestrator.stop()
```

### Обнаружение паттернов

- **Structuring**: Множественные транзакции под $10,000
- **Layering**: Сложные цепочки транзакций
- **Integration**: Крупные депозиты из неизвестных источников
- **Rapid Movement**: Быстрые перемещения средств

## 🧪 Тестирование

```bash
# Запуск тестов
pytest tests/

# Запуск с покрытием
pytest --cov=orchestrator tests/
```

## 📊 Примеры отчетов

Система генерирует детальные отчеты в формате JSON:

```json
{
  "id": "report_2024_001",
  "title": "AML Analysis Report - Q1 2024",
  "status": "completed",
  "summary": {
    "total_transactions_analyzed": 1500,
    "total_amount_analyzed": 2500000.00,
    "suspicious_patterns_found": 12,
    "high_risk_patterns": 3,
    "compliance_violations": 2
  },
  "patterns": [
    {
      "type": "structuring",
      "confidence": 0.85,
      "risk_level": "high",
      "affected_transactions": 5,
      "total_amount": 47500.00
    }
  ],
  "recommendations": [
    "File Suspicious Activity Report (SAR)",
    "Implement enhanced monitoring",
    "Conduct customer due diligence review"
  ]
}
```

## 🔍 Мониторинг

### Метрики агентов

- Статус выполнения
- Количество обработанных задач
- Процент успешности
- Время выполнения

### Логирование

- Структурированные логи
- Аудит действий
- Отслеживание ошибок

## 🚨 Требования

- Python 3.8+
- OpenAI API ключ
- 4GB+ RAM
- Интернет-соединение

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License

## 🆘 Поддержка

- Создайте Issue для багов
- Обсуждения в Discussions
- Документация в Wiki

---

**Примечание**: Это демонстрационная версия. Для продакшена требуется дополнительная настройка безопасности и соответствия требованиям. 