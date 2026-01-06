# 📋 **Requirements Specification Document (RSD) v2.0**
## **Telegram Gifts Buyer Bot - Modernized Edition**

---

> [!NOTE]
> This is the modernized and future-proofed version of the RSD, incorporating 2025 best practices in security, scalability, observability, and developer experience.

---

## **1. نظرة عامة على المشروع (Project Overview)**

### **1.1 الوصف (Description)**
بوت تيليجرام تلقائي عالي الأداء لشراء الهدايا بناءً على معايير ذكية، مع إدارة رصيد متقدمة، أولوية للهدايا النادرة، ومراقبة شاملة للعمليات.

### **1.2 الهدف (Objective)**
أتمتة عملية شراء الهدايا من تيليجرام مع ضمان:
- **الموثوقية العالية:** تشغيل مستمر 24/7 بدون توقف
- **المرونة:** تكوين سهل ومتقدم
- **الأمان:** حماية بيانات الاعتماد والجلسات
- **القابلية للرصد:** مراقبة وتنبيهات في الوقت الفعلي

### **1.3 الفئة المستهدفة (Target Audience)**
- مستخدمون نشطون في تيليجرام
- تجار الهدايا الرقمية
- مستخدمون يبحثون عن هدايا نادرة محدودة
- مطورون يريدون توسيع البوت

---

## **2. التحليل التقني والتحديث (Technical Audit & Modernization)**

### **2.1 المشاكل في الإصدار السابق**

| المكون | المشكلة | التأثير |
|--------|---------|---------|
| **Config (INI)** | صيغة قديمة بدون validation | أخطاء صامتة، صعوبة الصيانة |
| **pyrofork** | Fork غير رسمي من Pyrogram | مخاطر أمنية، توقف الدعم |
| **Logging** | `print()` statements | لا يوجد structured logging |
| **Error Handling** | Basic try/except | فقدان معلومات التشخيص |
| **Docker** | بدون health checks | عدم كشف حالات الفشل |
| **Data Storage** | ملفات JSON مباشرة | لا يوجد نسخ احتياطي، race conditions |
| **Rate Limiting** | غائب | احتمال حظر الحساب |
| **Secrets** | في config.ini | خطر التسريب في Git |

### **2.2 التقنيات المقترحة للتحديث**

| المكون | القديم | الجديد (2025) | السبب |
|--------|--------|---------------|-------|
| **Python** | 3.13 | 3.12+ (LTS) | استقرار أفضل، دعم طويل المدى |
| **Config** | INI + configparser | **pydantic-settings v2** | Type validation, env support |
| **Telegram Client** | pyrofork | **Pyrogram 2.x Official** أو **Telethon** | دعم رسمي، أمان أفضل |
| **Logging** | print() | **structlog** + **Loguru** | JSON logs, correlation IDs |
| **Storage** | JSON files | **SQLite + aiosqlite** | ACID, async, migrations |
| **Secrets** | config.ini | **Environment Variables** + **Docker Secrets** | أمان، 12-factor app |
| **Container** | Basic Docker | **Multi-stage builds** + **Health checks** | أمان، حجم أصغر |
| **Observability** | لا يوجد | **OpenTelemetry** + **Prometheus metrics** | Production monitoring |

---

## **3. User Stories (محدّثة)**

### **US-1: إعداد البوت الآمن**
**كـ** مستخدم  
**أريد** إعداد البوت ببيانات تيليجرام بطريقة آمنة  
**لكي** أبدأ استخدامه دون خطر تسريب البيانات

**Acceptance Criteria:**
- المستخدم يضبط المتغيرات البيئية (`API_ID`, `API_HASH`, `PHONE_NUMBER`)
- البوت يتحقق من صحة جميع الإعدادات عند البدء (pydantic validation)
- رسائل خطأ واضحة عند وجود إعدادات ناقصة أو خاطئة
- الجلسة مشفرة ومحفوظة في `./data/sessions/`
- لا توجد بيانات حساسة في أي ملف مُتتبع بـ Git

---

### **US-2: مراقبة الهدايا بذكاء**
**كـ** مستخدم  
**أريد** مراقبة ذكية للهدايا مع احترام حدود API  
**لكي** لا يتم حظر حسابي

