# 🚀 Быстрый старт - AML Orchestrator

## 📋 Что у вас есть

Ваш multi-agent AML анализ готов к запуску! Система включает:

- ✅ **6 специализированных агентов** для анализа отмывания денег
- ✅ **Демонстрационные данные** (20 транзакций с подозрительными паттернами)
- ✅ **Упрощенная демонстрация** (работает без API ключа)
- ✅ **Веб-дашборд** для визуализации
- ✅ **Полная система** с OpenAI интеграцией

## 🎯 Варианты запуска

### 1. 🎪 Быстрая демонстрация (рекомендуется для начала)

```bash
python run_demo.py
```

**Что покажет:**
- Загрузка 20 транзакций
- Обнаружение 10 высокорисковых транзакций
- Выявление 3 типов подозрительных паттернов
- Генерация отчета в JSON

### 2. 🌐 Веб-дашборд

```bash
streamlit run dashboard/app.py
```

**Откройте:** http://localhost:8501

**Возможности:**
- Обзор системы
- Статус агентов
- Управление отчетами
- Анализ паттернов

### 3. 🤖 Полная система (требует OpenAI API)

```bash
# 1. Настройте API ключ в .env
echo "OPENAI_API_KEY=your_key_here" >> .env

# 2. Запустите оркестратор
python -m orchestrator.main
```

## 📊 Что анализирует система

### Обнаруживаемые паттерны:

1. **🚨 Structuring** - Множественные транзакции под $10,000
2. **💰 Large Transactions** - Транзакции свыше $50,000
3. **⚡ Rapid Movement** - Быстрые перемещения средств
4. **🌊 Layering** - Сложные цепочки транзакций
5. **🔗 Integration** - Крупные депозиты из неизвестных источников

### Агенты системы:

- **Planner** - Планирует задачи анализа
- **Retriever** - Извлекает релевантные данные
- **Analysis** - Обнаруживает аномалии
- **Compliance** - Проверяет соответствие требованиям
- **Verifier** - Верифицирует результаты
- **Synthesizer** - Генерирует отчеты

## 🎯 Результаты демонстрации

После запуска `python run_demo.py` вы увидите:

```
🚀 AML Orchestrator - Simplified Demo
==================================================
✅ Loaded 20 transactions from data/transactions.csv

📊 Transaction Analysis
----------------------------------------
Total transactions: 20
Total amount: $269,500.00
Average amount: $13,475.00

Risk Level Distribution:
  high: 8 transactions
  low: 6 transactions
  medium: 3 transactions
  critical: 2 transactions

🚨 High-risk transactions: 10
High-risk transaction details:
  - John Doe → Bob Johnson: $9,500.00 (high)
  - John Doe → Alice Brown: $9,500.00 (high)
  - John Doe → Charlie Wilson: $9,500.00 (high)
  - John Doe → Diana Davis: $9,500.00 (high)
  - John Doe → Edward Miller: $9,500.00 (high)

🔍 Pattern Detection
----------------------------------------
🚨 Potential structuring detected: 2 entities
💰 Large transactions (>$50k): 2
⚡ Rapid movement detected: 3 instances

📋 AML Analysis Report
==================================================
Report generated: 2025-07-27T12:50:21.971003
Total transactions analyzed: 20
Total amount analyzed: $269,500.00
High-risk transactions: 10
Patterns detected: 3

Recommendations:
  1. Review 10 high-risk transactions
  2. File Suspicious Activity Report (SAR) for structuring patterns
  3. Conduct enhanced due diligence on large transaction entities

✅ Report saved to aml_report.json
```

## 🔧 Настройка для продакшена

### 1. Получите OpenAI API ключ
- Зарегистрируйтесь на https://platform.openai.com
- Создайте API ключ
- Добавьте в `.env` файл

### 2. Настройте данные
- Замените `data/transactions.csv` вашими данными
- Добавьте регулятивные документы в `regulatory_docs/`

### 3. Настройте мониторинг
- Настройте логирование в `logs/`
- Настройте метрики агентов
- Настройте алерты

## 📁 Структура файлов

```
Orchectra/
├── run_demo.py              # 🎪 Быстрая демонстрация
├── dashboard/app.py         # 🌐 Веб-интерфейс
├── orchestrator/main.py     # 🤖 Основная система
├── data/transactions.csv    # 📊 Демо данные
├── logs/                    # 📝 Логи
└── aml_report.json         # 📋 Сгенерированный отчет
```

## 🚨 Важные замечания

- **Демо версия**: Текущая версия предназначена для демонстрации
- **Безопасность**: Для продакшена требуется дополнительная настройка
- **Данные**: Используйте реальные данные для продакшена
- **Мониторинг**: Настройте логирование и алерты

## 🆘 Поддержка

- **Проблемы с запуском**: Проверьте Python 3.8+ и зависимости
- **Ошибки API**: Проверьте OpenAI API ключ
- **Проблемы с данными**: Убедитесь в корректности CSV файла

---

**🎉 Готово!** Ваша система анализа отмывания денег готова к использованию! 