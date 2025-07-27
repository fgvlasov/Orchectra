# 🚀 Инструкции по запуску AML Orchestrator

## ✅ Статус системы

Ваша система **полностью готова к работе**! Все компоненты установлены и настроены.

## 🎯 Варианты запуска

### 1. 🎪 Быстрая демонстрация (рекомендуется для начала)

```bash
python run_demo.py
```

**Результат:** Анализ 20 транзакций, обнаружение паттернов, генерация отчета

### 2. 🌐 Веб-дашборд (работает!)

```bash
python -m streamlit run dashboard/app.py
```

**Откройте в браузере:** http://localhost:8501

**Возможности дашборда:**
- 📊 Обзор системы и метрики
- 🤖 Статус и производительность агентов
- 📋 Управление отчетами
- 🔍 Анализ обнаруженных паттернов
- ⚙️ Настройки системы

### 3. 🤖 Полная система (требует OpenAI API)

```bash
# 1. Добавьте API ключ в .env
echo "OPENAI_API_KEY=your_key_here" >> .env

# 2. Запустите оркестратор
python -m orchestrator.main
```

## 📊 Что вы увидите

### В демонстрации:
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

### В веб-дашборде:
- Интерактивные графики и диаграммы
- Статус агентов в реальном времени
- Управление отчетами
- Детальный анализ паттернов

## 🔧 Исправленные проблемы

### ✅ Решено:
- Установлены все зависимости (включая plotly)
- Исправлены конфликты версий Pydantic
- Настроена конфигурация для Windows
- Dashboard запускается через `python -m streamlit`

### 📝 Важные замечания для Windows:

1. **Streamlit запуск:**
   ```bash
   # Правильно:
   python -m streamlit run dashboard/app.py
   
   # Неправильно:
   streamlit run dashboard/app.py
   ```

2. **Пути к файлам:**
   - Используйте `copy` вместо `cp`
   - Пути с обратными слешами работают корректно

3. **Порты:**
   - Dashboard работает на http://localhost:8501
   - Проверьте, что порт не занят другими приложениями

## 🎯 Следующие шаги

### Для демонстрации:
1. Запустите: `python run_demo.py`
2. Изучите результаты в консоли
3. Откройте `aml_report.json` для детального анализа

### Для веб-интерфейса:
1. Запустите: `python -m streamlit run dashboard/app.py`
2. Откройте http://localhost:8501
3. Изучите все разделы дашборда

### Для продакшена:
1. Получите OpenAI API ключ
2. Добавьте в `.env` файл
3. Замените демо-данные на реальные
4. Настройте мониторинг и логирование

## 🆘 Устранение неполадок

### Dashboard не запускается:
```bash
# Проверьте установку plotly
pip install plotly

# Запустите с правильной командой
python -m streamlit run dashboard/app.py
```

### Ошибки импорта:
```bash
# Переустановите зависимости
pip install -r requirements.txt
```

### Порт занят:
```bash
# Запустите на другом порту
python -m streamlit run dashboard/app.py --server.port 8502
```

## 📁 Ключевые файлы

- `run_demo.py` - Быстрая демонстрация
- `dashboard/app.py` - Веб-интерфейс
- `orchestrator/main.py` - Основная система
- `data/transactions.csv` - Демо данные
- `aml_report.json` - Сгенерированный отчет
- `requirements.txt` - Зависимости (обновлен)

---

## 🎉 Готово!

Ваша система анализа отмывания денег полностью функциональна и готова к использованию!

**Быстрый старт:**
1. `python run_demo.py` - для демонстрации
2. `python -m streamlit run dashboard/app.py` - для веб-интерфейса
3. Откройте http://localhost:8501 в браузере

🚀 **Удачного использования!** 