**Acceptance Criteria:**
- البوت يفحص الهدايا كل `INTERVAL` ثانية (قابل للتعديل، الحد الأدنى: 5 ثوانٍ)
- يطبق **Exponential Backoff** عند أخطاء الشبكة
- يحترم **Rate Limits** الخاصة بـ Telegram API
- يعرض حالة المراقبة في الـ console مع **Rich progress indicators**
- يحفظ تاريخ الهدايا في قاعدة بيانات SQLite

---

### **US-3: تصفية متقدمة للهدايا**
**كـ** مستخدم  
**أريد** تصفية الهدايا بمعايير متعددة ومرنة  
**لكي** أتحكم بدقة في ما أشتريه

**Acceptance Criteria:**
- تحديد نطاقات أسعار متعددة بصيغة YAML/JSON
- تصفية حسب:
  - نطاق السعر (`min_price`, `max_price`)
  - حد الكمية المتاحة (`supply_limit`)
  - قابلية الترقية (`upgradable_only`)
  - حالة التوفر (`available_only`)
- دعم **Regular Expressions** لأسماء الهدايا (اختياري)
- تحديث التصفية بدون إعادة تشغيل البوت (Hot Reload)

---

### **US-4: إرسال هدايا ذكي**
**كـ** مستخدم  
**أريد** إرسال هدايا لمستلمين متعددين بكميات مختلفة  
**لكي** أغطي احتياجاتي بفعالية

**Acceptance Criteria:**
- تحديد مستلمين متعددين (usernames, user IDs, channel IDs)
- دعم **القوائم البيضاء** والسوداء للمستلمين
- تحديد أولويات المستلمين (primary, fallback)
- تقسيم تلقائي للكميات الكبيرة لتجنب Rate Limits
- إمكانية جدولة الإرسال (مستقبلي)

---

### **US-5: أولوية ذكية متعددة المعايير**
**كـ** مستخدم  
**أريد** نظام أولويات ذكي ومرن  
**لكي** أحصل على أفضل الهدايا تلقائياً

**Acceptance Criteria:**
- ترتيب حسب معايير متعددة:
  - الندرة (`total_amount` الأقل أولاً)
  - السعر (الأقل أو الأعلى حسب الإعداد)
  - قابلية الترقية
  - تاريخ الإضافة
- دعم **Custom Priority Functions** عبر Python expressions
- إمكانية تعطيل الأولوية لنطاقات محددة

---

### **US-6: شراء هدايا قابلة للترقية**
**كـ** مستخدم  
**أريد** تفضيل الهدايا القابلة للترقية  
**لكي** أستفيد من ميزة الترقية لاحقاً

**Acceptance Criteria:**
- فلترة بواسطة `upgradable_only: true`
- عرض معلومات الترقية (سعر الترقية، المميزات)
- إحصائيات عن الهدايا القابلة/غير القابلة للترقية
- خيار لتتبع الهدايا المشتراة القابلة للترقية

---

### **US-7: إدارة رصيد متقدمة**
**كـ** مستخدم  
**أريد** إدارة ذكية للرصيد مع تنبيهات  
**لكي** لا أفاجأ بنفاد الرصيد

**Acceptance Criteria:**
- فحص الرصيد قبل كل عملية شراء
- حساب الكمية القابلة للشراء: `min(quantity, balance // price)`
- **Reserve Balance:** إمكانية تحديد حد أدنى للرصيد المحجوز
- إشعار عند انخفاض الرصيد تحت حد معين
- تقرير يومي بـ استهلاك الرصيد وملخص المشتريات
- دعم **Budget Limits** يومية/أسبوعية/شهرية

---

### **US-8: نظام إشعارات متقدم**
**كـ** مستخدم  
**أريد** إشعارات مفصلة وقابلة للتخصيص  
**لكي** أتابع نشاط البوت بفعالية

**Acceptance Criteria:**
- إشعارات عبر قناة تيليجرام (`NOTIFICATION_CHANNEL_ID`)
- أنواع الإشعارات:
  - ✅ نجاح الشراء (مع تفاصيل الهدية، المستلم، السعر)
  - ⚠️ رصيد غير كافٍ
  - 📝 شراء جزئي
  - 🔴 أخطاء حرجة
  - 📊 ملخص دوري
