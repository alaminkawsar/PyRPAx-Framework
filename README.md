# RPA FrameWork For Web
✅ Scalability \
✅ Maintainability\
✅ Logging & Monitoring\
✅ Error Handling\
✅ Retry Mechanism\
✅ Centralized Object Repository\
✅ Config-driven execution\
✅ Multi-bot support\
✅ Secure credential management\
✅ Deployment-ready structure


# High Level Architecture
```
RPA_Framework/
│
├── bots/
│     └── invoice_bot/
│            workflow.py
│
├── core/
│     driver_manager.py
│     base_page.py
│     retry_handler.py
│     logger.py
│     exception_handler.py
│
├── object_repository/
│     invoice_page.yaml
│
├── config/
│     config.yaml
│     environments.yaml
│
├── utils/
│     file_utils.py
│     db_utils.py
│
├── logs/
├── reports/
└── main.py
```

This structure separates:

- Business logic
- Core engine
- UI elements
- Configurations
- Utilities