# 🔍 Supply Chain Risk Audit - Multi-Agent Platform

Этот проект демонстрирует адаптацию существующей multi-agent платформы для аудита рисков цепочки поставок (ESG/Supply-Chain risk assessment). Система использует конфигурационный подход для переключения между различными use cases без изменения основного кода.

## 🎯 Возможности

- **Конфигурационная архитектура**: Переключение между AML и Supply Chain audit через YAML конфигурации
- **ESG анализ**: Оценка экологических, социальных и управленческих рисков
- **Compliance проверка**: Проверка соответствия регулятивным требованиям (EU CSDDD, ISO 14001, SA8000)
- **Risk scoring**: Композитная оценка рисков на основе множественных факторов
- **Multi-agent консенсус**: Верификация результатов через несколько агентов
- **Гибкая архитектура**: Легкое добавление новых агентов и use cases

## 🏗️ Архитектура

### Агенты для Supply Chain Audit

1. **InternalRetrieverAgent** - Загрузка и фильтрация данных поставщиков
2. **ExternalRetrieverAgent** - Получение внешних ESG и compliance данных
3. **RiskAnalysisAgent** - Анализ рисков поставщиков
4. **ESGComplianceAgent** - Проверка ESG compliance
5. **VerifierAgent** - Верификация результатов
6. **SynthesizerAgent** - Генерация отчетов

### Факторы риска

- **Country ESG Rating**: ESG рейтинг страны поставщика
- **Prior Violations**: Предыдущие нарушения
- **Supply Category Risk**: Риск категории поставок
- **Financial Stability**: Финансовая стабильность

### Compliance фреймворки

- **EU CSDDD**: European Union Corporate Sustainability Due Diligence Directive
- **ISO 14001**: Environmental Management Systems
- **SA8000**: Social Accountability International Standard
- **GRI Standards**: Global Reporting Initiative

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск демонстрации

```bash
# Демонстрация supply chain audit
python run_supply_chain_demo.py

# Или через оркестратор с конфигурацией
python -m orchestrator.main --config configs/supply_chain.yaml
```

### 3. Веб-дашборд

```bash
python -m streamlit run dashboard/app.py
```

## 📊 Демонстрационные данные

Система включает демонстрационные данные 20 поставщиков с различными профилями риска:

- **Низкий риск**: GreenTech Solutions (Германия), Clean Energy Systems (Дания)
- **Средний риск**: Global Manufacturing Co (Китай), Sustainable Textiles (Индия)
- **Высокий риск**: MetalCorp Industries (Россия), Forest Products Inc (Бразилия)
- **Критический риск**: Chemical Solutions Ltd (Китай), Steel Dynamics (Украина)

## ⚙️ Конфигурация

### Основная конфигурация

```yaml
# configs/supply_chain.yaml
name: "supply_chain_audit"
description: "ESG and compliance risk assessment for supply chain vendors"

# Источники данных
data_sources:
  suppliers_file: "data/suppliers.csv"
  external_documents:
    - "data/external/sanction_lists/"
    - "data/external/sustainability_reports/"

# Настройки агентов
agents:
  risk_analysis:
    risk_factors:
      country_esg_rating:
        weight: 0.25
        threshold: 0.6
      prior_violations:
        weight: 0.30
        threshold: 0.7
```

### Настройка порогов

```yaml
scoring:
  risk_levels:
    low: [0.0, 0.3]
    medium: [0.3, 0.6]
    high: [0.6, 0.8]
    critical: [0.8, 1.0]
  
  consensus_threshold: 0.8
  minimum_risk_score: 0.4
  flag_threshold: 0.6
```

## 🔧 Использование

### 1. Подготовка данных поставщиков

Создайте CSV файл с данными поставщиков:

```csv
id,name,country,industry,supplier_type,esg_score,financial_stability,prior_violations,supply_category,annual_spend,contract_duration,risk_level
supplier_001,Company Name,Country,Industry,Tier 1,0.85,0.8,0,Category,1000000,3,low
```

### 2. Запуск анализа