- إشعارات **قابلة للتخصيص** (تفعيل/تعطيل كل نوع)
- دعم **Webhook notifications** (Discord, Slack, etc.)
- تضمين **Action Buttons** في الإشعارات (مستقبلي)

---

### **US-9: واجهة متعددة اللغات موسّعة**
**كـ** مستخدم  
**أريد** استخدام البوت بلغتي المفضلة  
**لكي** أفهم كل الرسائل بوضوح

**Acceptance Criteria:**
- دعم: الإنجليزية (`EN`), الروسية (`RU`), العربية (`AR`)
- ملفات الترجمة بصيغة YAML في `locales/`
- الكشف التلقائي عن اللغة من نظام التشغيل (اختياري)
- دعم RTL (من اليمين لليسار) للعربية
- إمكانية المساهمة بترجمات جديدة

---

### **US-10: تشغيل حاوية آمن**
**كـ** DevOps Engineer  
**أريد** تشغيل البوت في Docker بشكل آمن وقابل للمراقبة  
**لكي** أضمن استمرارية التشغيل

**Acceptance Criteria:**
- **Multi-stage Dockerfile** (حجم أصغر، أمان أفضل)
- **Health checks** مدمجة
- **Non-root user** داخل الحاوية
- **Resource limits** (CPU, Memory)
- **Graceful shutdown** عند إيقاف الحاوية
- **Log rotation** تلقائي
- دعم **Docker Secrets** للبيانات الحساسة
- **Kubernetes-ready** manifests (اختياري)

---

## **4. Use Cases (محدّثة)**

### **UC-1: إعداد البوت لأول مرة (محدّث)**

**Actors:** المستخدم، النظام  
**Preconditions:** حساب تيليجرام نشط، Docker مثبت

**Main Flow:**
1. المستخدم يستنسخ الريبو:
   ```bash
   git clone https://github.com/3bkader-gpt/Girt_hunter.git
   cd Girt_hunter
   ```
2. ينسخ ملف البيئة النموذجي:
   ```bash
   cp .env.example .env
   ```
3. يعدل `.env` بإدخال البيانات الحساسة:
   ```env
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   TELEGRAM_PHONE_NUMBER=+1234567890
   ```
4. يعدل `config.yaml` للإعدادات غير الحساسة
5. يبني ويشغل البوت:
   ```bash
   docker compose up -d
   ```
6. يتابع السجلات لإكمال تسجيل الدخول:
   ```bash
   docker compose logs -f
   ```
7. يدخل رمز OTP عند الطلب
8. البوت يحفظ الجلسة ويبدأ المراقبة

**Postconditions:** البوت يعمل، الجلسة محفوظة، المراقبة نشطة

**Alternative Flow 5a:** خطأ في الإعدادات
- البوت يعرض رسالة خطأ واضحة مع الحقل الخاطئ
- المستخدم يصحح ويعيد التشغيل

---

### **UC-2: شراء هدية جديدة تلقائياً (محدّث)**

**Actors:** البوت، Telegram API  
**Preconditions:** البوت يعمل، رصيد كافٍ، إعدادات صحيحة

**Main Flow:**
1. البوت يفحص الهدايا كل `INTERVAL` ثانية
2. يكتشف هدية جديدة تطابق المعايير
3. يتحقق من:
   - السعر داخل النطاق المحدد
   - الكمية المتاحة (`available_amount`) ضمن الحد
   - قابلية الترقية (إن كان مطلوباً)
   - الهدية غير في القائمة السوداء
4. يرتب الهدايا حسب نظام الأولويات
5. يفحص الرصيد المتاح
6. يحسب الكمية القابلة للشراء مع احترام الحد اليومي
7. يشتري مع **Retry logic** (حتى 3 محاولات)
8. يرسل إشعارات النجاح مع التفاصيل
9. يحفظ السجل في قاعدة البيانات
10. يحدث الإحصائيات

**Exception Flows:**
- **E1: Rate Limit:** انتظار مع exponential backoff
- **E2: Network Error:** إعادة المحاولة
- **E3: Gift Sold Out:** تسجيل وتخطي
- **E4: Insufficient Balance:** شراء جزئي مع إشعار

**Postconditions:** الهدايا مُرسلة، السجلات محدّثة، الإحصائيات محدّثة

