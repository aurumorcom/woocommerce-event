# System Architecture Documentation: WordPress Kafka Event Bridge (wordpress-kafka Repo)

Welcome to the architecture documentation for the **WordPress Kafka Event Bridge** (`wordpress-kafka` repository). This repository implements an event-driven integration service connecting WordPress/WooCommerce with internal microservices, utilizing the `python-kafka` Infrastructure SDK.

---

## 1. Directory & File Index

### A. C4 & C3 Structural Models (`c4/`)
- [`c4/01-system-context.md`](c4/01-system-context.md) - C1 System Context ERD.
- [`c4/02-container.md`](c4/02-container.md) - C2 Container ERD.
- [`c4/03-component.md`](c4/03-component.md) - C3 Component ERD.

### B. BPMN Trigger Workflows (`bpmn/`)
- [`bpmn/01-wordpress-webhook-inbound.md`](bpmn/01-wordpress-webhook-inbound.md) - Inbound WordPress webhook event processing and translation.
- [`bpmn/02-product-created-outbound.md`](bpmn/02-product-created-outbound.md) - Outbound product creation workflow via RisingWave HTTP Push Sink.
- [`bpmn/03-product-updated-outbound.md`](bpmn/03-product-updated-outbound.md) - Outbound product modification workflow (`PUT /wc/v3/products/{id}`).
- [`bpmn/04-order-created-inbound.md`](bpmn/04-order-created-inbound.md) - Inbound WooCommerce order creation workflow and topic publishing.
- [`bpmn/05-inventory-synced-outbound.md`](bpmn/05-inventory-synced-outbound.md) - Real-time stock level synchronization workflow.
- [`bpmn/06-site-provisioning.md`](bpmn/06-site-provisioning.md) - Automated Site & Webhook self-provisioning workflow (`POST /wc/v3/webhooks`).

### C. arc42 Documentation & ADRs (`arc42/`)
- [`arc42/01-introduction-and-goals.md`](arc42/01-introduction-and-goals.md) - Requirements, quality goals, and stakeholder expectations.
- [`arc42/02-architecture-constraints.md`](arc42/02-architecture-constraints.md) - Technical, operational, and regulatory constraints.
- [`arc42/03-context-and-scope.md`](arc42/03-context-and-scope.md) - Business context, external interfaces, and domain boundaries.
- [`arc42/04-solution-strategy.md`](arc42/04-solution-strategy.md) - Architectural design decisions and solution patterns.
- [`arc42/05-building-block-view.md`](arc42/05-building-block-view.md) - Static decomposition into subsystems and components.
- [`arc42/06-runtime-view.md`](arc42/06-runtime-view.md) - Runtime behavior and links to BPMN workflows.
- [`arc42/07-deployment-view.md`](arc42/07-deployment-view.md) - Kubernetes deployment topology, ports, and network channels.
- [`arc42/08-cross-cutting-concepts.md`](arc42/08-cross-cutting-concepts.md) - Idempotency, rate-limiting, and error recovery.
- [`arc42/09-architecture-decisions/0001-record-architecture-decisions.md`](arc42/09-architecture-decisions/0001-record-architecture-decisions.md) - Baseline ADR for Asymmetric Integration System Pattern.
- [`arc42/09-architecture-decisions/0002-cloudevents-and-pydantic-avro-schema-derivation.md`](arc42/09-architecture-decisions/0002-cloudevents-and-pydantic-avro-schema-derivation.md) - ADR for Master Product Model, `pydantic-avro` Auto-Registration, and CloudEvents Specification.
- [`arc42/09-architecture-decisions/0004-two-repo-architecture.md`](arc42/09-architecture-decisions/0004-two-repo-architecture.md) - ADR for migrating from a monorepo to a 2-repository architecture (`python-kafka` and `wordpress-kafka`).
- [`arc42/10-quality-requirements.md`](arc42/10-quality-requirements.md) - Quality tree, latency targets, and concrete quality scenarios.
- [`arc42/11-risks-and-technical-debt.md`](arc42/11-risks-and-technical-debt.md) - Architectural risks, mitigation strategies, and technical debt tracking.
- [`arc42/12-glossary.md`](arc42/12-glossary.md) - Domain and technical dictionary.
