---
name: archimate-metamodel
description: Official ArchiMate 3.2 Metamodel Reference Guide encoding valid element types, layers, relationship types, and the relationship-validity matrix for legacy system architecture modeling.
---

# ArchiMate 3.2 Metamodel Specification

This reference skill defines the valid element types, layers, relationship types, and relationship-validity matrix as specified by the Open Group ArchiMate 3.2 standard.

---

## 1. ArchiMate Layers & Element Vocabulary

### 1.1 Motivation Layer
| Element Type | Category | Definition |
| :--- | :--- | :--- |
| `Stakeholder` | Motivation | Role of an individual, team, or organization holding interests in system outcomes. |
| `Driver` | Motivation | External or internal condition that motivates an organization to define goals. |
| `Assessment` | Motivation | Outcome of an analysis of a Driver (e.g. SWOT analysis, gap analysis). |
| `Goal` | Motivation | High-level statement of intent or direction an organization wants to achieve. |
| `Outcome` | Motivation | End result that has been achieved by exercising capabilities or executing plans. |
| `Principle` | Motivation | Qualitative statement of intent that guides system architecture decisions. |
| `Requirement` | Motivation | Statement of need that must be fulfilled by the system or architecture. |
| `Constraint` | Motivation | Hard boundary or restriction imposed on the system (budget, compliance, tech stack). |

### 1.2 Strategy Layer
| Element Type | Category | Definition |
| :--- | :--- | :--- |
| `Resource` | Strategy | Asset or capability owned or controlled by an organization (data, budget, IP). |
| `Capability` | Strategy | Ability that a business possesses or requires to achieve a specific outcome. |
| `CourseOfAction` | Strategy | Approach or plan for configuring resources and capabilities to achieve a Goal. |
| `ValueStream` | Strategy | Sequence of value-adding activities that achieves a result for a customer or stakeholder. |

### 1.3 Business Layer
| Element Type | Category | Definition |
| :--- | :--- | :--- |
| `BusinessActor` | Business | Organizational entity capable of performing business behavior (person, department). |
| `BusinessRole` | Business | Responsibility or set of behaviors assigned to an actor in a business context. |
| `BusinessProcess` | Business | Sequence of business behaviors that produces a specific set of products or services. |
| `BusinessFunction` | Business | Collection of business behavior grouped according to business criteria/skills. |
| `BusinessService` | Business | Explicitly defined business behavior exposed to internal or external customers. |
| `BusinessInterface` | Business | Point of access where a Business Service is made available to the environment. |
| `BusinessEvent` | Business | State change or trigger that initiates or bounds business behavior. |

### 1.4 Application Layer
| Element Type | Category | Definition |
| :--- | :--- | :--- |
| `ApplicationComponent` | Application | Autonomous encapsulation of application functionality (microservice, monolith, DB). |
| `ApplicationFunction` | Application | Automated behavior performed by one or more application components. |
| `ApplicationService` | Application | Automated service exposed by an Application Component via an interface. |
| `ApplicationInterface` | Application | Point of access (REST API endpoint, gRPC service, message queue queue) where a service is exposed. |
| `DataObject` | Application | Structured data elements used and processed by application components (database schema, payload). |

### 1.5 Technology & Infrastructure Layer
| Element Type | Category | Definition |
| :--- | :--- | :--- |
| `Node` | Technology | Computational or physical resource that hosts, manipulates, or executes artifacts. |
| `Device` | Technology | Physical hardware resource upon which software elements execute (server, router, mobile). |
| `SystemSoftware` | Technology | Software environment that manages hardware/execution runtime (OS, Docker, JVM, K8s). |
| `TechnologyService` | Technology | Infrastructure service exposed by a Node or System Software to applications (DNS, DB service). |
| `TechnologyInterface` | Technology | Point of access where a Technology Service is exposed (network port, socket). |
| `Artifact` | Technology | Physical piece of data or executable produced or used in a software system (JAR, container image, SQL script). |

---

## 2. Relationship Vocabulary (11 ArchiMate Relationship Types)

| Relationship Type | Class | Description |
| :--- | :--- | :--- |
| `Composition` | Structural | Source element consists of target element (part-of whole relationship). |
| `Aggregation` | Structural | Source element groups target elements (collective whole relationship). |
| `Assignment` | Structural | Source element is assigned to perform or host behavior of target element. |
| `Realization` | Structural | Source element plays a critical role in bringing target element into reality. |
| `Serving` | Dependency | Source element provides functionality used by target element. |
| `Access` | Dependency | Source behavior element reads, writes, or accesses target Data Object/Artifact. |
| `Influence` | Dependency | Source element affects implementation or achievement of target Goal/Requirement. |
| `Triggering` | Dynamic | Source behavior element initiates or calls target behavior element directly. |
| `Flow` | Dynamic | Source element transfers data or material to target element. |
| `Specialization` | Other | Source element is a specific subtype or specialized instance of target element. |
| `Association` | Other | Unspecified or general relationship connecting two elements. |

---

## 3. Relationship-Validity Matrix (Legal Source -> Target Pairs)

This matrix defines which relationships are legally permitted between layers and elements:

| Source Layer | Relationship | Allowed Target Layer / Elements |
| :--- | :--- | :--- |
| **Motivation** | `Influence` | Goal, Requirement, Constraint, Assessment |
| **Motivation** | `Realization` | Requirement realizes Goal; Constraint realizes Requirement |
| **Strategy** | `Realization` | Resource / Capability realizes Goal / ValueStream |
| **Business** | `Assignment` | BusinessActor assigned to BusinessRole; BusinessRole assigned to BusinessProcess |
| **Business** | `Realization` | BusinessProcess / BusinessFunction realizes BusinessService |
| **Business** | `Serving` | BusinessService serves BusinessRole / BusinessActor |
| **Application** | `Realization` | ApplicationComponent / ApplicationFunction realizes ApplicationService |
| **Application** | `Serving` | ApplicationService serves BusinessProcess / BusinessRole / ApplicationComponent |
| **Application** | `Access` | ApplicationComponent / ApplicationFunction accesses DataObject |
| **Application** | `Triggering / Flow` | ApplicationComponent / ApplicationService triggers or flows data to ApplicationComponent |
| **Technology** | `Realization` | SystemSoftware / Node / Artifact realizes TechnologyService or ApplicationComponent |
| **Technology** | `Assignment` | Node / SystemSoftware assigned to host Artifact / ApplicationComponent |
| **Technology** | `Serving` | TechnologyService serves ApplicationComponent / SystemSoftware |