---

## **5. المتطلبات الوظيفية (Functional Requirements)**

### **FR-1: المصادقة والجلسات**
| ID | المتطلب | الأولوية |
|----|---------|----------|
| FR-1.1 | استخدام Pyrogram 2.x الرسمي للمصادقة | P0 |
| FR-1.2 | حفظ الجلسات المشفرة في `./data/sessions/` | P0 |
| FR-1.3 | دعم إعادة الاتصال التلقائي مع backoff | P0 |
| FR-1.4 | دعم Two-Factor Authentication (2FA) | P1 |
| FR-1.5 | تحديث الجلسة تلقائياً قبل انتهائها | P1 |

### **FR-2: مراقبة الهدايا**
| ID | المتطلب | الأولوية |
|----|---------|----------|
| FR-2.1 | فحص دوري قابل للتعديل (min: 5s, default: 10s) | P0 |
| FR-2.2 | اكتشاف الهدايا الجديدة بمقارنة الـ hash | P0 |
| FR-2.3 | تخزين التاريخ في SQLite مع indexing | P0 |
| FR-2.4 | دعم webhooks للإشعارات الخارجية | P2 |
| FR-2.5 | Hot reload للإعدادات بدون إعادة تشغيل | P2 |

### **FR-3: التصفية والأولويات**
| ID | المتطلب | الأولوية |
|----|---------|----------|
| FR-3.1 | تصفية بنطاقات أسعار متعددة | P0 |
| FR-3.2 | تصفية بحد الكمية المتاحة | P0 |
| FR-3.3 | تصفية بقابلية الترقية | P0 |
| FR-3.4 | ترتيب بالندرة (total_amount ASC) | P0 |
| FR-3.5 | قوائم سوداء للهدايا/المستلمين | P1 |
| FR-3.6 | Custom priority expressions | P2 |

### **FR-4: الشراء وإدارة الرصيد**
| ID | المتطلب | الأولوية |
|----|---------|----------|
| FR-4.1 | التحقق من الرصيد قبل كل عملية | P0 |
| FR-4.2 | الشراء الجزئي عند عدم كفاية الرصيد | P0 |
| FR-4.3 | Retry logic مع exponential backoff | P0 |
| FR-4.4 | Reserve balance (حد أدنى محجوز) | P1 |
| FR-4.5 | Budget limits يومية/أسبوعية | P1 |
| FR-4.6 | Transaction logging للمراجعة | P0 |

### **FR-5: الإشعارات**
| ID | المتطلب | الأولوية |
|----|---------|----------|
| FR-5.1 | إشعارات Telegram channel | P0 |
| FR-5.2 | أنواع إشعارات قابلة للتفعيل/التعطيل | P0 |
| FR-5.3 | ملخص دوري (كل ساعة/يوم) | P1 |
| FR-5.4 | دعم Discord/Slack webhooks | P2 |
| FR-5.5 | Email notifications | P3 |

### **FR-6: التدويل (i18n)**
| ID | المتطلب | الأولوية |
|----|---------|----------|
| FR-6.1 | دعم EN, RU, AR | P0 |
| FR-6.2 | ملفات YAML للترجمات | P0 |
| FR-6.3 | كشف تلقائي للغة النظام | P2 |
| FR-6.4 | دعم RTL للعربية | P1 |

---

## **6. المتطلبات غير الوظيفية (Non-Functional Requirements)**

### **NFR-1: الأداء**
| ID | المتطلب | القيمة المستهدفة |
|----|---------|-----------------|
| NFR-1.1 | استهلاك الذاكرة | ≤ 150MB (idle), ≤ 300MB (peak) |
| NFR-1.2 | استهلاك CPU | ≤ 5% (idle), ≤ 50% (processing) |
| NFR-1.3 | وقت استجابة للهدايا الجديدة | ≤ INTERVAL + 2s |
| NFR-1.4 | Cold start time | ≤ 5s |
| NFR-1.5 | تشغيل مستمر | 24/7/365 بدون restart يدوي |

### **NFR-2: الموثوقية**
| ID | المتطلب | القيمة المستهدفة |
|----|---------|-----------------|
| NFR-2.1 | Uptime | ≥ 99.5% |
| NFR-2.2 | Error recovery time | ≤ 30s |
| NFR-2.3 | Data persistence | Zero data loss |
| NFR-2.4 | Graceful degradation | Yes |