```python
from orchestrator.main import Orchestrator

# Создание оркестратора с конфигурацией
orchestrator = Orchestrator("configs/supply_chain.yaml")

# Запуск анализа
report = await orchestrator.process_query(
    "Assess ESG and compliance risks for suppliers in the file data/suppliers.csv"
)
```

### 3. Пользовательские агенты

Создание нового агента для supply chain:

```python
from orchestrator.agents.base import BaseAgent

class CustomSupplyChainAgent(BaseAgent):
    async def process_task(self, task):
        # Ваша логика анализа
        return TaskResult(
            task_id=task.id,
            success=True,
            data={"custom_analysis": "results"}
        )
```

## 📋 Структура отчета

Отчет включает следующие разделы:

```json
{
  "metadata": {
    "report_type": "supply_chain_risk_audit",
    "total_suppliers": 20,
    "analysis_version": "1.0.0"
  },
  "executive_summary": {
    "total_suppliers_analyzed": 20,
    "high_risk_suppliers": 8,
    "non_compliant_suppliers": 6,
    "overall_risk_score": 0.45,
    "compliance_rate": 0.70
  },
  "risk_assessment": {
    "risk_distribution": {
      "low": 5,
      "medium": 7,
      "high": 5,
      "critical": 3
    },
    "high_risk_suppliers": [...]
  },
  "compliance_analysis": {
    "compliance_summary": {...},
    "non_compliant_suppliers": [...]
  },
  "supplier_details": [...],
  "recommendations": [...],
  "action_items": [...]
}
```

## 🧪 Тестирование

### Unit тесты

```bash
# Запуск unit тестов
pytest tests/test_supply_chain_agents.py -v

# Запуск интеграционных тестов
pytest tests/test_supply_chain_integration.py -v
```

### Тестовые данные

Система включает автоматические тесты с проверкой:

- Корректности анализа рисков
- Точности compliance оценки
- Валидации данных поставщиков
- Генерации отчетов

## 🔄 Расширение функциональности

### Добавление нового фактора риска

1. Обновите конфигурацию в `configs/supply_chain.yaml`
2. Добавьте логику в `RiskAnalysisAgent`
3. Обновите тесты

### Добавление нового compliance фреймворка

1. Добавьте фреймворк в конфигурацию
2. Реализуйте проверки в `ESGComplianceAgent`
3. Обновите документацию

### Интеграция с внешними API

```python
class ExternalDataAgent(BaseAgent):
    async def _call_external_api(self, endpoint, data):
        # Интеграция с внешними API
        response = await self.http_client.post(endpoint, json=data)
        return response.json()
```

## 📈 Метрики и мониторинг

### Ключевые метрики

- **Risk Distribution**: Распределение поставщиков по уровням риска
- **Compliance Rate**: Процент compliant поставщиков
- **Processing Time**: Время обработки анализа
- **Agent Performance**: Производительность агентов

### Логирование

```python
from orchestrator.utils.logging import logger

logger.info("Supply chain analysis started")
logger.warning("High-risk supplier detected")
logger.error("External API connection failed")
```

## 🚨 Обработка ошибок

### Типичные ошибки и решения

1. **FileNotFoundError**: Проверьте пути к файлам данных
2. **ValidationError**: Проверьте формат данных поставщиков
3. **APIError**: Проверьте подключение к внешним API
4. **ConfigurationError**: Проверьте YAML конфигурацию

### Отладка

```bash
# Включение debug логирования
export LOG_LEVEL=DEBUG

# Запуск с подробным выводом
python run_supply_chain_demo.py --verbose
```

## 📚 Дополнительные ресурсы

- [EU CSDDD Directive](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A52022PC0071)
- [ISO 14001 Standard](https://www.iso.org/iso-14001-environmental-management.html)
- [SA8000 Standard](https://sa-intl.org/programs/sa8000/)
- [GRI Standards](https://www.globalreporting.org/standards/)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Добавьте тесты для новой функциональности
4. Обновите документацию
5. Создайте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл LICENSE для подробностей. 