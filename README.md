# AI Flight Disruption Recovery Agent

An AI-powered flight disruption recovery assistant that helps passengers understand flight disruptions, explore alternative itineraries, and request rebooking through a controlled, approval-based workflow.

Built using **Python, FastAPI, and Anthropic Claude**, this project demonstrates how agentic AI can support airline post-booking operations.

> **Project status:** In development  
> **Data:** Synthetic airline and passenger data only  
> **Purpose:** Hackathon demonstration and learning project

---

## 1. Problem Statement

Flight disruptions such as cancellations, delays, and missed connections create a frustrating experience for passengers.

Passengers often need to:
- Understand what happened to their flight.
- Check applicable airline policies.
- Find suitable alternative itineraries.
- Understand their available recovery options.
- Confirm a rebooking request.

This project explores how an AI agent can simplify that experience by combining LLM reasoning, tool calling, retrieval-augmented generation (RAG), and human approval.

## 2. Solution Overview

The AI agent acts as a conversational flight disruption recovery assistant.

A passenger describes their disruption, and the agent follows a controlled workflow:

1. Retrieve the passenger's synthetic booking details.
2. Verify the reported flight disruption.
3. Retrieve and explain the applicable airline policy.
4. Offer alternative flight searches when appropriate.
5. Search for suitable itineraries after the passenger accepts the search offer.
6. Present available options and explain the recommendations.
7. Request explicit passenger approval before rebooking.
8. Execute a simulated rebooking after approval.

The agent does not independently make booking decisions or perform actions without the required passenger consent.

## 3. Key Features

- **Conversational AI:** Understands passenger requests and maintains conversation context within a session.
- **Tool Calling:** Uses controlled tools to retrieve bookings, check flight status, search policies, and manage recovery workflows.
- **RAG:** Retrieves relevant airline policy information to support policy-grounded responses.
- **Alternative Flight Search:** Finds and ranks suitable synthetic itineraries.
- **Human-in-the-Loop:** Requires explicit passenger approval before rebooking.
- **Safety Controls:** Validates consent, approval, pending requests, and rebooking eligibility.
- **Evaluation Framework:** Uses deterministic tests and live Claude evaluations to assess agent behavior.
- **Synthetic Airline Services:** Simulates airline operations without connecting to real airline systems.

## 4. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| AI Model | Anthropic Claude |
| LLM Integration | Anthropic API |
| Data Validation | Pydantic v2 |
| Policy Retrieval | BM25 |
| Testing | Pytest, HTTPX |
| API Server | Uvicorn |

## 5. High-Level Architecture

```text
             Passenger
                 |
                 v
           FastAPI Backend
                 |
                 v
          Session Manager
                 |
                 v
            Agent Runner
                 |
                 v
           Claude LLM
                 |
                 v
            Tool Registry
                 |
       +---------+---------+
       |         |         |
       v         v         v
    Booking   Flight     Policy
    Service   Service    Retrieval
       |         |         |
       +---------+---------+
                 |
                 v
        Alternative Search
                 |
                 v
        Approval Management
                 |
                 v
       Simulated Rebooking
```

The application runs as a single Python process. Session state and synthetic service data are maintained in memory for the demonstration.

## 6. Agent Workflow

The agent supports three primary disruption scenarios:

### Flight Cancellation
- Retrieve booking and verify cancellation.
- Retrieve applicable cancellation policy.
- Explain available recovery options.
- Search for alternatives when appropriate.
- Request explicit approval before rebooking.

### Flight Delay
- Retrieve booking and verify delay information.
- Explain the disruption and applicable policy.
- Offer an alternative flight search.
- Search only after the passenger accepts the offer.
- Request separate explicit approval before rebooking.

### Missed Connection
- Retrieve booking and verify the missed connection.
- Retrieve applicable policy.
- Search for eligible onward itineraries.
- Present suitable options.
- Request explicit approval before rebooking.

## 7. Safety and Human Approval

Passenger approval is a critical part of the system.

The application enforces the following principles:

- The agent cannot rebook without explicit passenger approval.
- Search consent and rebooking approval are separate.
- Approval is associated with the pending itinerary and booking.
- Approval is single-use and expires at the end of the granting turn.
- The rebooking service independently validates approval.
- The LLM cannot arbitrarily provide booking identifiers or approval flags to bypass application controls.
- The system does not claim that a refund has been processed.

All booking and rebooking operations are simulated.

## 8. Evaluation Framework

Agent quality is evaluated through two complementary approaches.

### Deterministic Evaluation
Tests application behavior without making live LLM calls.

Examples:
- Correct tool selection.
- Booking retrieval validation.
- Search consent enforcement.
- Rebooking approval enforcement.
- Policy retrieval relevance.
- Protection against prompt injection.
- Correct session handling.

### Live Claude Evaluation
Evaluates the complete conversational workflow using the Claude API.

An LLM-based judge provides additional qualitative feedback. Its assessment is advisory; deterministic checks determine pass or fail.

The evaluation framework targets:

| Metric | Target |
|---|---:|
| Approval compliance | 100% |
| Intent and tool accuracy | ≥90% |
| Gold policy document in top 3 | ≥80% |
| Overall evaluation score | ≥80% |

## 9. Project Scope

### Included
- Synthetic PNR and passenger data.
- Mock flight status service.
- Synthetic airline policy documents.
- Policy retrieval using BM25.
- Agent orchestration and tool calling.
- Alternative itinerary search.
- Passenger consent and approval management.
- Simulated rebooking.
- Deterministic and live LLM evaluations.

### Not Included
- Real airline or GDS integrations.
- Actual ticket issuance or rebooking.
- Real payment or refund processing.
- Production deployment.
- Authentication and authorization infrastructure.
- Cloud infrastructure or CI/CD.
- Real passenger personal information.

## 10. Getting Started

The implementation is currently in progress. Setup instructions will be updated as the application foundation is completed.

### Prerequisites

- Python 3.13
- Anthropic API access
- Git

### Configuration

The Anthropic API key will be supplied through an environment variable.

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

Do not commit API keys or other secrets to the repository.

### Installation and Execution

Installation, dependency management, and application startup commands will be documented once the initial implementation is complete.

## 11. Project Structure

The planned repository structure is:

```text
flight-disruption-agent/
│
├── docs/
│   ├── 01-problem-statement.md
│   ├── 02-requirements.md
│   └── 03-architecture.md
│
├── src/
│   └── flight_disruption_agent/
│       ├── api/
│       ├── agent/
│       ├── tools/
│       ├── services/
│       ├── retrieval/
│       ├── evaluation/
│       └── config/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── evaluation/
│
├── data/
│   ├── bookings/
│   ├── flights/
│   └── policies/
│
├── config/
├── pyproject.toml
├── .gitignore
└── README.md
```

The structure is a planned layout and may evolve during implementation.

## 12. Learning Objectives

This project is also an exploration of practical agentic AI concepts:

- Understanding LLMs and their limitations.
- Building agents with tool calling.
- Designing controlled agent workflows.
- Implementing RAG for domain-specific knowledge.
- Managing conversation and session state.
- Implementing human-in-the-loop approval.
- Evaluating agent reliability and safety.
- Testing adversarial scenarios and prompt injection.

## 13. Disclaimer

This is an experimental hackathon project built exclusively with synthetic data.

It is not connected to real airline reservation systems and must not be used to make actual travel or booking decisions.

---

**Built as an exploration of Agentic AI in airline post-booking and disruption recovery workflows.**