### **NFR-3: الأمان**
| ID | المتطلب | التفاصيل |
|----|---------|----------|
| NFR-3.1 | Secrets management | Environment variables / Docker secrets فقط |
| NFR-3.2 | Session encryption | AES-256 للجلسات المحفوظة |
| NFR-3.3 | No sensitive data in logs | Redaction التلقائية |
| NFR-3.4 | Container security | Non-root user, read-only filesystem |
| NFR-3.5 | Dependency scanning | Dependabot / Snyk مفعل |
| NFR-3.6 | Git security | `.gitignore` شامل، pre-commit hooks |

### **NFR-4: القابلية للرصد (Observability)**
| ID | المتطلب | التقنية |
|----|---------|---------|
| NFR-4.1 | Structured logging | JSON format via structlog |
| NFR-4.2 | Metrics endpoint | Prometheus `/metrics` |
| NFR-4.3 | Health endpoint | HTTP `/health` |
| NFR-4.4 | Distributed tracing | OpenTelemetry (optional) |
| NFR-4.5 | Alerting | Prometheus Alertmanager / Telegram |

### **NFR-5: قابلية الصيانة**
| ID | المتطلب | التفاصيل |
|----|---------|----------|
| NFR-5.1 | Code style | Ruff linter + formatter |
| NFR-5.2 | Type hints | 100% coverage, mypy strict |
| NFR-5.3 | Test coverage | ≥ 80% |
| NFR-5.4 | Documentation | Docstrings + README + API docs |
| NFR-5.5 | Dependency management | uv / poetry مع lockfile |

---

## **7. نموذج البيانات (Data Model)**

### **7.1 Gift Entity**
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Gift(BaseModel):
    """Represents a Telegram gift item."""
    id: int = Field(..., description="Unique gift identifier")
    name: str = Field(..., description="Gift display name")
    price: int = Field(..., ge=0, description="Price in Telegram Stars")
    total_amount: int = Field(..., ge=0, description="Total supply")
    available_amount: int = Field(..., ge=0, description="Remaining supply")
    is_limited: bool = Field(default=False, description="Limited edition flag")
    is_sold_out: bool = Field(default=False, description="Sold out flag")
    upgrade_price: Optional[int] = Field(None, ge=0, description="Upgrade cost")
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_checked: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def is_upgradable(self) -> bool:
        return self.upgrade_price is not None
    
    @property
    def availability_percentage(self) -> float:
        if self.total_amount == 0:
            return 0.0
        return (self.available_amount / self.total_amount) * 100
```

### **7.2 Purchase Record**
```python
class PurchaseRecord(BaseModel):
    """Tracks a successful gift purchase."""
    id: int = Field(..., description="Auto-generated ID")
    gift_id: int
    gift_name: str
    recipient_id: int
    recipient_username: Optional[str]
    price: int
    quantity: int
    total_cost: int
    purchased_at: datetime = Field(default_factory=datetime.utcnow)
    transaction_id: Optional[str] = None
```

### **7.3 Configuration Schema (config.yaml)**
```yaml
# config.yaml
telegram:
  interval_seconds: 10          # Polling interval (min: 5)
  max_retries: 3                # Retry attempts per purchase
  retry_delay_seconds: 2        # Initial retry delay

notifications:
  channel_id: -1001234567890    # Notification channel (-100 to disable)
  types:
    purchase_success: true
    purchase_partial: true
    balance_low: true
    errors: true
    daily_summary: true
  low_balance_threshold: 1000   # Stars

gifts:
  ranges:
    - name: "Budget Range"
      min_price: 1
      max_price: 500
      supply_limit: 500000
      quantity_per_recipient: 1
      recipients:
        - "@user1"
        - 123456789
      upgradable_only: false
      
    - name: "Premium Range"
      min_price: 1000
      max_price: 5000
      supply_limit: 10000
      quantity_per_recipient: 2
      recipients:
        - "@vip_user"
      upgradable_only: true
      
  prioritize_low_supply: true
  blacklist:
    gifts: []                   # Gift IDs to skip
    recipients: []              # User IDs to never send to

budget:
  daily_limit: 50000            # Max daily spend (0 = unlimited)
  reserve_balance: 1000         # Always keep this balance

language: "EN"                  # EN | RU | AR
```

### **7.4 Environment Variables (.env)**
```env
# .env.example
# ⚠️ NEVER commit the actual .env file!

# Required
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
TELEGRAM_PHONE_NUMBER=

# Optional
LOG_LEVEL=INFO
METRICS_PORT=9090
HEALTH_PORT=8080
```

---

## **8. البنية التقنية (Architecture)**

### **8.1 Component Diagram**
```
┌─────────────────────────────────────────────────────────────────┐
│                        Gift Hunter Bot                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Config     │  │   Telegram   │  │    Notification      │  │
│  │   Manager    │  │   Client     │  │    Service           │  │
│  │  (Pydantic)  │  │  (Pyrogram)  │  │ (Telegram/Webhooks)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         ▼                 ▼                      ▼              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Core Engine                            │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │  │
│  │  │  Monitor   │  │  Filter    │  │  Purchase Engine   │  │  │
│  │  │  Service   │→ │  Pipeline  │→ │  (Retry + Balance) │  │  │
│  │  └────────────┘  └────────────┘  └────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│         │                 │                      │              │
│         ▼                 ▼                      ▼              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Database   │  │   Metrics   │  │      Logger          │  │
│  │   (SQLite)   │  │ (Prometheus)│  │    (Structlog)       │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### **8.2 Project Structure**
```
gift_hunter/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Pydantic settings
│   │   └── schemas.py          # Config validation schemas
│   ├── core/
│   │   ├── __init__.py
│   │   ├── client.py           # Telegram client wrapper
│   │   ├── monitor.py          # Gift monitoring service
│   │   ├── filter.py           # Filtering pipeline
│   │   ├── purchase.py         # Purchase engine
│   │   └── priority.py         # Priority system
│   ├── notifications/
│   │   ├── __init__.py
│   │   ├── telegram.py         # Telegram notifications
│   │   └── webhooks.py         # External webhooks
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLite handler
│   │   ├── models.py           # SQLAlchemy models
│   │   └── migrations/         # Alembic migrations
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── logging.py          # Structlog setup
│   │   ├── metrics.py          # Prometheus metrics
│   │   └── health.py           # Health checks
│   └── i18n/
│       ├── __init__.py
│       └── loader.py           # Translation loader
├── locales/
│   ├── en.yaml
│   ├── ru.yaml
│   └── ar.yaml
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docker/
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   └── docker-compose.yml
├── config.yaml                 # Non-sensitive config
├── .env.example                # Environment template
├── pyproject.toml              # Project metadata
├── uv.lock                     # Dependency lock
└── README.md
```

---

## **9. Dockerfile المحدّث**

```dockerfile
# docker/Dockerfile
# Multi-stage build for security and size optimization

# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.12-slim as runtime

# Security: Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/
COPY locales/ ./locales/

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create data directory with correct permissions
RUN mkdir -p /app/data && chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Expose metrics and health ports
EXPOSE 8080 9090

# Run application
CMD ["python", "-m", "src.main"]
```

### **9.1 docker-compose.yml المحدّث**
```yaml
# docker/docker-compose.yml
services:
  gift-hunter:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: gift-hunter
    restart: unless-stopped
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    
    # Security
    security_opt:
      - no-new-privileges:true
    read_only: true
    
    # Volumes
    volumes:
      - ../data:/app/data:rw
      - ../config.yaml:/app/config.yaml:ro
    tmpfs:
      - /tmp
    
    # Environment
    env_file:
      - ../.env
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    
    # Networking
    ports:
      - "8080:8080"   # Health check
      - "9090:9090"   # Metrics
    
    # Logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
    # Health check override
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

---

## **10. سيناريوهات الاختبار (Test Scenarios)**

### **TS-1: Unit Tests**
```python
# tests/unit/test_filter.py
import pytest
from src.core.filter import GiftFilter
from src.config.schemas import GiftRange

class TestGiftFilter:
    def test_price_range_filter(self):
        """Test filtering by price range."""
        gift_range = GiftRange(min_price=100, max_price=500)
        filter = GiftFilter(gift_range)
        
        assert filter.matches_price(200) == True
        assert filter.matches_price(50) == False
        assert filter.matches_price(600) == False
    
    def test_supply_limit_filter(self):
        """Test filtering by supply limit."""
        gift_range = GiftRange(supply_limit=10000)
        filter = GiftFilter(gift_range)
        
        assert filter.matches_supply(5000) == True
        assert filter.matches_supply(15000) == False
```

### **TS-2: Integration Tests**
```python
# tests/integration/test_purchase_flow.py
import pytest
from unittest.mock import AsyncMock
from src.core.purchase import PurchaseEngine

@pytest.mark.asyncio
async def test_partial_purchase_on_low_balance():
    """Test partial purchase when balance is insufficient."""
    # Given
    mock_client = AsyncMock()
    mock_client.get_balance.return_value = 3000
    engine = PurchaseEngine(mock_client)
    
    # When: Attempting to buy 4 gifts at 1500 each
    result = await engine.purchase(gift_id=123, price=1500, quantity=4, recipient_id=456)
    
    # Then: Should purchase only 2
    assert result.purchased_quantity == 2
    assert result.is_partial == True
    assert mock_client.send_gift.call_count == 2
```

### **TS-3: End-to-End Tests**
| Test ID | الوصف | الخطوات | النتيجة المتوقعة |
|---------|-------|---------|-----------------|
| E2E-1 | اكتشاف هدية جديدة | 1. شغّل البوت 2. انتظر هدية جديدة | البوت يكتشف ويعالج الهدية |
| E2E-2 | الشراء الناجح | 1. هدية متاحة 2. رصيد كافٍ | شراء + إشعار نجاح |
| E2E-3 | الشراء الجزئي | 1. رصيد = 3000⭐ 2. سعر = 1500⭐ 3. كمية = 4 | شراء 2 + إشعار جزئي |
| E2E-4 | إعادة الاتصال | 1. قطع الإنترنت 2. إعادة الاتصال | البوت يعاود العمل تلقائياً |
| E2E-5 | تحديث الإعدادات | 1. تعديل config.yaml 2. Hot reload | التغييرات تُطبق بدون restart |

---

## **11. القيود والافتراضات**

### **Constraints:**
- اتصال إنترنت مستقر ومستمر
- حساب تيليجرام نشط ومُفعّل
- رصيد كافٍ لشراء هدية واحدة على الأقل
- Docker/Python 3.12+ مثبت
- Telegram API rate limits (~30 requests/second)

### **Assumptions:**
- Telegram API متاح ومستقر
- المستخدم لديه معرفة أساسية بـ Docker/CLI
- بيئة Linux/macOS/Windows مع WSL2

---

## **12. خارطة الطريق المستقبلية (Roadmap)**

### **Phase 1: Core Modernization (Q1 2026)**
- [x] Migrate to Pyrogram 2.x official
- [x] Implement pydantic-settings
- [x] Add structured logging
- [x] SQLite database integration
- [x] Secure Docker setup

### **Phase 2: Enhanced Features (Q2 2026)**
- [ ] Web dashboard (FastAPI + React)
- [ ] Webhook notifications (Discord, Slack)
- [ ] Budget management system
- [ ] Gift scheduling
- [ ] Advanced analytics

### **Phase 3: Enterprise Features (Q3 2026)**
- [ ] Multi-account support
- [ ] Kubernetes deployment
- [ ] GraphQL API
- [ ] Mobile companion app
- [ ] AI-powered gift recommendations

---

## **13. المراجع**

- [Telegram API Documentation](https://core.telegram.org/api)
- [Pyrogram Official Documentation](https://docs.pyrogram.org/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [Structlog Documentation](https://www.structlog.org/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [12-Factor App Methodology](https://12factor.net/)

---

**تاريخ الإنشاء:** 2026-01-05  
**آخر تحديث:** 2026-01-06  
**الإصدار:** 2.0  
**المؤلف:** Modernized by Senior Software Architect Review

---

> [!IMPORTANT]
> هذا المستند يمثل الرؤية المستهدفة للمشروع. التنفيذ الفعلي قد يتطلب تعديلات بناءً على:
> - توافر الموارد التطويرية
> - تغييرات في Telegram API
> - متطلبات المستخدمين الجديدة
